import uuid
from io import BytesIO

from PIL import Image, ImageFilter

from app.database import SessionLocal
from app.models import Task
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def process_aura_task(self, task_id: str):
    db = SessionLocal()
    try:
        tid = uuid.UUID(task_id)
        task = db.query(Task).filter(Task.id == tid).first()
        if not task:
            return
        task.status = "PROCESSING"
        db.commit()

        # Dev placeholder: build blurred thumb from local upload if path resolvable
        blurred_url = task.input_image_url
        result_url = task.input_image_url
        try:
            from pathlib import Path
            from urllib.parse import urlparse

            path = urlparse(task.input_image_url).path
            if "/static/uploads/" in path:
                local = Path(__file__).resolve().parent.parent.parent / "uploads" / Path(path).name
                if local.exists():
                    img = Image.open(local).convert("RGB")
                    blurred = img.filter(ImageFilter.GaussianBlur(radius=20))
                    buf = BytesIO()
                    blurred.save(buf, format="JPEG", quality=85)
                    buf.seek(0)
                    out_name = f"blur_{local.stem}.jpg"
                    out_dir = local.parent
                    out_path = out_dir / out_name
                    out_path.write_bytes(buf.getvalue())
                    from app.config import get_settings
                    from app.services import config_service

                    settings = get_settings()
                    base = str(
                        config_service.get("public_base_url", default=settings.public_base_url, db=db)
                    ).rstrip("/")
                    blurred_url = f"{base}/static/uploads/{out_name}"
        except Exception:
            pass

        task.result_json = {
            "vibe": "Your aura whispers of quiet mornings and untold stories.",
            "preview": "Your aura whispers of quiet mornings...",
            "full": "Your aura whispers of quiet mornings and untold stories. "
            "Soft light gathers where curiosity lingers.",
        }
        task.result_image_url = result_url
        task.blurred_image_url = blurred_url
        task.status = "COMPLETED"
        db.commit()
    except Exception as e:
        db.rollback()
        if self.request.retries >= self.max_retries:
            t2 = db.query(Task).filter(Task.id == uuid.UUID(task_id)).first()
            if t2:
                t2.status = "FAILED"
                t2.error_message = str(e)
                t2.retry_count = (t2.retry_count or 0) + 1
                db.commit()
            raise
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries)) from e
    finally:
        db.close()
