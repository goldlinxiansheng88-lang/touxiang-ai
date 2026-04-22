from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 与「当前工作目录 cwd」无关：始终指向 backend 目录下的 .env（否则在仓库根目录启动 uvicorn 时会读错文件，仍用默认 localhost 连接串）
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_REPO_ROOT_ENV = _BACKEND_ROOT.parent / ".env"
# 后加载的覆盖先加载的：仓库根 .env 先、backend/.env 后，保证服务专用配置优先
_ENV_FILES: list[Path] = []
for _p in (_REPO_ROOT_ENV, _BACKEND_ROOT / ".env"):
    if _p.is_file():
        _ENV_FILES.append(_p)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # env_file 顺序：仓库根 .env 先、backend/.env 后（后者覆盖前者）。另：操作系统里的 DATABASE_URL 等会再覆盖文件（见 /health/env）
        env_file=tuple(str(p) for p in _ENV_FILES) if _ENV_FILES else str(_BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg://aurashift:aurashift@localhost:5432/aurashift"
    #: 若连接串未带 sslmode，可设为 require / disable 等（见 libpq sslmode）
    database_sslmode: str = ""
    redis_url: str = "redis://localhost:6379/0"
    encryption_key: str = ""
    admin_email: str = "admin@aurashift.ai"
    admin_password: str = "changeme"
    public_base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"

    claude_api_key: str = ""
    #: 彩虹屁文案：claude | gemini | deepseek（与配置库 aura_llm_provider 一致）
    aura_llm_provider: str = "claude"
    gemini_api_key: str = ""
    deepseek_api_key: str = ""
    image_api_key: str = ""
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    creem_api_key: str = ""
    creem_product_id: str = ""
    creem_webhook_secret: str = ""
    creem_api_base_url: str = "https://api.creem.io"

    #: 若将 API 标准输出重定向到某文件，可填绝对或相对路径；后台「终端运行日志」将读取该文件尾部。
    runtime_log_file: str = ""

    #: JWT 签名密钥；留空则使用 ENCRYPTION_KEY 派生（建议生产单独设置）
    jwt_secret: str = ""
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    microsoft_oauth_client_id: str = ""
    microsoft_oauth_client_secret: str = ""

    # —— 存储（S3 兼容，如 Cloudflare R2）——
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket_name: str = ""
    s3_region: str = "us-east-1"
    s3_endpoint_url: str = ""
    s3_public_base_url: str = ""

    @field_validator("database_url", "redis_url", "runtime_log_file", "database_sslmode", mode="before")
    @classmethod
    def strip_env_junk(cls, v: object) -> object:
        if v is None:
            return v
        s = str(v).strip().replace("\r", "").replace("\n", "")
        return s


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    """使下次 get_settings() 重新读环境变量 / .env。修改 DATABASE_URL 后需配合 database.get_engine() 才会用上新连接串。"""
    get_settings.cache_clear()


def get_backend_root() -> Path:
    """backend 包所在目录（含 .env 预期位置）。"""
    return _BACKEND_ROOT


def get_loaded_env_file_paths() -> tuple[str, ...]:
    """实际参与加载的 .env 绝对路径（无文件时可能仍指向默认路径供诊断）。"""
    return tuple(str(p) for p in _ENV_FILES) if _ENV_FILES else (str(_BACKEND_ROOT / ".env"),)
