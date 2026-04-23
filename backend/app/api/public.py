import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.data.static_config import SCENES, STYLES, STYLE_PARAMS
from app.services import config_service
from app.services.aura_prompt_builder import build_generation_prompts
from app.services.storage_s3 import load_s3_config, put_bytes
from app.api.auth_endpoints import get_optional_user_id
from app.models import Affiliate, AffiliateClick, Task, User
from app.utils.cookies import get_aff_ref, get_device_id, set_cookies
from app.workers.tasks import process_aura_task, process_aura_task_inline

from .deps import DbSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["public"])

PROGRESS_HINTS = [
    "Aligning your aura...",
    "Reading your energy...",
    "Channeling your vibe...",
]


@router.get("/config")
def get_public_config():
    return {"scenes": SCENES, "styles": STYLES}


def _resolve_current_user(db: DbSession, request: Request) -> User | None:
    """
    Resolve a user for "My page":
    - If logged in, use session user id
    - Else fallback to device_id cookie (anonymous user record)
    """
    session_uid = get_optional_user_id(request)
    if session_uid:
        u = db.query(User).filter(User.id == session_uid).first()
        if u:
            return u
    device = get_device_id(request)
    if device:
        return db.query(User).filter(User.device_id == device).first()
    return None


@router.get("/me")
def me_public(db: DbSession, request: Request):
    """Current user's public profile (for personal homepage)."""
    u = _resolve_current_user(db, request)
    if not u:
        return {"authenticated": False, "user": None}
    return {
        "authenticated": bool(u.email),
        "user": {
            "id": str(u.id),
            "device_id": u.device_id,
            "email": u.email,
            "display_name": u.display_name,
            "is_vip": bool(u.is_vip),
            "vip_expires_at": u.vip_expires_at.isoformat() if u.vip_expires_at else None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        },
    }


@router.get("/me/tasks")
def my_tasks(db: DbSession, request: Request, page: int = 1, page_size: int = 20):
    """List recent tasks for current user/device."""
    u = _resolve_current_user(db, request)
    if not u:
        return {"total": 0, "page": page, "items": []}
    q = db.query(Task).filter(Task.user_id == u.id)
    total = q.count()
    rows = (
        q.order_by(Task.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "items": [
            {
                "id": str(t.id),
                "status": t.status,
                "scene": t.scene,
                "style": t.style,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in rows
        ],
    }


def _mask_connection_url(url: str) -> str:
    """仅用于后台预览：去掉账号密码，避免未登录时完全空白、又不在响应里泄露密钥。"""
    if not url or not url.strip():
        return ""
    try:
        from urllib.parse import urlparse, urlunparse

        u = urlparse(url.strip())
        host = u.hostname or ""
        port = f":{u.port}" if u.port else ""
        netloc = f"{host}{port}" if host else ""
        # 丢弃 username / password
        return urlunparse((u.scheme, netloc, u.path or "", u.params, u.query, u.fragment))
    except Exception:
        return "（已配置，详情见 .env）"


@router.get("/meta/infrastructure-preview")
def infrastructure_preview():
    """只读基础设施的脱敏预览，无需管理口令，便于未授权时也能看到「连的是哪」。"""
    s = get_settings()
    ek = (s.encryption_key or "").strip()
    return {
        "database_url": _mask_connection_url(s.database_url),
        "redis_url": _mask_connection_url(s.redis_url),
        "encryption_key": "（已配置）" if ek else "（未配置 ENCRYPTION_KEY）",
    }


@router.get("/meta/config-registry")
def get_config_registry_meta():
    """后台表单结构（不含敏感值），未登录也可拉取，用于先渲染完整配置页。"""
    from app.data.config_registry import CONFIG_ENTRIES, GROUP_HINTS, GROUP_ORDER, VALUE_KIND_LABELS

    return {
        "groups": [{"id": g, "label": g, "hint": GROUP_HINTS.get(g, "")} for g in GROUP_ORDER],
        "items": [
            {
                "key": e.key,
                "label": e.label,
                "group": e.group,
                "description": e.description,
                "readonly": e.readonly,
                "is_secret": e.is_secret,
                "value_kind": VALUE_KIND_LABELS.get(e.key, "文本"),
                "required": e.required,
            }
            for e in CONFIG_ENTRIES
        ],
    }


_ASPECT_RATIOS = frozenset({"auto", "1:1", "3:4", "4:3", "16:9", "9:16", "2:3", "3:2"})


@router.post("/tasks")
async def create_task(
    db: DbSession,
    request: Request,
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    scene: str = Form(...),
    style: str = Form(...),
    aspect_ratio: str | None = Form(None),
    ref: str | None = Query(None),
    aff_ref: str | None = Form(None),
):
    settings = get_settings()
    public_base = config_service.get("public_base_url", default=settings.public_base_url, db=db)
    aff = aff_ref or ref or get_aff_ref(request)
    ar = (aspect_ratio or "auto").strip()
    if ar not in _ASPECT_RATIOS:
        ar = "auto"

    style = (style or "").strip()
    scene = (scene or "").strip()
    if style not in STYLE_PARAMS:
        raise HTTPException(status_code=400, detail=f"Unknown style: {style}")

    ext = Path(image.filename or "img.jpg").suffix or ".jpg"
    if ext.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    fname = f"{uuid.uuid4()}{ext}"
    content = await image.read()
    # Prefer S3/R2 public URL for fal to fetch. Fallback to local uploads if not configured.
    s3cfg = load_s3_config(db=db)
    if s3cfg:
        public_url = put_bytes(
            cfg=s3cfg,
            key=f"uploads/input/{fname}",
            data=content,
            content_type=image.content_type or None,
            cache_control="public, max-age=31536000, immutable",
        )
    else:
        upload_dir = Path(__file__).resolve().parent.parent.parent / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        dest = upload_dir / fname
        dest.write_bytes(content)
        public_url = f"{str(public_base).rstrip('/')}/static/uploads/{fname}"

    session_uid = get_optional_user_id(request)
    user = None
    if session_uid:
        user = db.query(User).filter(User.id == session_uid).first()
    device = get_device_id(request) or str(uuid.uuid4())
    if not user:
        user = db.query(User).filter(User.device_id == device).first()
    if not user:
        user = User(device_id=device, ip_address=request.client.host if request.client else None)
        db.add(user)
        db.flush()

    if aff:
        aff_row = db.query(Affiliate).filter(Affiliate.code == aff).first()
        if aff_row:
            db.add(
                AffiliateClick(
                    affiliate_id=aff_row.id,
                    user_id=user.id,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                )
            )

    prompts = build_generation_prompts(scene=scene, style=style, aspect_ratio=ar)

    task = Task(
        user_id=user.id,
        input_image_url=public_url,
        scene=scene,
        style=style,
        aspect_ratio=ar,
        status="QUEUED",
        result_json={
            "generation": {
                "positive_prompt": prompts.positive,
                "negative_prompt": prompts.negative,
                "parts": prompts.parts,
            }
        },
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    try:
        process_aura_task.delay(str(task.id))
    except Exception as e:
        logger.exception("Celery 入队失败（Redis 未启动或未运行 Worker 时常见）")
        # Fallback: run in-process to avoid hard failure on small deployments.
        task.status = "QUEUED"
        task.error_message = (
            f"队列不可用，已改为 API 进程处理（可能较慢）：{e!s}"[:2000]
        )
        db.commit()
        background_tasks.add_task(process_aura_task_inline, str(task.id))

    resp = JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"task_id": str(task.id), "status": task.status},
    )
    set_cookies(resp, device_id=device, aff_ref=aff if aff else None)
    return resp


@router.get("/tasks/{task_id}")
def get_task_status(db: DbSession, request: Request, task_id: str):
    try:
        tid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")
    task = db.query(Task).filter(Task.id == tid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status in ("QUEUED", "PROCESSING"):
        hint = PROGRESS_HINTS[hash(str(task.id)) % len(PROGRESS_HINTS)]
        return {
            "status": task.status,
            "progress_hint": hint,
            "aspect_ratio": task.aspect_ratio or "auto",
        }

    if task.status == "FAILED":
        return {
            "status": "FAILED",
            "error_message": task.error_message or "Unknown error",
            "aspect_ratio": task.aspect_ratio or "auto",
        }

    def _vip_active(u) -> bool:
        return bool(u and u.is_vip)

    user = task.user
    is_vip = _vip_active(user)

    preview = ""
    full_text = ""
    if task.result_json:
        preview = str(task.result_json.get("preview") or task.result_json.get("vibe") or "")[:200]
        full_text = str(task.result_json.get("full") or task.result_json.get("vibe") or "")

    unlocked = task.is_paid or is_vip
    return {
        "status": task.status,
        "is_paid": task.is_paid,
        "aspect_ratio": task.aspect_ratio or "auto",
        "blurred_image_url": task.blurred_image_url,
        "preview_text": preview,
        "full_text": full_text if unlocked else "",
        "highres_url": task.result_image_url if unlocked else None,
    }
