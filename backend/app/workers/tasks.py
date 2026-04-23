import uuid
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import httpx
from PIL import Image, ImageFilter

from app.database import SessionLocal
from app.models import Task
from app.services.aura_prompt_builder import build_generation_prompts
from app.services.aura_vibe_copywriter import generate_vibe_copy
from app.services.fal_flux_img2img import DEFAULT_MODEL_ID, first_image_url, run_flux_img2img
from app.services.storage_s3 import load_s3_config, put_bytes
from app.workers.celery_app import celery_app


def _blur_upload_path(input_image_url: str) -> Path | None:
    path = urlparse(input_image_url).path
    if "/static/uploads/" not in path:
        return None
    local = Path(__file__).resolve().parent.parent.parent / "uploads" / Path(path).name
    return local if local.exists() else None


def _download_image(url: str, dest: Path) -> None:
    with httpx.Client(timeout=120.0, follow_redirects=True) as client:
        r = client.get(url)
        r.raise_for_status()
        dest.write_bytes(r.content)


def process_aura_task_inline(task_id: str) -> None:
    """
    Fallback execution path when Celery/Redis is unavailable.
    Runs the same logic as the Celery task in-process (use with care on small deployments).
    """
    _process_aura_task(task_id)


def _process_aura_task(task_id: str, *, _celery_retry=None, _celery_self=None) -> None:
    db = SessionLocal()
    try:
        tid = uuid.UUID(task_id)
        task = db.query(Task).filter(Task.id == tid).first()
        if not task:
            return
        task.status = "PROCESSING"
        db.commit()

        prompts = build_generation_prompts(
            scene=task.scene,
            style=task.style,
            aspect_ratio=task.aspect_ratio or "auto",
        )

        from app.config import get_settings
        from app.services import config_service

        settings = get_settings()
        fal_key = (config_service.get("fal_key", default="", db=db) or "").strip()
        model_id = (
            config_service.get("flux_img2img_model_id", default=DEFAULT_MODEL_ID, db=db) or DEFAULT_MODEL_ID
        ).strip()

        gen_meta = {
            "positive_prompt": prompts.positive,
            "negative_prompt": prompts.negative,
            "parts": prompts.parts,
            "model_id": model_id,
        }

        blurred_url = task.input_image_url
        result_url = task.input_image_url
        s3cfg = load_s3_config(db=db)

        if fal_key:
            raw = run_flux_img2img(
                fal_key=fal_key,
                model_id=model_id,
                image_url=task.input_image_url,
                positive_prompt=prompts.positive,
                negative_prompt=prompts.negative,
            )
            remote_out = first_image_url(raw)
            upload_dir = Path(__file__).resolve().parent.parent.parent / "uploads"
            upload_dir.mkdir(parents=True, exist_ok=True)
            out_name = f"flux_{tid}.jpg"
            out_path = upload_dir / out_name
            _download_image(remote_out, out_path)

            if s3cfg:
                result_url = put_bytes(
                    cfg=s3cfg,
                    key=f"outputs/result/{out_name}",
                    data=out_path.read_bytes(),
                    content_type="image/jpeg",
                    cache_control="public, max-age=31536000, immutable",
                )
            else:
                public_base = str(
                    config_service.get("public_base_url", default=settings.public_base_url, db=db)
                ).rstrip("/")
                result_url = f"{public_base}/static/uploads/{out_name}"

            img = Image.open(out_path).convert("RGB")
            blurred = img.filter(ImageFilter.GaussianBlur(radius=20))
            buf = BytesIO()
            blurred.save(buf, format="JPEG", quality=85)
            buf.seek(0)
            blur_name = f"blur_flux_{tid}.jpg"
            blur_path = upload_dir / blur_name
            blur_path.write_bytes(buf.getvalue())
            if s3cfg:
                blurred_url = put_bytes(
                    cfg=s3cfg,
                    key=f"outputs/blur/{blur_name}",
                    data=blur_path.read_bytes(),
                    content_type="image/jpeg",
                    cache_control="public, max-age=31536000, immutable",
                )
            else:
                blurred_url = f"{public_base}/static/uploads/{blur_name}"

            gen_meta["provider"] = "fal"
            gen_meta["fal_output_url"] = remote_out[:500]
        else:
            gen_meta["provider"] = "placeholder"
            try:
                local = _blur_upload_path(task.input_image_url)
                if local:
                    img = Image.open(local).convert("RGB")
                    blurred = img.filter(ImageFilter.GaussianBlur(radius=20))
                    buf = BytesIO()
                    blurred.save(buf, format="JPEG", quality=85)
                    buf.seek(0)
                    out_name = f"blur_{local.stem}.jpg"
                    out_path = local.parent / out_name
                    out_path.write_bytes(buf.getvalue())
                    base = str(
                        config_service.get("public_base_url", default=settings.public_base_url, db=db)
                    ).rstrip("/")
                    blurred_url = f"{base}/static/uploads/{out_name}"
            except Exception:
                pass

        preview_text, full_vibe, vibe_llm = generate_vibe_copy(scene=task.scene, style=task.style, db=db)

        task.result_json = {
            **(task.result_json or {}),
            "generation": gen_meta,
            "vibe": full_vibe,
            "preview": preview_text,
            "full": full_vibe,
            "vibe_llm": vibe_llm,
            "aspect_ratio": task.aspect_ratio or "auto",
        }
        task.result_image_url = result_url
        task.blurred_image_url = blurred_url
        task.status = "COMPLETED"
        db.commit()
    except Exception as e:
        db.rollback()
        if _celery_self is not None and _celery_retry is not None:
            if _celery_self.request.retries >= _celery_self.max_retries:
                t2 = db.query(Task).filter(Task.id == uuid.UUID(task_id)).first()
                if t2:
                    t2.status = "FAILED"
                    t2.error_message = str(e)
                    t2.retry_count = (t2.retry_count or 0) + 1
                    db.commit()
                raise
            raise _celery_retry(exc=e, countdown=60 * (2 ** _celery_self.request.retries)) from e
        t2 = db.query(Task).filter(Task.id == uuid.UUID(task_id)).first()
        if t2:
            t2.status = "FAILED"
            t2.error_message = str(e)
            t2.retry_count = (t2.retry_count or 0) + 1
            db.commit()
        raise
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def process_aura_task(self, task_id: str):
    _process_aura_task(task_id, _celery_retry=self.retry, _celery_self=self)
