from __future__ import annotations

import mimetypes
from dataclasses import dataclass

from app.config import get_settings
from app.services import config_service


@dataclass(frozen=True)
class S3Config:
    access_key: str
    secret_key: str
    bucket: str
    region: str
    endpoint_url: str
    public_base_url: str


def _clean(s: str | None) -> str:
    return (s or "").strip()


def load_s3_config(*, db) -> S3Config | None:
    """读取 S3/R2 配置。缺任一关键项则返回 None。"""
    settings = get_settings()
    ak = _clean(config_service.get("s3_access_key", default="", db=db) or "")
    sk = _clean(config_service.get("s3_secret_key", default="", db=db) or "")
    bucket = _clean(config_service.get("s3_bucket_name", default="", db=db) or "")
    region = _clean(config_service.get("s3_region", default="us-east-1", db=db) or "us-east-1")
    endpoint = _clean(config_service.get("s3_endpoint_url", default="", db=db) or "")
    public_base = _clean(config_service.get("s3_public_base_url", default="", db=db) or "")

    # 允许只用环境变量（部署平台）覆盖：S3_ENDPOINT_URL / S3_PUBLIC_BASE_URL
    endpoint = endpoint or _clean(getattr(settings, "s3_endpoint_url", ""))
    public_base = public_base or _clean(getattr(settings, "s3_public_base_url", ""))

    if not (ak and sk and bucket and endpoint and public_base):
        return None
    return S3Config(
        access_key=ak,
        secret_key=sk,
        bucket=bucket,
        region=region or "us-east-1",
        endpoint_url=endpoint,
        public_base_url=public_base.rstrip("/"),
    )


def _client(cfg: S3Config):
    import boto3

    return boto3.client(
        "s3",
        aws_access_key_id=cfg.access_key,
        aws_secret_access_key=cfg.secret_key,
        region_name=cfg.region,
        endpoint_url=cfg.endpoint_url,
    )


def public_url(cfg: S3Config, key: str) -> str:
    key = key.lstrip("/")
    return f"{cfg.public_base_url}/{key}"


def put_bytes(
    *,
    cfg: S3Config,
    key: str,
    data: bytes,
    content_type: str | None = None,
    cache_control: str = "public, max-age=31536000, immutable",
) -> str:
    key = key.lstrip("/")
    ct = content_type or mimetypes.guess_type(key)[0] or "application/octet-stream"
    _client(cfg).put_object(
        Bucket=cfg.bucket,
        Key=key,
        Body=data,
        ContentType=ct,
        CacheControl=cache_control,
    )
    return public_url(cfg, key)

