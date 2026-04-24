"""fal.ai background removal (rembg)."""

from __future__ import annotations

import os
from typing import Any


DEFAULT_MODEL_ID = "fal-ai/imageutils/rembg"


def run_rembg(*, fal_key: str, image_url: str, model_id: str = DEFAULT_MODEL_ID) -> dict[str, Any]:
    import fal_client

    if not fal_key.strip():
        raise ValueError("fal_key is empty")
    mid = (model_id or "").strip() or DEFAULT_MODEL_ID
    arguments: dict[str, Any] = {"image_url": image_url.strip()}

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
    if not isinstance(result, dict):
        raise ValueError("unexpected fal response type")
    img = result.get("image")
    if isinstance(img, dict) and img.get("url"):
        return str(img["url"]).strip()
    data = result.get("data")
    if isinstance(data, dict):
        img = data.get("image")
        if isinstance(img, dict) and img.get("url"):
            return str(img["url"]).strip()
    raise ValueError("fal rembg response missing image.url")

