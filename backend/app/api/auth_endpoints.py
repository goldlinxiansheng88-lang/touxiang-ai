"""用户邮箱登录与 Google / Microsoft OAuth。"""

from __future__ import annotations

import re
import secrets
from typing import Optional
from urllib.parse import urlencode, urlparse
from uuid import UUID, uuid4

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.schemas.user_auth import EmailLoginBody, EmailRegisterBody
from app.services.auth_passwords import hash_password, verify_password
from app.services.auth_tokens import SESSION_COOKIE, decode_session_token, encode_session_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
OAUTH_STATE_COOKIE = "oauth_state"
OAUTH_STATE_MAX_AGE = 600


def get_optional_user_id(request: Request) -> Optional[UUID]:
    raw = request.cookies.get(SESSION_COOKIE)
    if not raw:
        return None
    payload = decode_session_token(raw)
    if not payload or payload.get("typ") != "user":
        return None
    try:
        return UUID(str(payload["sub"]))
    except (KeyError, ValueError):
        return None


def _norm_email(s: str) -> str:
    return (s or "").strip().lower()


def _validate_email(email: str) -> str:
    e = _norm_email(email)
    if not e or not EMAIL_RE.match(e):
        raise HTTPException(status_code=400, detail="邮箱格式无效")
    return e


def _oauth_redirect_base() -> str:
    return get_settings().public_base_url.rstrip("/")


def _frontend_base() -> str:
    return get_settings().frontend_url.rstrip("/")


def _cookie_same_site_policy() -> tuple[str, bool]:
    """
    When the SPA is hosted on a different site than the API, browsers require
    SameSite=None + Secure for cookies to be included in cross-site XHR/fetch
    (axios withCredentials=true).
    """
    s = get_settings()
    fe = urlparse((s.frontend_url or "").strip())
    api = urlparse((s.public_base_url or "").strip())
    if fe.scheme == "https" and api.scheme == "https" and fe.netloc and api.netloc and fe.netloc != api.netloc:
        return "none", True
    return "lax", False


def _set_session_cookie(response: Response, user_id: UUID, email: str) -> None:
    token = encode_session_token(user_id=user_id, email=email)
    same_site, secure = _cookie_same_site_policy()
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=30 * 24 * 60 * 60,
        httponly=True,
        samesite=same_site,
        secure=secure,
        path="/",
    )


@router.post("/email/register")
def register_email(body: EmailRegisterBody, db: Session = Depends(get_db)):
    email = _validate_email(body.email)
    exists = db.query(User).filter(User.email == email).first()
    if exists:
        raise HTTPException(status_code=409, detail="该邮箱已注册")
    dev = f"acct:{uuid4()}"
    u = User(
        device_id=dev[:255],
        email=email,
        password_hash=hash_password(body.password),
        display_name=email.split("@")[0],
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    resp = JSONResponse(content={"ok": True, "user_id": str(u.id)})
    _set_session_cookie(resp, u.id, email)
    return resp


@router.post("/email/login")
def login_email(body: EmailLoginBody, db: Session = Depends(get_db)):
    email = _validate_email(body.email)
    u = db.query(User).filter(User.email == email).first()
    if not u or not u.password_hash:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    if not verify_password(body.password, u.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    resp = JSONResponse(content={"ok": True, "user_id": str(u.id)})
    _set_session_cookie(resp, u.id, email)
    return resp


@router.post("/logout")
def logout():
    resp = JSONResponse(content={"ok": True})
    same_site, secure = _cookie_same_site_policy()
    resp.delete_cookie(SESSION_COOKIE, path="/", samesite=same_site, secure=secure)
    return resp


@router.get("/me")
def me(request: Request, db: Session = Depends(get_db)):
    uid = get_optional_user_id(request)
    if not uid:
        return {"authenticated": False}
    u = db.query(User).filter(User.id == uid).first()
    if not u:
        return {"authenticated": False}
    return {
        "authenticated": True,
        "user_id": str(u.id),
        "email": u.email,
        "display_name": u.display_name or u.email,
    }


# —— Google OAuth ——


@router.get("/oauth/google/start")
def oauth_google_start(request: Request):
    cid = (get_settings().google_oauth_client_id or "").strip()
    if not cid:
        raise HTTPException(
            status_code=503,
            detail="未配置 GOOGLE_OAUTH_CLIENT_ID：请在 backend/.env 填写并在 Google Cloud Console 登记回调地址。",
        )
    state = secrets.token_urlsafe(24)
    redirect_uri = f"{_oauth_redirect_base()}/api/auth/oauth/google/callback"
    q = urlencode(
        {
            "client_id": cid,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
        }
    )
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{q}"
    resp = RedirectResponse(url=url, status_code=302)
    same_site, secure = _cookie_same_site_policy()
    resp.set_cookie(
        OAUTH_STATE_COOKIE,
        state,
        max_age=OAUTH_STATE_MAX_AGE,
        httponly=True,
        samesite=same_site,
        secure=secure,
        path="/",
    )
    return resp


@router.get("/oauth/google/callback")
async def oauth_google_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if error:
        return RedirectResponse(url=f"{_frontend_base()}/?auth_error={error}", status_code=302)
    expected = request.cookies.get(OAUTH_STATE_COOKIE)
    if not state or not expected or state != expected:
        return RedirectResponse(url=f"{_frontend_base()}/?auth_error=state", status_code=302)
    cid = (get_settings().google_oauth_client_id or "").strip()
    csec = (get_settings().google_oauth_client_secret or "").strip()
    if not code or not cid or not csec:
        return RedirectResponse(url=f"{_frontend_base()}/?auth_error=missing", status_code=302)
    redirect_uri = f"{_oauth_redirect_base()}/api/auth/oauth/google/callback"
    async with httpx.AsyncClient(timeout=30.0) as client:
        tr = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": cid,
                "client_secret": csec,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if tr.status_code != 200:
        return RedirectResponse(url=f"{_frontend_base()}/?auth_error=token", status_code=302)
    access = tr.json().get("access_token")
    if not access:
        return RedirectResponse(url=f"{_frontend_base()}/?auth_error=token", status_code=302)
    async with httpx.AsyncClient(timeout=20.0) as client:
        ur = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access}"},
        )
    if ur.status_code != 200:
        return RedirectResponse(url=f"{_frontend_base()}/?auth_error=userinfo", status_code=302)
    info = ur.json()
    email = _norm_email(info.get("email") or "")
    if not email:
        return RedirectResponse(url=f"{_frontend_base()}/?auth_error=noemail", status_code=302)
    name = (info.get("name") or email.split("@")[0])[:255]
    u = db.query(User).filter(User.email == email).first()
    if not u:
        u = User(
            device_id=f"acct:{uuid4()}"[:255],
            email=email,
            password_hash=None,
            display_name=name,
        )
        db.add(u)
        db.commit()
        db.refresh(u)
    else:
        if name and not u.display_name:
            u.display_name = name
            db.commit()
    resp = RedirectResponse(url=f"{_frontend_base()}/?login=ok", status_code=302)
    same_site, secure = _cookie_same_site_policy()
    resp.delete_cookie(OAUTH_STATE_COOKIE, path="/", samesite=same_site, secure=secure)
    _set_session_cookie(resp, u.id, email)
    return resp


# —— Microsoft (Outlook / Entra) OAuth ——


@router.get("/oauth/microsoft/start")
def oauth_microsoft_start(request: Request):
    cid = (get_settings().microsoft_oauth_client_id or "").strip()
    if not cid:
        raise HTTPException(
            status_code=503,
            detail="未配置 MICROSOFT_OAUTH_CLIENT_ID：请在 Azure 门户注册应用并填写密钥与回调地址。",
        )
    state = secrets.token_urlsafe(24)
    redirect_uri = f"{_oauth_redirect_base()}/api/auth/oauth/microsoft/callback"
    q = urlencode(
        {
            "client_id": cid,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "response_mode": "query",
            "scope": "openid profile email offline_access https://graph.microsoft.com/User.Read",
            "state": state,
        }
    )
    url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?{q}"
    resp = RedirectResponse(url=url, status_code=302)
    same_site, secure = _cookie_same_site_policy()
    resp.set_cookie(
        OAUTH_STATE_COOKIE,
        state,
        max_age=OAUTH_STATE_MAX_AGE,
        httponly=True,
        samesite=same_site,
        secure=secure,
        path="/",
    )
    return resp


@router.get("/oauth/microsoft/callback")
async def oauth_microsoft_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if error:
        return RedirectResponse(url=f"{_frontend_base()}/?auth_error={error}", status_code=302)
    expected = request.cookies.get(OAUTH_STATE_COOKIE)
    if not state or not expected or state != expected:
        return RedirectResponse(url=f"{_frontend_base()}/?auth_error=state", status_code=302)
    cid = (get_settings().microsoft_oauth_client_id or "").strip()
    csec = (get_settings().microsoft_oauth_client_secret or "").strip()
    if not code or not cid or not csec:
        return RedirectResponse(url=f"{_frontend_base()}/?auth_error=missing", status_code=302)
    redirect_uri = f"{_oauth_redirect_base()}/api/auth/oauth/microsoft/callback"
    async with httpx.AsyncClient(timeout=30.0) as client:
        tr = await client.post(
            "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            data={
                "client_id": cid,
                "client_secret": csec,
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
                "scope": "openid profile email offline_access https://graph.microsoft.com/User.Read",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if tr.status_code != 200:
        return RedirectResponse(url=f"{_frontend_base()}/?auth_error=token", status_code=302)
    access = tr.json().get("access_token")
    if not access:
        return RedirectResponse(url=f"{_frontend_base()}/?auth_error=token", status_code=302)
    async with httpx.AsyncClient(timeout=20.0) as client:
        ur = await client.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {access}"},
        )
    if ur.status_code != 200:
        return RedirectResponse(url=f"{_frontend_base()}/?auth_error=userinfo", status_code=302)
    info = ur.json()
    email = _norm_email(info.get("mail") or info.get("userPrincipalName") or "")
    if not email:
        return RedirectResponse(url=f"{_frontend_base()}/?auth_error=noemail", status_code=302)
    name = (info.get("displayName") or email.split("@")[0])[:255]
    u = db.query(User).filter(User.email == email).first()
    if not u:
        u = User(
            device_id=f"acct:{uuid4()}"[:255],
            email=email,
            password_hash=None,
            display_name=name,
        )
        db.add(u)
        db.commit()
        db.refresh(u)
    else:
        if name and not u.display_name:
            u.display_name = name
            db.commit()
    resp = RedirectResponse(url=f"{_frontend_base()}/?login=ok", status_code=302)
    same_site, secure = _cookie_same_site_policy()
    resp.delete_cookie(OAUTH_STATE_COOKIE, path="/", samesite=same_site, secure=secure)
    _set_session_cookie(resp, u.id, email)
    return resp
