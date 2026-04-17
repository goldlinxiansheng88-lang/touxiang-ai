import ipaddress
import threading
from collections.abc import Generator
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import get_settings


def normalize_postgres_url(url: str) -> str:
    """SQLAlchemy 默认 postgresql:// 会走 psycopg2；本项目仅安装 psycopg v3，须使用 postgresql+psycopg://。"""
    u = (url or "").strip().replace("\r", "").replace("\n", "")
    if not u:
        return u
    low = u.lower()
    if low.startswith("postgresql+") or low.startswith("postgres+"):
        return u
    if low.startswith("postgresql://"):
        return "postgresql+psycopg://" + u.split("://", 1)[1]
    if low.startswith("postgres://"):
        return "postgresql+psycopg://" + u.split("://", 1)[1]
    return u


def _host_likely_requires_tls(hostname: str) -> bool:
    """判断是否在未显式写 sslmode 时应默认加 sslmode=require（Docker 单主机名如 postgres 不加）。"""
    host = (hostname or "").strip().lower()
    if not host:
        return False
    if host in ("localhost", "127.0.0.1", "::1"):
        return False
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_loopback or ip.is_private or ip.is_link_local:
            return False
        return True
    except ValueError:
        pass
    # 单段主机名（Docker / K8s 服务名）默认不强行 SSL
    if "." not in host:
        return False
    if host.endswith((".local", ".lan", ".internal", ".localhost")):
        return False
    markers = (
        "supabase.co",
        "supabase.com",
        "neon.tech",
        "render.com",
        "railway.app",
        "azure.com",
        "rds.amazonaws.com",
        "cloud.google.com",
        "timescale.com",
        "aiven.io",
    )
    if any(m in host for m in markers):
        return True
    # 公网域名（含多段）常见需 TLS
    return True


def augment_supabase_libpq_defaults(url: str) -> str:
    """Supabase：为 Windows 上偶发的 GSS 协商与解析问题追加安全默认值（不改变密码）。"""
    try:
        p = urlparse(url)
        host = (p.hostname or "").lower()
        if "supabase.co" not in host and "supabase.com" not in host:
            return url
        q = dict(parse_qsl(p.query, keep_blank_values=True))
        lk = {k.lower() for k in q}
        if "gssencmode" not in lk:
            q["gssencmode"] = "disable"
        return urlunparse((p.scheme, p.netloc, p.path, p.params, urlencode(q), p.fragment))
    except Exception:
        return url


def augment_postgres_url_for_cloud_tls(url: str) -> str:
    """云端 / 公网 PostgreSQL 常要求 TLS；未带 ssl 参数时自动追加 sslmode=require。"""
    try:
        p = urlparse(url)
    except Exception:
        return url
    host = (p.hostname or "").lower()
    if not host:
        return url
    q = dict(parse_qsl(p.query, keep_blank_values=True))
    if any(k.lower() in ("sslmode", "ssl") for k in q):
        return url
    if not _host_likely_requires_tls(host):
        return url
    q["sslmode"] = "require"
    return urlunparse((p.scheme, p.netloc, p.path, p.params, urlencode(q), p.fragment))


def prepare_postgres_url(url: str) -> str:
    """供 SQLAlchemy 与「连接检测」共用：驱动前缀 + 云端 SSL；可选 Settings.database_sslmode 覆盖/补充。"""
    u = augment_supabase_libpq_defaults(augment_postgres_url_for_cloud_tls(normalize_postgres_url(url)))
    extra = (get_settings().database_sslmode or "").strip().lower()
    if not extra:
        return u
    try:
        p = urlparse(u)
        q = dict(parse_qsl(p.query, keep_blank_values=True))
        if "sslmode" in {k.lower() for k in q}:
            return u
        q["sslmode"] = extra
        return urlunparse((p.scheme, p.netloc, p.path, p.params, urlencode(q), p.fragment))
    except Exception:
        return u


Base = declarative_base()

_lock = threading.Lock()
_engine: Engine | None = None
_session_maker = None
_bound_url: str | None = None


def get_engine() -> Engine:
    """按当前 Settings 中的 DATABASE_URL 返回 Engine；URL 变化时释放旧连接池并重建。

    解决：模块 import 时只建一次 engine 导致改 .env / 后台保存连接串后进程仍用旧库的问题。
    """
    global _engine, _bound_url, _session_maker
    url = prepare_postgres_url(get_settings().database_url)
    with _lock:
        if _engine is not None and _bound_url == url:
            return _engine
        if _engine is not None:
            _engine.dispose()
        # prepare_threshold=None：Supabase Transaction pooler（6543）与 PgBouncer 下避免预编译语句冲突（DuplicatePreparedStatement 等）
        _engine = create_engine(
            url,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 20,
                "prepare_threshold": None,
            },
        )
        _session_maker = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        _bound_url = url
        return _engine


class _SessionLocalProxy:
    """始终使用当前 get_engine() 绑定的会话工厂，避免 import 时绑死旧 engine。"""

    def __call__(self, *args, **kwargs):
        get_engine()
        assert _session_maker is not None
        return _session_maker(*args, **kwargs)


SessionLocal = _SessionLocalProxy()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
