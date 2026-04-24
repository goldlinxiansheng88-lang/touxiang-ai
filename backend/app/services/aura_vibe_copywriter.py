"""彩虹屁 / aura 短文案：支持 Claude、Gemini、DeepSeek 三选一（由配置 aura_llm_provider 决定）。"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_FALLBACK_BY_LOCALE: dict[str, str] = {
    "en": (
        "Your aura whispers of quiet mornings and untold stories. "
        "Soft light gathers where curiosity lingers."
    ),
    "zh-CN": "你的气场像清晨的微光，安静却坚定。温柔的好奇心在你身上流动，像把世界悄悄点亮。",
    "zh-TW": "你的氣場像清晨的微光，安靜卻堅定。溫柔的好奇心在你身上流動，像把世界悄悄點亮。",
    "ja": "あなたのオーラは静かな朝の光のように、やわらかく確かな強さをまとっています。好奇心がそっと世界を明るくします。",
    "ko": "당신의 오라는 고요한 아침빛처럼 부드럽고 단단해요. 은은한 호기심이 당신을 따라 세상을 밝혀요.",
    "es": "Tu aura susurra calma y determinación. Una curiosidad suave te acompaña y enciende el mundo a tu alrededor.",
    "fr": "Ton aura respire le calme et la détermination. Une curiosité douce t’accompagne et illumine le monde autour de toi.",
    "de": "Deine Aura wirkt ruhig und zugleich entschlossen. Sanfte Neugier begleitet dich und lässt die Welt um dich herum leuchten.",
    "pt-BR": "Sua aura mistura calma e coragem. Uma curiosidade suave te acompanha e ilumina tudo ao redor.",
    "ru": "Твоя аура — как тихий свет утра: мягкая, но уверенная. В тебе живёт любопытство, которое незаметно озаряет мир вокруг.",
    "ar": "هالتك تشبه ضوء الصباح الهادئ؛ لطيفة لكنها ثابتة. فضولٌ رقيق يرافقك ويُضيء العالم من حولك.",
    "hi": "तुम्हारी आभा शांत सुबह की रोशनी जैसी है—कोमल लेकिन दृढ़। एक नरम जिज्ञासा तुम्हारे साथ रहती है और आसपास की दुनिया को चमक देती है।",
    "id": "Auramu terasa tenang namun teguh. Rasa ingin tahu yang lembut menemanimu dan menerangi sekitarmu.",
    "th": "ออร่าของคุณเหมือนแสงยามเช้าที่สงบ นุ่มนวลแต่มั่นคง ความอยากรู้อ่อนโยนค่อย ๆ ทำให้โลกรอบตัวสว่างขึ้น",
    "vi": "Aura của bạn như ánh sáng buổi sớm: dịu dàng nhưng vững vàng. Sự tò mò nhẹ nhàng theo bạn và làm bừng sáng xung quanh.",
    "tr": "Auran sakin bir sabah ışığı gibi: yumuşak ama kararlı. Nazik bir merak seni takip ediyor ve etrafını aydınlatıyor.",
    "pl": "Twoja aura jest jak spokojne światło poranka: miękka, ale pewna. Delikatna ciekawość rozświetla wszystko wokół ciebie.",
    "nl": "Je aura voelt als rustig ochtendlicht: zacht maar standvastig. Een milde nieuwsgierigheid verlicht alles om je heen.",
    "it": "La tua aura è come la luce calma del mattino: morbida ma decisa. Una curiosità gentile illumina ciò che ti circonda.",
    "uk": "Твоя аура — мов тихе ранкове світло: м’яка, але впевнена. Ніжна цікавість супроводжує тебе й освітлює світ довкола.",
    "ms": "Aura kamu terasa tenang namun teguh. Rasa ingin tahu yang lembut menemani kamu dan menerangi sekeliling.",
}


def _norm_locale(code: str | None) -> str:
    v = (code or "").strip()
    if not v:
        return "en"
    low = v.lower().replace("_", "-")
    if low in ("zh-cn", "zh-hans", "zh"):
        return "zh-CN"
    if low in ("zh-tw", "zh-hant", "zh-hk", "zh-mo"):
        return "zh-TW"
    if low.startswith("pt"):
        return "pt-BR"
    # keep short codes like en/ja/ko/fr...
    if "-" in v:
        base = v.split("-", 1)[0]
        # we only special-case Chinese above; others fallback to base
        return base
    return v


def _system_prompt(locale_code: str) -> str:
    # Keep prompts simple and consistent across providers.
    lang = _norm_locale(locale_code)
    if lang == "zh-CN":
        out = "简体中文"
    elif lang == "zh-TW":
        out = "繁體中文"
    else:
        out = lang
    return (
        "You are AuraShift, a warm creative writer. Write 2–3 short sentences of poetic "
        "'aura reading' praise inspired by the user's chosen scene and style. "
        "No markdown, no title line, no quotation marks around the whole reply. "
        f"Write in {out}."
    )


def _user_message(scene: str, style: str) -> str:
    return f"Scene: {scene}. Style id: {style}. Write only the short reading text."


def _call_claude(api_key: str, user_text: str, system: str) -> str:
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
            "system": system,
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


def _call_gemini(api_key: str, scene: str, style: str, system: str) -> str:
    """Google AI Studio API Key；模型名可后续抽到配置。"""
    user_text = _user_message(scene, style)
    model = "gemini-1.5-flash"
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        f"?key={api_key.strip()}"
    )
    combined = f"{system}\n\n{user_text}"
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


def _call_deepseek(api_key: str, user_text: str, system: str) -> str:
    r = httpx.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "authorization": f"Bearer {api_key.strip()}",
            "content-type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system},
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


def generate_vibe_copy(*, scene: str, style: str, locale: str | None, db: "Session") -> tuple[str, str, str]:
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

    loc = _norm_locale(locale)
    system = _system_prompt(loc)
    user_text = _user_message(scene, style)
    fallback = _FALLBACK_BY_LOCALE.get(loc) or _FALLBACK_BY_LOCALE.get(_norm_locale(loc)) or _FALLBACK_BY_LOCALE["en"]

    try:
        if raw == "claude":
            key = (config_service.get("claude_api_key", default="", db=db) or "").strip()
            if not key:
                return _preview_full(fallback), fallback, "fallback"
            text = _call_claude(key, user_text, system)
        elif raw == "gemini":
            key = (config_service.get("gemini_api_key", default="", db=db) or "").strip()
            if not key:
                return _preview_full(fallback), fallback, "fallback"
            text = _call_gemini(key, scene, style, system)
        else:
            key = (config_service.get("deepseek_api_key", default="", db=db) or "").strip()
            if not key:
                return _preview_full(fallback), fallback, "fallback"
            text = _call_deepseek(key, user_text, system)

        if not text:
            return _preview_full(fallback), fallback, "fallback"
        return _preview_full(text), text, raw
    except Exception as e:
        logger.warning("vibe copywriter failed (%s): %s", raw, e)
        return _preview_full(fallback), fallback, "fallback"


def _preview_full(full: str) -> str:
    full = full.strip()
    if len(full) <= 200:
        return full
    return full[:200].rstrip() + "…"
