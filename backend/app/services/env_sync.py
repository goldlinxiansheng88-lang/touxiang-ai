"""将基础设施配置同步到 backend/.env，便于与进程外工具、重启后加载一致。"""

from __future__ import annotations

from pathlib import Path

from dotenv import set_key

# config_registry 的 key → .env 变量名
CONFIG_TO_ENV: dict[str, str] = {
    "database_url": "DATABASE_URL",
    "redis_url": "REDIS_URL",
    "encryption_key": "ENCRYPTION_KEY",
}


def backend_dotenv_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / ".env"


def sync_keys_to_dotenv(updates: dict[str, str]) -> None:
    """对给定配置键写入或更新 .env 中对应行（不存在则追加）。"""
    path = backend_dotenv_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")
    for k, v in updates.items():
        env_name = CONFIG_TO_ENV.get(k)
        if not env_name:
            continue
        set_key(str(path), env_name, v, quote_mode="always")
