from sqlalchemy.orm import Session

from app.data.config_registry import CONFIG_ENTRIES, should_encrypt_on_write
from app.models import SystemConfig
from app.services import config_service


def seed_system_configs(db: Session) -> None:
    from app.config import get_settings

    settings = get_settings()
    for e in CONFIG_ENTRIES:
        if e.readonly:
            continue
        exists = db.query(SystemConfig).filter(SystemConfig.key == e.key).first()
        if exists:
            continue
        if hasattr(settings, e.key):
            v = getattr(settings, e.key)
            initial = "" if v is None else str(v)
        else:
            initial = e.default
        config_service.set_value(
            db,
            e.key,
            initial,
            encrypt=should_encrypt_on_write(e.key),
            description=e.description,
        )
    db.commit()
