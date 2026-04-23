"""管理后台「连接」按钮：按配置项 key 做轻量连通性检测。"""

from __future__ import annotations

import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.data.config_registry import entry_by_key
from app.database import prepare_postgres_url
from app.services import config_service

# 与前端 CONFIG_TESTABLE_KEYS 保持一致
TESTABLE_KEYS = frozenset(
    {
        "database_url",
        "redis_url",
        "encryption_key",
        "public_base_url",
        "frontend_url",
        "claude_api_key",
        "aura_llm_provider",
        "gemini_api_key",
        "deepseek_api_key",
        "image_api_key",
        "image_api_endpoint",
        "fal_key",
        "flux_img2img_model_id",
        "s3_access_key",
        "s3_secret_key",
        "s3_bucket_name",
        "s3_region",
        "stripe_secret_key",
        "lemon_squeezy_api_key",
        "usdt_receive_address",
    }
)


def _mask_sentinel(val: str | None) -> bool:
    if not val:
        return True
    s = val.strip()
    return s == "" or "••••" in s


def resolve_value(key: str, body_value: str | None, db: Session) -> str:
    if not _mask_sentinel(body_value):
        return (body_value or "").strip()
    ent = entry_by_key(key)
    default = ent.default if ent else None
    raw = config_service.get(key, default=default, db=db)
    if raw is not None and str(raw).strip():
        return str(raw).strip()
    s = get_settings()
    v = getattr(s, key, None)
    if v is not None and str(v).strip():
        return str(v).strip()
    return ""


def _related_get(related: dict[str, str] | None, key: str, db: Session) -> str:
    if related and key in related and not _mask_sentinel(related.get(key)):
        return (related[key] or "").strip()
    return resolve_value(key, None, db)


def run_connection_test(
    key: str,
    body_value: str | None,
    related: dict[str, str] | None,
    db: Session,
) -> tuple[bool, str]:
    if key not in TESTABLE_KEYS:
        raise ValueError("此项暂不支持连通性检测")

    if key == "database_url":
        url = resolve_value(key, body_value, db)
        if not url:
            return False, "未填写完整的数据库信息（主机、库名等）"
        try:
            eng = create_engine(
                prepare_postgres_url(url),
                pool_pre_ping=True,
                connect_args={"connect_timeout": 20, "prepare_threshold": None},
            )
            with eng.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True, "连接成功（PostgreSQL）"
        except Exception as e:
            return False, f"连接失败：{e!s}"[:500]

    if key == "redis_url":
        url = resolve_value(key, body_value, db)
        if not url:
            return False, "未填写 Redis（主机等）"
        try:
            import redis

            r = redis.Redis.from_url(url, socket_connect_timeout=8, socket_timeout=8)
            r.ping()
            return True, "连接成功（Redis PING）"
        except Exception as e:
            return False, f"连接失败：{e!s}"[:500]

    if key == "encryption_key":
        raw = resolve_value(key, body_value, db)
        if not raw:
            return False, "未填写加密主密钥"
        try:
            from cryptography.fernet import Fernet

            Fernet(raw.encode("utf-8"))
            return True, "密钥格式有效（Fernet）"
        except Exception as e:
            return False, f"无效密钥：{e!s}"[:500]

    if key in ("public_base_url", "frontend_url"):
        url = resolve_value(key, body_value, db)
        if not url:
            return False, "未填写 URL"
        return _test_http_url(url, label="站点")

    if key == "claude_api_key":
        api_key = resolve_value(key, body_value, db)
        if not api_key:
            return False, "未填写 API Key"
        try:
            r = httpx.get(
                "https://api.anthropic.com/v1/models",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
                timeout=20.0,
            )
            if r.status_code == 200:
                return True, "连接成功（Anthropic 密钥有效）"
            if r.status_code in (401, 403):
                return False, "连接失败：密钥无效或无权限"
            return False, f"连接失败：HTTP {r.status_code}"
        except httpx.RequestError as e:
            return False, f"网络错误：{e!s}"[:500]

    if key == "aura_llm_provider":
        v = (resolve_value(key, body_value, db) or "").strip().lower()
        if v in ("claude", "gemini", "deepseek"):
            return True, f"已选择：{v}"
        return False, "须为 claude、gemini 或 deepseek（小写）"

    if key == "gemini_api_key":
        api_key = resolve_value(key, body_value, db)
        if not api_key:
            return False, "未填写 Gemini API Key"
        try:
            r = httpx.get(
                "https://generativelanguage.googleapis.com/v1beta/models",
                params={"key": api_key},
                timeout=20.0,
            )
            if r.status_code == 200:
                return True, "连接成功（Gemini 密钥可用）"
            if r.status_code in (400, 401, 403):
                return False, "连接失败：密钥无效或无权限"
            return False, f"连接失败：HTTP {r.status_code}"
        except httpx.RequestError as e:
            return False, f"网络错误：{e!s}"[:500]

    if key == "deepseek_api_key":
        api_key = resolve_value(key, body_value, db)
        if not api_key:
            return False, "未填写 DeepSeek API Key"
        try:
            r = httpx.get(
                "https://api.deepseek.com/v1/models",
                headers={"authorization": f"Bearer {api_key}"},
                timeout=20.0,
            )
            if r.status_code == 200:
                return True, "连接成功（DeepSeek 密钥可用）"
            if r.status_code in (401, 403):
                return False, "连接失败：密钥无效或无权限"
            return False, f"连接失败：HTTP {r.status_code}"
        except httpx.RequestError as e:
            return False, f"网络错误：{e!s}"[:500]

    if key == "image_api_endpoint":
        endpoint = resolve_value(key, body_value, db)
        if not endpoint:
            return False, "未填写图像 API 根地址"
        return _test_http_url(endpoint, label="图像 API")

    if key == "image_api_key":
        token = resolve_value(key, body_value, db)
        endpoint = _related_get(related, "image_api_endpoint", db)
        if not token:
            return False, "未填写图像 API Key"
        if not endpoint:
            endpoint = "https://api.replicate.com/v1"
        base = endpoint.rstrip("/")
        try:
            r = httpx.get(
                f"{base}/models",
                headers={"Authorization": f"Token {token}"},
                timeout=20.0,
            )
            if r.status_code == 200:
                return True, "连接成功（Replicate 密钥有效）"
            if r.status_code in (401, 403):
                return False, "连接失败：Token 无效"
            return False, f"连接失败：HTTP {r.status_code}"
        except httpx.RequestError as e:
            return False, f"网络错误：{e!s}"[:500]

    if key == "fal_key":
        token = resolve_value(key, body_value, db)
        if not token:
            return False, "未填写 Fal API Key"
        try:
            url = "https://api.fal.ai/v1/models"
            for prefix in ("Key", "Bearer"):
                r = httpx.get(
                    url,
                    headers={"Authorization": f"{prefix} {token}"},
                    timeout=20.0,
                )
                if r.status_code == 200:
                    return True, "连接成功（Fal 密钥可用）"
                if r.status_code not in (401, 403):
                    return False, f"连接失败：HTTP {r.status_code}"
            return False, "连接失败：密钥无效或无权限"
        except httpx.RequestError as e:
            return False, f"网络错误：{e!s}"[:500]

    if key == "flux_img2img_model_id":
        mid = resolve_value(key, body_value, db)
        if not mid:
            return False, "未填写模型 ID"
        mid = mid.strip()
        if "/" not in mid:
            return False, "格式应为 fal endpoint，例如 fal-ai/flux/dev/image-to-image"
        return True, "格式有效（实际推理以 Worker 调用为准）"

    if key in (
        "s3_access_key",
        "s3_secret_key",
        "s3_bucket_name",
        "s3_region",
        "s3_endpoint_url",
        "s3_public_base_url",
    ):
        ak = _related_get(related, "s3_access_key", db)
        sk = _related_get(related, "s3_secret_key", db)
        bucket = _related_get(related, "s3_bucket_name", db)
        region = _related_get(related, "s3_region", db) or "us-east-1"
        endpoint = _related_get(related, "s3_endpoint_url", db)
        public_base = _related_get(related, "s3_public_base_url", db)
        if not ak or not sk or not bucket or not endpoint or not public_base:
            return False, "请填写 Access/Secret、桶、Endpoint URL、公网前缀后再测"
        try:
            import boto3
            from botocore.exceptions import ClientError

            client = boto3.client(
                "s3",
                aws_access_key_id=ak,
                aws_secret_access_key=sk,
                region_name=region,
                endpoint_url=str(endpoint).strip() or None,
            )
            client.head_bucket(Bucket=bucket)
            return True, "连接成功（S3 存储桶可访问）"
        except ClientError as e:
            return False, f"S3 错误：{e!s}"[:500]
        except Exception as e:
            return False, f"连接失败：{e!s}"[:500]

    if key == "stripe_secret_key":
        sk = resolve_value(key, body_value, db)
        if not sk:
            return False, "未填写 Stripe Secret Key"
        if not sk.startswith(("sk_", "rk_")):
            return False, "格式异常：应以 sk_ 或 rk_ 开头"
        try:
            import stripe

            stripe.api_key = sk
            stripe.Balance.retrieve()
            return True, "连接成功（Stripe 密钥有效）"
        except Exception as e:
            return False, f"连接失败：{e!s}"[:500]

    if key == "lemon_squeezy_api_key":
        api_key = resolve_value(key, body_value, db)
        store_id = _related_get(related, "lemon_squeezy_store_id", db)
        if not api_key:
            return False, "未填写 Lemon Squeezy API Key"
        if not store_id:
            return False, "请同时填写 Store ID 后再测"
        try:
            r = httpx.get(
                f"https://api.lemonsqueezy.com/v1/stores/{store_id}",
                headers={
                    "Accept": "application/vnd.api+json",
                    "Authorization": f"Bearer {api_key}",
                },
                timeout=20.0,
            )
            if r.status_code == 200:
                return True, "连接成功（Lemon Squeezy 密钥有效）"
            if r.status_code in (401, 403):
                return False, "连接失败：密钥无效或无权限"
            return False, f"连接失败：HTTP {r.status_code}"
        except httpx.RequestError as e:
            return False, f"网络错误：{e!s}"[:500]

    if key == "usdt_receive_address":
        addr = resolve_value(key, body_value, db)
        if not addr or len(addr.strip()) < 8:
            return False, "请填写收款地址"
        return True, "地址已填写（链上到账后请在订单页手动确认收款）"

    raise ValueError("此项暂不支持连通性检测")


def _test_http_url(url: str, *, label: str) -> tuple[bool, str]:
    u = url.strip()
    if not u.startswith(("http://", "https://")):
        return False, "URL 需以 http:// 或 https:// 开头"
    try:
        r = httpx.get(u, follow_redirects=True, timeout=12.0)
        if r.status_code < 500:
            return True, f"连接成功（{label} HTTP {r.status_code}）"
        return False, f"服务返回 HTTP {r.status_code}"
    except httpx.RequestError as e:
        return False, f"无法连接：{e!s}"[:500]
