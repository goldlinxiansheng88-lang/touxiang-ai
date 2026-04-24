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
    # Nordics / Central & Eastern Europe (prefer local languages when we have them; otherwise fall back to en)
    "SE": "en",
    "NO": "en",
    "DK": "en",
    "FI": "en",
    "CZ": "en",
    "SK": "en",
    "HU": "en",
    "RO": "en",
    "BG": "en",
    "GR": "en",
    "IL": "en",
    "ZA": "en",
    # More coverage for frequent visitors
    "PK": "hi",
    "BD": "hi",
    "LK": "hi",
    "MA": "ar",
    "DZ": "ar",
    "TN": "ar",
    "JO": "ar",
    "KW": "ar",
    "QA": "ar",
    "BH": "ar",
    "OM": "ar",
    "VN": "vi",
    "TR": "tr",
    "KZ": "ru",
    "MD": "ru",
    "LT": "en",
    "LV": "en",
    "EE": "en",
    "IS": "en",
    "NG": "en",
    "KE": "en",
    "GH": "en",
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


def _best_locale_from_accept_language(request: Request) -> str | None:
    """
    Best-effort parsing for browser language preference.
    We intentionally keep this minimal and only return locales the frontend supports.
    """
    raw = (request.headers.get("accept-language") or request.headers.get("Accept-Language") or "").strip()
    if not raw:
        return None
    supported = {
        "en",
        "zh-CN",
        "zh-TW",
        "ja",
        "ko",
        "es",
        "fr",
        "de",
        "pt-BR",
        "ru",
        "ar",
        "hi",
        "id",
        "th",
        "vi",
        "tr",
        "pl",
        "nl",
        "it",
        "uk",
        "ms",
    }
    # parse in order; ignore q for simplicity (browsers already order by preference)
    for part in raw.split(","):
        code = part.split(";", 1)[0].strip()
        if not code:
            continue
        low = code.lower().replace("_", "-")
        if low in ("zh", "zh-cn", "zh-hans"):
            cand = "zh-CN"
        elif low in ("zh-tw", "zh-hk", "zh-mo", "zh-hant"):
            cand = "zh-TW"
        elif low.startswith("pt-"):
            cand = "pt-BR"
        else:
            cand = code.split("-", 1)[0]
        if cand in supported:
            return cand
    return None


@router.get("/detect")
def detect_locale(request: Request) -> dict[str, Any]:
    """返回推荐 locale；本地/内网 IP 无法解析时返回 en。"""
    ip = _client_ip(request)
    if not ip or ip in ("127.0.0.1", "::1", "localhost"):
        al = _best_locale_from_accept_language(request) or "en"
        return {"locale": al, "country_code": None, "source": "loopback"}

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
        al = _best_locale_from_accept_language(request)
        return {"locale": al or "en", "country_code": None, "source": "error" if not al else "accept_language"}

    if data.get("status") != "success":
        al = _best_locale_from_accept_language(request)
        return {"locale": al or "en", "country_code": None, "source": "geoip_fail" if not al else "accept_language"}

    cc = (data.get("countryCode") or "").strip().upper()
    loc = _locale_from_country(cc)
    # If geoip maps to en but browser has a more specific supported locale, prefer it
    if loc == "en":
        al = _best_locale_from_accept_language(request)
        if al and al != "en":
            return {"locale": al, "country_code": cc or None, "source": "accept_language"}
    return {"locale": loc, "country_code": cc or None, "source": "geoip"}
