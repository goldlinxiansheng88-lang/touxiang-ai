import hashlib
import hmac
import json
import uuid

import stripe
from fastapi import APIRouter, HTTPException, Request

from app.config import get_settings
from app.models import Order
from app.services import config_service
from app.services.payment_finalize import finalize_order_paid
from app.database import SessionLocal

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    settings = get_settings()

    db = SessionLocal()
    try:
        wh_secret = config_service.get(
            "stripe_webhook_secret", default=settings.stripe_webhook_secret, db=db
        )
        if not wh_secret:
            raise HTTPException(status_code=503, detail="Webhook secret not configured")

        try:
            event = stripe.Webhook.construct_event(payload, sig, wh_secret)
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid payload") from e
        except Exception as e:
            if type(e).__name__ == "SignatureVerificationError":
                raise HTTPException(status_code=400, detail="Invalid signature") from e
            raise

        if event["type"] != "checkout.session.completed":
            return {"received": True}

        session = event["data"]["object"]
        meta = session.get("metadata") or {}
        task_id = meta.get("task_id")
        order_id = meta.get("order_id")

        if not task_id:
            return {"received": True}

        tid = uuid.UUID(task_id)
        if order_id:
            order = db.query(Order).filter(Order.id == uuid.UUID(order_id)).first()
            if order:
                finalize_order_paid(db, order)
            else:
                task = db.query(Task).filter(Task.id == tid).first()
                if task:
                    task.is_paid = True
        else:
            task = db.query(Task).filter(Task.id == tid).first()
            if task:
                task.is_paid = True

        db.commit()
        return {"received": True}
    finally:
        db.close()


@router.post("/lemon-squeezy")
async def lemon_squeezy_webhook(request: Request):
    payload = await request.body()
    sig = (request.headers.get("X-Signature") or "").strip()
    db = SessionLocal()
    try:
        secret = (config_service.get("lemon_squeezy_webhook_secret", default="", db=db) or "").strip()
        if not secret:
            raise HTTPException(status_code=503, detail="Lemon Squeezy webhook secret not configured")
        expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            raise HTTPException(status_code=400, detail="Invalid signature")

        body = json.loads(payload.decode("utf-8"))
        meta = body.get("meta") or {}
        custom = meta.get("custom_data") or {}
        task_id = custom.get("task_id")
        order_id = custom.get("order_id")
        data_obj = body.get("data") or {}
        attrs = data_obj.get("attributes") or {}
        if (attrs.get("status") or "").lower() != "paid":
            return {"received": True}
        if not task_id or not order_id:
            return {"received": True}
        try:
            tid = uuid.UUID(str(task_id))
            oid = uuid.UUID(str(order_id))
        except ValueError:
            return {"received": True}

        order = db.query(Order).filter(Order.id == oid, Order.task_id == tid).first()
        if order:
            finalize_order_paid(db, order)
        db.commit()
        return {"received": True}
    finally:
        db.close()
