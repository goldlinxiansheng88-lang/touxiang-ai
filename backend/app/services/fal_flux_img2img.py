"""fal.ai FLUX.1 img2img（官方 endpoint：fal-ai/flux/dev/image-to-image）。"""

from __future__ import annotations

import os
from typing import Any

DEFAULT_MODEL_ID = "fal-ai/flux/dev/image-to-image"


def _merge_prompts(positive: str, negative: str) -> str:
    p = (positive or "").strip()
    n = (negative or "").strip()
    if not n:
        return p
    return f"{p}. Avoid, do not render: {n}"


def run_flux_img2img(
    *,
    fal_key: str,
    model_id: str,
    image_url: str,
    positive_prompt: str,
    negative_prompt: str,
    strength: float = 0.9,
    num_inference_steps: int = 32,
    guidance_scale: float = 3.5,
) -> dict[str, Any]:
    """调用 fal `subscribe`，返回模型 JSON（含 images[].url）。"""
    import fal_client

    if not fal_key.strip():
        raise ValueError("fal_key is empty")
    mid = (model_id or "").strip() or DEFAULT_MODEL_ID
    prompt = _merge_prompts(positive_prompt, negative_prompt)

    arguments: dict[str, Any] = {
        "image_url": image_url.strip(),
        "prompt": prompt,
        "strength": strength,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
        "num_images": 1,
        "enable_safety_checker": True,
        "output_format": "jpeg",
    }

    prev = os.environ.get("FAL_KEY")
    try:
        os.environ["FAL_KEY"] = fal_key.strip()
        return fal_client.subscribe(mid, arguments=arguments)
    finally:
        if prev is None:
            os.environ.pop("FAL_KEY", None)
        else:
            os.environ["FAL_KEY"] = prev


def first_image_url(result: Any) -> str:
    """从 subscribe 返回结构中取出第一张图 URL。"""
    if not isinstance(result, dict):
        raise ValueError("unexpected fal response type")
    imgs = result.get("images")
    if imgs is None and isinstance(result.get("data"), dict):
        imgs = result["data"].get("images")
    if not imgs or not isinstance(imgs, list):
        raise ValueError(
            f"fal response missing images; keys={list(result.keys()) if isinstance(result, dict) else type(result)}"
        )
    first = imgs[0]
    if isinstance(first, dict) and first.get("url"):
        return str(first["url"]).strip()
    if isinstance(first, str):
        return first.strip()
    raise ValueError("fal images[0] has no url")
