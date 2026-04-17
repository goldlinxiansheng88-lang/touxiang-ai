"""用户会话 JWT（与 admin 无关）。"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

import jwt

from app.config import get_settings


SESSION_COOKIE = "aurashift_session"
JWT_ALG = "HS256"
JWT_EXPIRE_DAYS = 30


def _secret() -> str:
    s = get_settings()
    raw = (s.jwt_secret or "").strip()
    if raw:
        return raw
    ek = (s.encryption_key or "").strip()
    if ek:
        return hashlib.sha256(ek.encode("utf-8")).hexdigest()
    return "aurashift-dev-only-set-encryption-key-or-jwt-secret"


def encode_session_token(*, user_id: UUID, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=JWT_EXPIRE_DAYS)).timestamp()),
        "typ": "user",
    }
    return jwt.encode(payload, _secret(), algorithm=JWT_ALG)


def decode_session_token(token: str) -> Optional[dict[str, Any]]:
    try:
        return jwt.decode(token, _secret(), algorithms=[JWT_ALG])
    except jwt.PyJWTError:
        return None
