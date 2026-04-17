import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.data.static_config import SCENES, STYLES
from app.services import config_service
from app.api.auth_endpoints import get_optional_user_id
from app.models import Affiliate, AffiliateClick, Task, User
from app.utils.cookies import get_aff_ref, get_device_id, set_cookies
from app.workers.tasks import process_aura_task

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


@router.post("/tasks")
async def create_task(
    db: DbSession,
    request: Request,
    image: UploadFile = File(...),
    scene: str = Form(...),
    style: str = Form(...),
    ref: str | None = Query(None),
    aff_ref: str | None = Form(None),
):
    settings = get_settings()
    public_base = config_service.get("public_base_url", default=settings.public_base_url, db=db)
    aff = aff_ref or ref or get_aff_ref(request)

    upload_dir = Path(__file__).resolve().parent.parent.parent / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(image.filename or "img.jpg").suffix or ".jpg"
    if ext.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    fname = f"{uuid.uuid4()}{ext}"
    dest = upload_dir / fname
    content = await image.read()
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

    task = Task(
        user_id=user.id,
        input_image_url=public_url,
        scene=scene,
        style=style,
        status="QUEUED",
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    try:
        process_aura_task.delay(str(task.id))
    except Exception as e:
        logger.exception("Celery 入队失败（Redis 未启动或未运行 Worker 时常见）")
        task.status = "FAILED"
        task.error_message = (
            f"任务无法入队：{e!s}"[:2000]
            + "。请确认 Redis 可连，并已启动："
            "celery -A app.workers.celery_app worker -l info"
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "异步队列不可用：请确认 REDIS_URL 可连并在 .env 中配置，且已运行 Celery Worker；"
                "仅启动 API 进程无法处理生成任务。"
            ),
        ) from e

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
        return {"status": task.status, "progress_hint": hint}

    if task.status == "FAILED":
        return {"status": "FAILED", "error_message": task.error_message or "Unknown error"}

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
        "blurred_image_url": task.blurred_image_url,
        "preview_text": preview,
        "full_text": full_text if unlocked else "",
        "highres_url": task.result_image_url if unlocked else None,
    }
