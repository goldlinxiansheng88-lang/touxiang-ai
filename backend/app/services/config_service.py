import os
from typing import Any, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import SystemConfig
from app.services import crypto

_redis_client: Any = None


def _get_redis():
    """配置缓存用 Redis；不可达时必须快速失败，避免拖住整条请求链（如管理口令校验卡满 60s）。"""
    global _redis_client
    if _redis_client is not False:
        try:
            import redis

            from app.config import get_settings

            r = redis.Redis.from_url(
                get_settings().redis_url,
                decode_responses=True,
                socket_connect_timeout=3.0,
                socket_timeout=3.0,
            )
            r.ping()
            _redis_client = r
            return r
        except Exception:
            _redis_client = False
    return None


def invalidate_cache(key: str) -> None:
    r = _get_redis()
    if r:
        r.delete(f"config:{key}")


def get(key: str, default: Any = None, db: Optional[Session] = None) -> Any:
    r = _get_redis()
    if r:
        cached = r.get(f"config:{key}")
        if cached is not None:
            return cached

    close = False
    if db is None:
        db = SessionLocal()
        close = True
    try:
        try:
            row = db.query(SystemConfig).filter(SystemConfig.key == key).one_or_none()
        except SQLAlchemyError:
            try:
                db.rollback()
            except Exception:
                pass
            row = None
        if row is None:
            val = os.environ.get(key.upper(), default)
            return val
        value = row.value
        if row.is_encrypted and value:
            try:
                value = crypto.decrypt_value(value)
            except RuntimeError:
                value = row.value
        if r:
            r.setex(f"config:{key}", 300, value if isinstance(value, str) else str(value))
        return value
    finally:
        if close:
            db.close()


def set_value(
    db: Session,
    key: str,
    value: str,
    *,
    encrypt: bool = True,
    updated_by: Optional[Any] = None,
    description: Optional[str] = None,
) -> None:
    row = db.query(SystemConfig).filter(SystemConfig.key == key).one_or_none()
    use_enc = bool(encrypt and value)
    stored = crypto.encrypt_value(value) if use_enc else value
    if row:
        row.value = stored
        row.is_encrypted = use_enc
        if updated_by:
            row.updated_by = updated_by
        if description is not None:
            row.description = description
    else:
        db.add(
            SystemConfig(
                key=key,
                value=stored,
                is_encrypted=use_enc,
                updated_by=updated_by,
                description=description,
            )
        )
    invalidate_cache(key)
