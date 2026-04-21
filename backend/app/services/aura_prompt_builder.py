from __future__ import annotations

from dataclasses import dataclass

from app.data.static_config import STYLE_PARAMS


@dataclass(frozen=True)
class GenerationPrompts:
    positive: str
    negative: str
    parts: dict[str, str]


_IDENTITY_HARD = (
    "same person as the reference image, preserve facial identity, face structure, skin tone and expression, "
    "keep age and gender, keep hairstyle length, do not swap face"
)

# Scene prompts should be light-touch (avoid fighting identity).
_SCENE_PROMPTS: dict[str, str] = {
    "AVATAR": "portrait photo, head-and-shoulders framing, clean background, sharp eyes",
    "DAILY": "lifestyle portrait, candid but clear face, natural light",
    "FASHION": "fashion portrait, editorial lighting, full or three-quarter body if possible, clear face",
    "POSTER": "poster-style portrait, bold composition, clean readable subject",
    "TRAVEL": "travel portrait, cinematic daylight, subject clearly separated from background",
    "WALLPAPER": "wallpaper-ready portrait, subject anchored, background simplified",
}

# Global negative prompt: reduces common img2img failures.
_NEGATIVE_GLOBAL = (
    "worst quality, low quality, lowres, blurry, out of focus, jpeg artifacts, watermark, text, logo, "
    "deformed face, asymmetrical face, bad eyes, crossed eyes, extra teeth, bad hands, extra fingers, "
    "extra limbs, missing limbs, duplicate person, multiple people, child, nude, gore"
)


def build_generation_prompts(*, scene: str, style: str, aspect_ratio: str = "auto") -> GenerationPrompts:
    style = (style or "").strip()
    scene = (scene or "").strip()
    ar = (aspect_ratio or "auto").strip()

    style_params = STYLE_PARAMS.get(style) or {}
    style_prompt = str(style_params.get("prompt") or "").strip()
    if not style_prompt:
        style_prompt = "portrait style transfer, preserve identity from reference, natural skin, clean background"

    scene_prompt = _SCENE_PROMPTS.get(scene, "portrait photo, clear face, subject-centered framing")
    ar_hint = "" if ar == "auto" else f"aspect ratio {ar}"

    # Layered prompt: identity first, then scene guardrails, then style.
    parts = {
        "identity": _IDENTITY_HARD,
        "scene": scene_prompt,
        "style": style_prompt,
        "aspect_ratio": ar_hint,
    }
    positive = ", ".join([p for p in parts.values() if p])

    return GenerationPrompts(
        positive=positive,
        negative=_NEGATIVE_GLOBAL,
        parts=parts,
    )

