"""彩虹屁 / aura 短文案：支持 Claude、Gemini、DeepSeek 三选一（由配置 aura_llm_provider 决定）。"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_FALLBACK = (
    "Your aura whispers of quiet mornings and untold stories. "
    "Soft light gathers where curiosity lingers."
)

_SYSTEM = (
    "You are AuraShift, a warm creative writer. Write 2–3 short sentences of poetic "
    "'aura reading' praise inspired by the user's chosen scene and style. "
    "No markdown, no title line, no quotation marks around the whole reply. English only."
)


def _user_message(scene: str, style: str) -> str:
    return f"Scene: {scene}. Style id: {style}. Write only the short reading text."


def _call_claude(api_key: str, user_text: str) -> str:
    r = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key.strip(),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-3-5-haiku-20241022",
            "max_tokens": 400,
            "system": _SYSTEM,
            "messages": [{"role": "user", "content": user_text}],
        },
        timeout=60.0,
    )
    r.raise_for_status()
    data = r.json()
    parts = data.get("content") or []
    if not parts or parts[0].get("type") != "text":
        raise ValueError("unexpected claude response shape")
    return str(parts[0].get("text") or "").strip()


def _call_gemini(api_key: str, scene: str, style: str) -> str:
    """Google AI Studio API Key；模型名可后续抽到配置。"""
    user_text = _user_message(scene, style)
    model = "gemini-1.5-flash"
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        f"?key={api_key.strip()}"
    )
    combined = f"{_SYSTEM}\n\n{user_text}"
    r = httpx.post(
        url,
        headers={"content-type": "application/json"},
        json={
            "contents": [{"role": "user", "parts": [{"text": combined}]}],
            "generationConfig": {"maxOutputTokens": 400, "temperature": 0.8},
        },
        timeout=60.0,
    )
    r.raise_for_status()
    data = r.json()
    cands = data.get("candidates") or []
    if not cands:
        raise ValueError("gemini: no candidates")
    parts = (cands[0].get("content") or {}).get("parts") or []
    if not parts:
        raise ValueError("gemini: no parts")
    return str(parts[0].get("text") or "").strip()


def _call_deepseek(api_key: str, user_text: str) -> str:
    r = httpx.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "authorization": f"Bearer {api_key.strip()}",
            "content-type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": user_text},
            ],
            "max_tokens": 400,
            "temperature": 0.8,
        },
        timeout=60.0,
    )
    r.raise_for_status()
    data = r.json()
    choices = data.get("choices") or []
    if not choices:
        raise ValueError("deepseek: no choices")
    return str(choices[0].get("message", {}).get("content") or "").strip()


def generate_vibe_copy(*, scene: str, style: str, db: "Session") -> tuple[str, str, str]:
    """
    返回 (preview, full_text, provider_tag)。
    provider_tag: claude | gemini | deepseek | fallback
    """
    from app.config import get_settings
    from app.services import config_service

    raw = (
        config_service.get("aura_llm_provider", default=get_settings().aura_llm_provider, db=db) or "claude"
    ).strip().lower()
    if raw not in ("claude", "gemini", "deepseek"):
        raw = "claude"

    user_text = _user_message(scene, style)

    try:
        if raw == "claude":
            key = (config_service.get("claude_api_key", default="", db=db) or "").strip()
            if not key:
                return _preview_full(_FALLBACK), _FALLBACK, "fallback"
            text = _call_claude(key, user_text)
        elif raw == "gemini":
            key = (config_service.get("gemini_api_key", default="", db=db) or "").strip()
            if not key:
                return _preview_full(_FALLBACK), _FALLBACK, "fallback"
            text = _call_gemini(key, scene, style)
        else:
            key = (config_service.get("deepseek_api_key", default="", db=db) or "").strip()
            if not key:
                return _preview_full(_FALLBACK), _FALLBACK, "fallback"
            text = _call_deepseek(key, user_text)

        if not text:
            return _preview_full(_FALLBACK), _FALLBACK, "fallback"
        return _preview_full(text), text, raw
    except Exception as e:
        logger.warning("vibe copywriter failed (%s): %s", raw, e)
        return _preview_full(_FALLBACK), _FALLBACK, "fallback"


def _preview_full(full: str) -> str:
    full = full.strip()
    if len(full) <= 200:
        return full
    return full[:200].rstrip() + "…"
