import logging
import os
import re
from contextlib import asynccontextmanager
from pathlib import Path

from urllib.parse import parse_qsl, urlparse

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import InterfaceError, OperationalError, ProgrammingError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import admin, auth_endpoints, locale_endpoints, payments, public, webhooks
from app.bootstrap import seed_system_configs
from app.config import get_backend_root, get_loaded_env_file_paths, get_settings
from app.database import Base, SessionLocal, get_engine, prepare_postgres_url

logger = logging.getLogger(__name__)


def _parse_cors_origins(raw: str) -> list[str]:
    parts = [p.strip() for p in (raw or "").split(",")]
    return [p for p in parts if p]


def _build_cors_allow_origins() -> list[str]:
    """
    Browser security rule: you cannot use Access-Control-Allow-Origin: * together with credentials.

    Our frontend axios uses withCredentials=true (cookies), so we must return an explicit Origin echo.
    """
    s = get_settings()
    merged = []
    merged.extend(_parse_cors_origins(s.cors_allowed_origins))
    if (s.frontend_url or "").strip():
        merged.append(str(s.frontend_url).strip().rstrip("/"))
    if (s.public_base_url or "").strip():
        merged.append(str(s.public_base_url).strip().rstrip("/"))

    # De-dupe while preserving order
    out: list[str] = []
    seen: set[str] = set()
    for o in merged:
        if o in seen:
            continue
        seen.add(o)
        out.append(o)

    if not out:
        # Sensible local defaults (dev)
        out = ["http://localhost:5173", "http://127.0.0.1:5173"]

    return out


def _build_cors_allow_origin_regex() -> str | None:
    """
    Vercel Preview domains change frequently. Regex-based allowlisting avoids needing to
    update CORS for every new deployment hostname, while still avoiding wildcard '*'.
    """
    s = get_settings()
    custom = (s.cors_allow_origin_regex or "").strip()
    if custom:
        return custom
    if not bool(s.cors_enable_vercel_preview_regex):
        return None
    # HTTPS only; matches typical Vercel preview/prod hostnames on vercel.app
    # Note: preview hostnames can contain multiple dot-separated labels before vercel.app.
    parts: list[str] = [
        r"^https://(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+vercel\.app$"
    ]
    # Also allow the configured frontend / API hostnames when they are real HTTPS origins.
    # This helps teams using custom domains (or Vercel Preview Deployment Suffix) where the
    # browser Origin is not *.vercel.app, without forcing every hostname into allow_origins.
    for raw in (str(s.frontend_url or "").strip(), str(s.public_base_url or "").strip()):
        if not raw:
            continue
        try:
            u = urlparse(raw if "://" in raw else f"https://{raw}")
        except Exception:
            continue
        if u.scheme != "https" or not u.hostname:
            continue
        host = u.hostname.lower()
        if host.endswith(".vercel.app"):
            continue
        label = r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)"
        escaped = re.escape(host).replace(r"\*", rf"{label}")
        parts.append(rf"^https://{escaped}$")

    if len(parts) == 1:
        return parts[0]
    return "(?:" + "|".join(parts) + ")"


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=get_engine())
        # 旧库补列：邮箱登录 / OAuth
        try:
            with get_engine().begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(320)"
                    )
                )
                conn.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)"
                    )
                )
                conn.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN IF NOT EXISTS display_name VARCHAR(255)"
                    )
                )
                conn.execute(
                    text(
                        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_channel VARCHAR(32)"
                    )
                )
                conn.execute(
                    text(
                        "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS aspect_ratio VARCHAR(16) NOT NULL DEFAULT 'auto'"
                    )
                )
        except Exception as e:
            logger.warning("users 表补列未完成（若为新库可忽略）：%s", e)
        db = SessionLocal()
        try:
            seed_system_configs(db)
        finally:
            db.close()
    except Exception as e:
        logger.warning("数据库启动阶段未完成建表/播种（修正 DATABASE_URL 后请重启 API）：%s", e, exc_info=True)
    yield


app = FastAPI(title="AuraShift.ai API", version="3.0.0", lifespan=lifespan)


@app.exception_handler(OperationalError)
async def sqlalchemy_operational_handler(_request: Request, _exc: OperationalError) -> JSONResponse:
    """PostgreSQL 不可达时给出明确提示，避免前端只显示泛化的「检查 ENCRYPTION_KEY」。"""
    return JSONResponse(
        status_code=503,
        content={
            "detail": (
                "数据库连接失败：请核对 backend/.env 中的 DATABASE_URL（密码特殊字符需 URL 编码，云库常需 ?sslmode=require），"
                "确认 PostgreSQL 可达。保存系统配置后本进程会按新串重建连接池；若仍失败请访问 /health/db 查看详情，"
                "或重启 API 后再试。"
            )
        },
    )


@app.exception_handler(InterfaceError)
async def sqlalchemy_interface_handler(_request: Request, _exc: InterfaceError) -> JSONResponse:
    """连接池失效、连接被服务端关闭等，与 OperationalError 区分时仍给明确 JSON。"""
    return JSONResponse(
        status_code=503,
        content={
            "detail": (
                "数据库连接已中断或失效。请确认 PostgreSQL 仍在线；修改 DATABASE_URL 并保存后一般会重建连接池，"
                "若仍失败可重启 API；长时间空闲后偶发可重启进程后再试。"
            )
        },
    )


@app.exception_handler(ProgrammingError)
async def sqlalchemy_programming_handler(request: Request, exc: ProgrammingError) -> JSONResponse:
    """表不存在、迁移未完成等：返回 JSON detail，避免前端只看到 Axios 泛化 500。"""
    logger.warning("%s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=503,
        content={
            "detail": (
                "数据库结构异常（常见：表尚未创建、迁移未完成或与当前代码不一致）。"
                "请确认 PostgreSQL 可连接后重启 API（启动阶段会执行建表）；修改 DATABASE_URL 并保存后，本进程会重建连接池，一般无需再重启。"
                f" 原始错误：{str(exc)[:1200]}"
            )
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """未捕获异常时仍返回 JSON detail，避免前端只看到泛化 500 且无正文。"""
    if isinstance(exc, RequestValidationError):
        return await request_validation_exception_handler(request, exc)
    # FastAPI 的 HTTPException 继承自 Starlette；两者都交给框架默认处理
    if isinstance(exc, (StarletteHTTPException, HTTPException)):
        return await http_exception_handler(request, exc)
    logger.exception("%s %s", request.method, request.url.path, exc_info=exc)
    msg = f"{type(exc).__name__}: {exc!s}"
    return JSONResponse(status_code=500, content={"detail": msg[:2000]})


app.add_middleware(
    CORSMiddleware,
    allow_origins=_build_cors_allow_origins(),
    allow_origin_regex=_build_cors_allow_origin_regex(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_root = Path(__file__).resolve().parent.parent / "uploads"
upload_root.mkdir(parents=True, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=str(upload_root)), name="uploads")

app.include_router(public.router)
app.include_router(locale_endpoints.router)
app.include_router(auth_endpoints.router)
app.include_router(payments.router)
app.include_router(webhooks.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    # Provide a minimal build fingerprint to verify which commit is deployed.
    # Railway commonly injects these; if missing, we still return status ok.
    sha = (
        os.environ.get("RAILWAY_GIT_COMMIT_SHA")
        or os.environ.get("GIT_COMMIT_SHA")
        or os.environ.get("COMMIT_SHA")
        or os.environ.get("SOURCE_VERSION")
        or os.environ.get("VERCEL_GIT_COMMIT_SHA")
        or ""
    ).strip()
    return {"status": "ok", "commit": sha[:12] or None}


@app.get("/health/cors")
def health_cors():
    """诊断：当前进程实际生效的 CORS 配置（不含密钥）。"""
    s = get_settings()
    return {
        "cors": {
            "allow_origins": _build_cors_allow_origins(),
            "allow_origin_regex": _build_cors_allow_origin_regex(),
            "settings": {
                "frontend_url": str(s.frontend_url or "").strip(),
                "public_base_url": str(s.public_base_url or "").strip(),
                "cors_allowed_origins": str(s.cors_allowed_origins or "").strip(),
                "cors_allow_origin_regex": str(s.cors_allow_origin_regex or "").strip(),
                "cors_enable_vercel_preview_regex": bool(s.cors_enable_vercel_preview_regex),
            },
        }
    }


@app.get("/healthy/db")
def health_db_common_typo():
    """常见笔误 /healthy/db → 重定向到 /health/db。"""
    return RedirectResponse(url="/health/db", status_code=307)


@app.get("/health/db")
def health_db():
    """无需鉴权：用于确认当前进程能否连上 DATABASE_URL 中的 PostgreSQL（不返回账号密码）。"""
    s = get_settings()
    prepared = prepare_postgres_url(s.database_url)
    p = urlparse(prepared)
    q = dict(parse_qsl(p.query, keep_blank_values=True))
    meta = {
        "scheme": p.scheme,
        "host": p.hostname,
        "port": p.port,
        "dbname": (p.path or "").lstrip("/") or None,
        "sslmode": q.get("sslmode") or q.get("ssl"),
        "encryption_key_set": bool((s.encryption_key or "").strip()),
        "process_env_has_database_url": "DATABASE_URL" in os.environ,
    }
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"database": "ok", **meta}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "database": "error",
                "detail": str(e),
                **meta,
                "hint": (
                    "常见原因：① DNS 无法解析 host（本机可试改 DNS、换热点、或用 Session pooler 连接串）② 密码含 @#/ 等未做 URL 编码 ③ TLS/sslmode。"
                    "若 process_env_has_database_url 为 true，说明系统环境变量里也有 DATABASE_URL，会覆盖 backend/.env；请删环境变量或改成与 .env 一致后重启 API。"
                ),
            },
        )


@app.get("/health/redis")
def health_redis():
    """无需鉴权：检查 Celery broker 使用的 Redis 是否可达。"""
    try:
        import redis

        r = redis.Redis.from_url(get_settings().redis_url, socket_connect_timeout=3, socket_timeout=3)
        r.ping()
        return {"redis": "ok"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "redis": "error",
                "detail": str(e),
                "hint": "生成任务依赖可连的 Redis 与 Celery Worker。请在 .env 配置 REDIS_URL（云 Redis 或本机已启动的 Redis）。",
            },
        )


@app.get("/health/env")
def health_env():
    """诊断：.env 是否从预期路径加载（与 shell 当前目录无关）。不返回任何密钥。"""
    paths = get_loaded_env_file_paths()
    exists_map = {p: Path(p).is_file() for p in paths}
    s = get_settings()
    prepared = prepare_postgres_url(s.database_url)
    pu = urlparse(prepared)
    return {
        "backend_root": str(get_backend_root()),
        "env_files": paths,
        "env_file_exists": exists_map,
        "database_sslmode_override": (s.database_sslmode or "").strip() or None,
        "resolved_db_host": pu.hostname,
        "resolved_db_port": pu.port,
        "process_env_defines_database_url": "DATABASE_URL" in os.environ,
        "process_env_defines_redis_url": "REDIS_URL" in os.environ,
        "note": (
            "若 env_file_exists 中任一为 false，对应路径尚无文件，仅依赖系统环境变量或内置默认值。"
            "Pydantic 规则：若操作系统/容器已设置 DATABASE_URL 或 REDIS_URL，会覆盖 .env 中的同名字段（易误判为「没读到 .env」）。"
            "后台保存配置并同步 backend/.env 后，本服务会 clear_settings_cache 并按新 DATABASE_URL 重建连接池。"
        ),
    }
