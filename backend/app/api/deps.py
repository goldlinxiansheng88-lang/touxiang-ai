from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.services import config_service

DbSession = Annotated[Session, Depends(get_db)]


def admin_token(
    db: DbSession,
    x_admin_token: Annotated[Optional[str], Header(alias="X-Admin-Token")] = None,
    # EventSource 无法自定义请求头，流式日志接口可用查询参数传同一口令（请勿把链接分享给他人）。
    admin_token_q: Annotated[Optional[str], Query(alias="admin_token")] = None,
) -> None:
    settings = get_settings()
    secret = config_service.get("admin_password", default=settings.admin_password, db=db)
    t = (x_admin_token or admin_token_q or "").strip()
    if not t or t != str(secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
