"""根据客户端 IP 推断地区，返回推荐界面语言（需可访问 ip-api.com）。"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/locale", tags=["locale"])

# ISO 3166-1 alpha-2 → vue-i18n locale code
COUNTRY_TO_LOCALE: dict[str, str] = {
    "CN": "zh-CN",
    "TW": "zh-TW",
    "HK": "zh-TW",
    "MO": "zh-TW",
    "JP": "ja",
    "KR": "ko",
    "US": "en",
    "GB": "en",
    "AU": "en",
    "NZ": "en",
    "CA": "en",
    "IE": "en",
    "SG": "en",
    "DE": "de",
    "AT": "de",
    "CH": "de",
    "FR": "fr",
    "BE": "fr",
    "ES": "es",
    "MX": "es",
    "AR": "es",
    "CO": "es",
    "CL": "es",
    "BR": "pt-BR",
    "PT": "pt-BR",
    "RU": "ru",
    "BY": "ru",
    "UA": "uk",
    "PL": "pl",
    "IT": "it",
    "NL": "nl",
    "TR": "tr",
    "SA": "ar",
    "AE": "ar",
    "EG": "ar",
    "IQ": "ar",
    "IN": "hi",
    "ID": "id",
    "MY": "ms",
    "TH": "th",
    "VN": "vi",
    "PH": "en",
    "SE": "en",
    "NO": "en",
    "DK": "en",
    "FI": "en",
    "CZ": "en",
    "HU": "en",
    "RO": "en",
    "GR": "en",
    "IL": "en",
    "ZA": "en",
}


def _client_ip(request: Request) -> str | None:
    xff = request.headers.get("x-forwarded-for") or request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def _locale_from_country(country_code: str) -> str:
    cc = (country_code or "").strip().upper()
    return COUNTRY_TO_LOCALE.get(cc, "en")


@router.get("/detect")
def detect_locale(request: Request) -> dict[str, Any]:
    """返回推荐 locale；本地/内网 IP 无法解析时返回 en。"""
    ip = _client_ip(request)
    if not ip or ip in ("127.0.0.1", "::1", "localhost"):
        return {"locale": "en", "country_code": None, "source": "loopback"}

    # ip-api 免费：HTTP、IPv4；失败时回落 en
    try:
        r = httpx.get(
            f"http://ip-api.com/json/{ip}",
            params={"fields": "status,message,countryCode"},
            timeout=3.0,
        )
        data = r.json()
    except Exception as e:
        logger.debug("geoip request failed: %s", e)
        return {"locale": "en", "country_code": None, "source": "error"}

    if data.get("status") != "success":
        return {"locale": "en", "country_code": None, "source": "geoip_fail"}

    cc = (data.get("countryCode") or "").strip().upper()
    loc = _locale_from_country(cc)
    return {"locale": loc, "country_code": cc or None, "source": "geoip"}
