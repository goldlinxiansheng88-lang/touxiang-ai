import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Affiliate, Order, PayoutRequest, SystemConfig, Task, User
from app.services.payment_finalize import finalize_order_paid
from app.schemas.admin import ConfigBatchPatch, ConnectionTestBody, CreateAffiliateBody, PayoutActionBody
from app.config import clear_settings_cache, get_settings
from app.data.config_registry import CONFIG_ENTRIES, GROUP_HINTS, GROUP_ORDER, entry_by_key, should_encrypt_on_write
from app.services import config_service
from app.services.connection_tests import run_connection_test, TESTABLE_KEYS
from app.services.env_sync import CONFIG_TO_ENV, backend_dotenv_path, sync_keys_to_dotenv

from .deps import DbSession, admin_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(admin_token)])


def _sync_keys_to_dotenv_or_raise(updates: dict[str, str]) -> None:
    try:
        sync_keys_to_dotenv(updates)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"无法写入 {backend_dotenv_path()}：{e}。请检查路径、权限或磁盘空间。",
        ) from e


def _read_runtime_log_tail(path: Path, *, max_lines: int, max_bytes: int = 2_097_152) -> list[str]:
    """读取文本文件尾部若干行（大文件只读末尾 max_bytes 字节）。"""
    try:
        size = path.stat().st_size
    except OSError:
        return []
    with path.open("rb") as f:
        if size <= max_bytes:
            raw = f.read()
        else:
            f.seek(-min(max_bytes, size), 2)
            raw = f.read()
    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()
    if len(lines) > max_lines:
        lines = lines[-max_lines:]
    return lines


def _resolve_runtime_log_path() -> tuple[Path | None, str | None]:
    """返回 (可读文件路径, 错误说明)。路径为 None 时 hint 给前端展示。"""
    raw = (get_settings().runtime_log_file or "").strip()
    if not raw:
        return None, (
            "未配置日志文件：在 backend/.env 中设置 RUNTIME_LOG_FILE=日志路径，并将进程输出重定向到该文件"
            "（例如 uvicorn ... 2>&1 | tee logs/api.log）。"
        )
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = (Path(__file__).resolve().parent.parent.parent / path).resolve()
    else:
        path = path.resolve()
    if not path.is_file():
        return None, f"文件不存在或不可读：{path}"
    return path, None


@router.get("/runtime-logs")
def runtime_logs(tail_lines: int = Query(800, ge=1, le=20_000)):
    """返回可选的运行日志文件尾部（需在服务器配置 runtime_log_file / RUNTIME_LOG_FILE）。"""
    path, err = _resolve_runtime_log_path()
    if not path:
        return {"lines": [], "path": None, "hint": err}
    lines = _read_runtime_log_tail(path, max_lines=tail_lines)
    return {"lines": lines, "path": str(path), "hint": None}


@router.get("/runtime-logs/stream")
async def runtime_logs_stream(request: Request):
    """SSE：先推送当前尾部，再按文件追加近乎实时推送（约 0.45s 轮询一次新内容）。"""

    async def event_gen():
        path, err = _resolve_runtime_log_path()
        if not path or err:
            yield f"data: {json.dumps({'type': 'error', 'hint': err or '无法解析日志路径'}, ensure_ascii=False)}\n\n"
            return
        init_lines = _read_runtime_log_tail(path, max_lines=800)
        yield f"data: {json.dumps({'type': 'init', 'path': str(path), 'lines': init_lines}, ensure_ascii=False)}\n\n"
        try:
            offset = path.stat().st_size
        except OSError:
            offset = 0
        carry = ""
        while True:
            if await request.is_disconnected():
                break
            await asyncio.sleep(0.45)
            try:
                size = path.stat().st_size
            except OSError:
                continue
            if size < offset:
                offset = 0
                carry = ""
                yield f"data: {json.dumps({'type': 'reset'}, ensure_ascii=False)}\n\n"
                continue
            if size <= offset:
                continue
            try:
                with path.open("rb") as f:
                    f.seek(offset)
                    chunk = f.read()
            except OSError:
                continue
            offset = size
            text = carry + chunk.decode("utf-8", errors="replace")
            parts = text.split("\n")
            carry = parts.pop() if parts else ""
            for line in parts:
                yield f"data: {json.dumps({'type': 'append', 'line': line}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/dashboard")
def dashboard(db: DbSession):
    today = datetime.now(timezone.utc).date()
    start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)

    tasks_today = db.query(func.count(Task.id)).filter(Task.created_at >= start).scalar() or 0
    queued = db.query(func.count(Task.id)).filter(Task.status == "QUEUED").scalar() or 0
    completed = db.query(func.count(Task.id)).filter(Task.status == "COMPLETED").scalar() or 0
    failed = db.query(func.count(Task.id)).filter(Task.status == "FAILED").scalar() or 0
    total_done = completed + failed
    success_rate = (completed / total_done) if total_done else 0.0

    revenue = (
        db.query(func.coalesce(func.sum(Order.amount), 0))
        .filter(Order.status == "PAID", Order.created_at >= start)
        .scalar()
    )
    revenue = float(revenue or 0)

    return {
        "visitors_today": tasks_today,
        "queued_tasks": int(queued),
        "success_rate": round(success_rate, 4),
        "revenue_today_usd": revenue,
        "compute_cost_usd": 0.0,
    }


@router.get("/users")
def list_users(
    db: DbSession,
    page: int = 1,
    page_size: int = 20,
):
    q = db.query(User)
    total = q.count()
    rows = (
        q.order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "items": [
            {
                "id": str(u.id),
                "device_id": u.device_id,
                "ip_address": str(u.ip_address) if u.ip_address is not None else None,
                "is_vip": u.is_vip,
                "vip_expires_at": u.vip_expires_at.isoformat() if u.vip_expires_at else None,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in rows
        ],
    }


@router.get("/orders")
def list_orders(
    db: DbSession,
    page: int = 1,
    page_size: int = 20,
    status_filter: str | None = Query(None, alias="status"),
):
    q = db.query(Order)
    if status_filter:
        q = q.filter(Order.status == status_filter)
    total = q.count()
    rows = (
        q.order_by(Order.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "items": [
            {
                "id": str(o.id),
                "task_id": str(o.task_id),
                "user_id": str(o.user_id),
                "amount": float(o.amount),
                "currency": o.currency,
                "status": o.status,
                "affiliate_id": str(o.affiliate_id) if o.affiliate_id else None,
                "commission_earned": float(o.commission_earned) if o.commission_earned is not None else None,
                "created_at": o.created_at.isoformat() if o.created_at else None,
                "paid_at": o.paid_at.isoformat() if o.paid_at else None,
                "payment_channel": o.payment_channel,
            }
            for o in rows
        ],
    }


@router.post("/orders/{order_id}/mark-paid")
def mark_order_paid_manual(db: DbSession, order_id: str):
    """链上 USDT 等需人工核对到账后，在此将订单标为已付。"""
    try:
        oid = uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order_id")
    order = db.query(Order).filter(Order.id == oid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == "PAID":
        return {"ok": True, "already_paid": True}
    if (order.payment_channel or "") != "usdt":
        raise HTTPException(
            status_code=400,
            detail="Only USDT (pending) orders can be confirmed this way",
        )
    finalize_order_paid(db, order)
    db.commit()
    return {"ok": True, "already_paid": False}


@router.get("/tasks")
def list_tasks(
    db: DbSession,
    status_filter: str | None = Query(None, alias="status"),
    user_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    q = db.query(Task)
    if status_filter:
        q = q.filter(Task.status == status_filter)
    if user_id:
        q = q.filter(Task.user_id == uuid.UUID(user_id))
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
                "user_id": str(t.user_id),
                "scene": t.scene,
                "style": t.style,
                "status": t.status,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in rows
        ],
    }


@router.post("/tasks/{task_id}/retry")
def retry_task(db: DbSession, task_id: str):
    try:
        tid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task id")
    task = db.query(Task).filter(Task.id == tid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Not found")
    if task.status != "FAILED":
        raise HTTPException(status_code=400, detail="Only failed tasks can be retried")
    task.status = "QUEUED"
    task.error_message = None
    db.commit()
    from app.workers.tasks import process_aura_task

    process_aura_task.delay(str(task.id))
    return {"ok": True}


@router.get("/affiliates")
def list_affiliates(db: DbSession):
    rows = db.query(Affiliate).order_by(Affiliate.created_at.desc()).all()
    return {
        "items": [
            {
                "id": str(a.id),
                "code": a.code,
                "name": a.name,
                "commission_rate": a.commission_rate,
                "wallet_balance": float(a.wallet_balance or 0),
                "total_earned": float(a.total_earned or 0),
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in rows
        ]
    }


@router.post("/affiliates")
def create_affiliate(db: DbSession, body: CreateAffiliateBody):
    import secrets
    import string

    code = (body.code or "").strip().upper()
    if not code:
        alphabet = string.ascii_uppercase + string.digits
        code = "".join(secrets.choice(alphabet) for _ in range(8))
    exists = db.query(Affiliate).filter(Affiliate.code == code).first()
    if exists:
        raise HTTPException(status_code=409, detail="Code already exists")
    aff = Affiliate(code=code, name=body.name, commission_rate=body.commission_rate)
    db.add(aff)
    db.commit()
    db.refresh(aff)
    return {
        "id": str(aff.id),
        "code": aff.code,
        "link": f"?ref={aff.code}",
    }


@router.get("/payouts")
def list_payouts(db: DbSession):
    rows = db.query(PayoutRequest).order_by(PayoutRequest.created_at.desc()).all()
    return {
        "items": [
            {
                "id": str(p.id),
                "affiliate_id": str(p.affiliate_id),
                "amount": float(p.amount),
                "status": p.status,
                "payment_method": p.payment_method,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in rows
        ]
    }


@router.patch("/payouts/{payout_id}")
def update_payout(db: DbSession, payout_id: str, body: PayoutActionBody):
    try:
        pid = uuid.UUID(payout_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid id")
    p = db.query(PayoutRequest).filter(PayoutRequest.id == pid).first()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    p.status = body.status
    if body.status == "COMPLETED":
        p.processed_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}


@router.get("/configs")
def list_configs(db: DbSession):
    from app.config import get_settings

    settings = get_settings()
    try:
        all_cfgs = db.query(SystemConfig).order_by(SystemConfig.key.asc()).all()
    except SQLAlchemyError:
        try:
            db.rollback()
        except Exception:
            pass
        all_cfgs = []
    rows_by_key = {r.key: r for r in all_cfgs}
    out = []
    for e in CONFIG_ENTRIES:
        if e.readonly:
            raw = getattr(settings, e.key, None)
            if raw is None:
                raw = e.default
            raw_s = "" if raw is None else str(raw)
            if e.is_secret and raw_s:
                display = "••••••••"
            else:
                display = raw_s
            out.append(
                {
                    "key": e.key,
                    "label": e.label,
                    "group": e.group,
                    "value": display,
                    "value_type": "string",
                    "description": e.description,
                    "is_encrypted": e.is_secret,
                    "readonly": True,
                    "source": "env",
                }
            )
            continue

        row = rows_by_key.get(e.key)
        if row:
            display = row.value if not row.is_encrypted else "••••••••"
            desc = row.description or e.description
            is_enc = row.is_encrypted
        else:
            raw = getattr(settings, e.key, None)
            if raw is None:
                raw = e.default
            raw_s = "" if raw is None else str(raw)
            if e.is_secret and raw_s:
                display = "••••••••"
            else:
                display = raw_s
            desc = e.description
            is_enc = e.is_secret and bool(raw_s)

        out.append(
            {
                "key": e.key,
                "label": e.label,
                "group": e.group,
                "value": display,
                "value_type": row.value_type if row else "string",
                "description": desc,
                "is_encrypted": is_enc,
                "readonly": False,
                "source": "database" if row else "env_default",
            }
        )

    shown = {e.key for e in CONFIG_ENTRIES}
    extra: list[dict] = []
    for r in all_cfgs:
        if r.key in shown:
            continue
        display = r.value if not r.is_encrypted else "••••••••"
        extra.append(
            {
                "key": r.key,
                "label": r.key,
                "group": "其它",
                "value": display,
                "value_type": r.value_type,
                "description": r.description,
                "is_encrypted": r.is_encrypted,
                "readonly": False,
                "source": "database",
            }
        )
    out.extend(extra)

    groups_out = [{"id": g, "label": g, "hint": GROUP_HINTS.get(g, "")} for g in GROUP_ORDER]
    if extra:
        groups_out.append({"id": "其它", "label": "其它", "hint": "注册表中未列出的历史键，可继续编辑。"})

    return {
        "items": out,
        "groups": groups_out,
    }


@router.post("/configs/test-connection")
def test_config_connection(db: DbSession, body: ConnectionTestBody):
    """对单个配置项做连通性检测（数据库 / Redis / HTTP / 云 API 等）。"""
    if body.key not in TESTABLE_KEYS:
        raise HTTPException(status_code=400, detail="此项暂不支持连通性检测")
    try:
        ok, message = run_connection_test(body.key, body.value, body.related, db)
        return {"ok": ok, "message": message}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def _collect_infra_dotenv_updates(body: ConfigBatchPatch) -> dict[str, str]:
    """从本次保存请求中提取要写入 .env 的基础设施项（跳过空值与脱敏占位）。"""
    out: dict[str, str] = {}
    for item in body.items:
        if item.key not in CONFIG_TO_ENV:
            continue
        val = str(item.value or "").strip()
        if not val or "••" in val:
            continue
        if item.key == "encryption_key" and not val:
            continue
        if item.key in ("database_url", "redis_url") and not val:
            continue
        out[item.key] = val
    return out


def _work_db_after_infra_sync(db: Session, body: ConfigBatchPatch) -> Session:
    """若本次保存改了 DATABASE_URL 等：先写入 .env 并重建引擎；若改了库连接串则换用新 Session。

    否则会出现：右侧「连接」用新串成功，但此处仍用请求开头创建的 Session 连旧库，commit 失败并误走 env-only 降级。
    """
    infra_updates = _collect_infra_dotenv_updates(body)
    if not infra_updates:
        return db
    _sync_keys_to_dotenv_or_raise(infra_updates)
    clear_settings_cache()
    from app.database import SessionLocal, get_engine

    if "database_url" in infra_updates:
        db.close()
        get_engine()
        return SessionLocal()
    get_engine()
    return db


def _preflight_infra_connectivity_or_raise(body: ConfigBatchPatch, db: DbSession) -> None:
    """保存前对本次请求中的 database_url / redis_url / encryption_key 先检测；不通过则 400，不写入。"""
    check = frozenset({"database_url", "redis_url", "encryption_key"})
    labels = {
        "database_url": "PostgreSQL",
        "redis_url": "Redis",
        "encryption_key": "Fernet 加密主密钥",
    }
    errs: list[str] = []
    for item in body.items:
        if item.key not in check:
            continue
        if item.key == "encryption_key" and not (item.value or "").strip():
            continue
        if item.key in ("database_url", "redis_url") and not str(item.value or "").strip():
            errs.append(f"{labels[item.key]}：未填写连接串。")
            continue
        ok, msg = run_connection_test(item.key, item.value, None, db)
        if not ok:
            errs.append(f"{labels.get(item.key, item.key)}：{msg}")
    if errs:
        raise HTTPException(
            status_code=400,
            detail="保存前检测未通过，请先修正或点该项右侧「连接」验证后再保存。\n" + "\n".join(errs),
        )


def _patch_configs_env_only(body: ConfigBatchPatch, db_error: str | None = None) -> dict:
    """PostgreSQL 不可达时：仅将 database_url / redis_url / encryption_key 写入 backend/.env。"""
    allowed = frozenset(CONFIG_TO_ENV.keys())
    env_updates: dict[str, str] = {}
    deferred: list[str] = []
    for item in body.items:
        ent = entry_by_key(item.key)
        if ent and ent.readonly:
            raise HTTPException(status_code=400, detail=f"配置项 {item.key} 为只读，请在 .env 中修改并重启服务。")
        if item.key not in allowed:
            deferred.append(item.key)
            continue
        if item.key == "encryption_key" and not (item.value or "").strip():
            continue
        if item.key in ("database_url", "redis_url") and not str(item.value or "").strip():
            raise HTTPException(status_code=400, detail=f"{item.key} 不能为空")
        env_updates[item.key] = item.value
    if not env_updates:
        raise HTTPException(
            status_code=400,
            detail=(
                "数据库尚未连通：当前仅能保存 PostgreSQL、Redis、Fernet 主密钥并同步到 backend/.env。"
                + (" 以下项需数据库恢复后再保存：" + ", ".join(deferred) if deferred else " 请至少修改并保存上述三项之一。")
            ),
        )
    _sync_keys_to_dotenv_or_raise(env_updates)
    clear_settings_cache()
    # 写入 .env 后立刻按新 DATABASE_URL 重建引擎并试连；无需仅为换库而重启本 API 进程
    reconnect_ok = False
    reconnect_detail: str | None = None
    try:
        from app.database import get_engine

        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        reconnect_ok = True
    except Exception as e:
        reconnect_detail = str(e).replace("\n", " ").strip()[:500]
        logger.warning("写入 .env 后仍无法用新连接串连上 PostgreSQL：%s", reconnect_detail)

    if reconnect_ok:
        hint = (
            "已用新连接串写入 backend/.env，并已在本进程内重建数据库连接池且测试连接成功。"
            "请再点击一次「保存更改」，即可把本次配置写入数据库。"
        )
    else:
        hint = (
            "本次请求仍无法用数据库（旧连接失败），已将基础设施写入 backend/.env 并刷新了内存配置。"
            "若连接串正确，请检查网络、密码编码与 Supabase 状态；也可打开 /health/db 查看详情。"
        )
        if reconnect_detail:
            hint += f" 尝试新连接时：{reconnect_detail}"
    if db_error:
        hint += " 写入前旧连接报错：" + db_error.replace("\n", " ").strip()[:400]
    if deferred:
        hint += " 暂未写入（需 PostgreSQL 可用后重试保存）：" + ", ".join(deferred)
    return {
        "ok": True,
        "env_synced": True,
        "hint": hint,
        "db_unavailable": not reconnect_ok,
        "pool_reconnected": reconnect_ok,
        "deferred_keys": deferred,
    }


@router.patch("/configs")
def patch_configs(db: DbSession, body: ConfigBatchPatch):
    _preflight_infra_connectivity_or_raise(body, db)
    work_db = _work_db_after_infra_sync(db, body)
    env_updates: dict[str, str] = {}
    try:
        for item in body.items:
            ent = entry_by_key(item.key)
            if ent and ent.readonly:
                raise HTTPException(status_code=400, detail=f"配置项 {item.key} 为只读，请在 .env 中修改并重启服务。")
            row = work_db.query(SystemConfig).filter(SystemConfig.key == item.key).first()
            if item.value == "" and row and row.is_encrypted:
                continue
            encrypt = should_encrypt_on_write(item.key)
            if row and item.value_type:
                row.value_type = item.value_type
            desc_new = ent.description if ent and not row else None
            try:
                config_service.set_value(work_db, item.key, item.value, encrypt=encrypt, description=desc_new)
            except RuntimeError as e:
                work_db.rollback()
                if "ENCRYPTION_KEY" in str(e):
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "无法保存：缺少有效的 ENCRYPTION_KEY（Fernet）。请先在 backend/.env 设置 ENCRYPTION_KEY，"
                            "或在后台填写「Fernet 加密主密钥」并保存；保存敏感项前必须先有可用的加密主密钥。"
                        ),
                    ) from e
                raise
            except ValueError as e:
                work_db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "无法加密保存：ENCRYPTION_KEY 须为有效的 Fernet 密钥（32 字节 URL-safe base64），"
                        f"或所填内容格式不被接受。详情：{e}"
                    ),
                ) from e
            if item.key in CONFIG_TO_ENV:
                env_updates[item.key] = item.value
        work_db.commit()
    except IntegrityError:
        try:
            work_db.rollback()
        except Exception:
            pass
        raise
    except SQLAlchemyError as e:
        try:
            work_db.rollback()
        except Exception:
            pass
        return _patch_configs_env_only(body, db_error=str(e))
    finally:
        if work_db is not db:
            try:
                work_db.close()
            except Exception:
                pass
    if env_updates:
        _sync_keys_to_dotenv_or_raise(env_updates)
    clear_settings_cache()
    out: dict = {"ok": True}
    if env_updates:
        out["env_synced"] = True
        out["hint"] = (
            "已同步到 backend/.env；本进程已重新加载配置并重建数据库连接池，一般无需仅为换库而重启 API（独立 Celery 等进程除外）。"
        )
    return out
