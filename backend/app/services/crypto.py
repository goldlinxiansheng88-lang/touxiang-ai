from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings


def _fernet() -> Fernet:
    from app.database import SessionLocal
    from app.services import config_service

    settings = get_settings()
    db = SessionLocal()
    try:
        key = (config_service.get("encryption_key", default=settings.encryption_key, db=db) or "").strip()
    finally:
        db.close()
    if not key:
        raise RuntimeError("ENCRYPTION_KEY is not set (环境变量或后台只读项)")
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_value(plain: str) -> str:
    return _fernet().encrypt(plain.encode()).decode()


def decrypt_value(token: str) -> str:
    try:
        return _fernet().decrypt(token.encode()).decode()
    except (InvalidToken, RuntimeError, ValueError):
        return ""
