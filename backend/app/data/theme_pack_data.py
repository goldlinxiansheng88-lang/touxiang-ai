"""主题包风格：由 frontend/src/data/themePacks.catalog.json 单一数据源生成 STYLES / STYLE_PARAMS。"""

from __future__ import annotations

import json
from pathlib import Path

_CATALOG_PATH = Path(__file__).resolve().parents[3] / "frontend" / "src" / "data" / "themePacks.catalog.json"


def _load_catalog() -> dict:
    if not _CATALOG_PATH.is_file():
        raise FileNotFoundError(
            f"Theme pack catalog missing: {_CATALOG_PATH}. "
            "Run: python scripts/build_theme_packs_catalog.py"
        )
    return json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))


def build_theme_pack_styles() -> list[dict[str, str]]:
    doc = _load_catalog()
    packs: dict[str, list[dict]] = doc["packs"]
    thumbs: list[str] = list(doc.get("thumbs") or [])
    rows: list[dict[str, str]] = []
    for code, items in packs.items():
        for i, item in enumerate(items, start=1):
            sid = f"tp_{code}_{i:02d}"
            url = (item.get("image") or "").strip()
            if not url and thumbs:
                url = thumbs[int(item.get("thumb", 0)) % len(thumbs)]
            if not url:
                raise ValueError(f"Style {sid} missing image URL in catalog")
            rows.append(
                {
                    "id": sid,
                    "display_name": str(item["nameEn"]),
                    "subtitle": str(item["subEn"]),
                    "social_proof": str(item["proof"]),
                    "thumbnail_url": url,
                }
            )
    return rows


def _lora_for_code(code: str) -> str:
    """按大类给占位 LoRA 权重（与旧版一致为占位；真生成管线可再细分）。"""
    if code in ("co", "lo"):
        return "DarkRomance:0.35"
    if code in ("ca", "an", "jo"):
        return "PixarStyle:0.4"
    if code in ("re", "mo"):
        return "PolaroidVibe:0.35"
    if code in ("ar",):
        return "OilPainting:0.45"
    if code in ("ga",):
        return "ShonenStyle:0.4"
    if code in ("li", "tr"):
        return "CottagecoreV2:0.3"
    if code in ("st", "dr"):
        return "Holographic:0.35"
    if code in ("sp",):
        return "ShonenStyle:0.45"
    return "GhibliBackground:0.35"


# 与 catalog 内单条 prompt 拼接：统一强调参考图身份、构图与画质（情侣/单人皆适用）
_THEME_PROMPT_TAIL = (
    ", same person as the reference image, preserve facial identity and key pose, "
    "portrait-led composition, subject-centered framing, background simplified and not distracting, "
    "subject clearly separated from background, natural skin"
)


def build_theme_pack_style_params() -> dict[str, dict[str, str]]:
    doc = _load_catalog()
    packs: dict[str, list[dict]] = doc["packs"]
    out: dict[str, dict[str, str]] = {}
    for code, items in packs.items():
        for i, item in enumerate(items, start=1):
            sid = f"tp_{code}_{i:02d}"
            prompt = str(item["prompt"]).strip()
            out[sid] = {
                "prompt": f"{prompt}{_THEME_PROMPT_TAIL}",
                "lora": _lora_for_code(code),
                "color": "scene-appropriate grade",
            }
    return out


THEME_PACK_STYLES: list[dict[str, str]] = build_theme_pack_styles()
THEME_PACK_STYLE_PARAMS: dict[str, dict[str, str]] = build_theme_pack_style_params()
