import uuid
from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, HTTPException, Request

from app.config import get_settings
from app.models import Affiliate, AffiliateClick, Order, Task
from app.services import config_service
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

        task = db.query(Task).filter(Task.id == uuid.UUID(task_id)).first()
        if task:
            task.is_paid = True
        if order_id:
            order = db.query(Order).filter(Order.id == uuid.UUID(order_id)).first()
            if order:
                order.status = "PAID"
                order.paid_at = datetime.now(timezone.utc)

                if order.affiliate_id:
                    aff = db.query(Affiliate).filter(Affiliate.id == order.affiliate_id).first()
                    if aff:
                        rate = float(aff.commission_rate)
                        commission = float(order.amount) * rate
                        order.commission_earned = commission
                        aff.wallet_balance = float(aff.wallet_balance or 0) + commission
                        aff.total_earned = float(aff.total_earned or 0) + commission

                    now = datetime.now(timezone.utc)
                    for c in (
                        db.query(AffiliateClick)
                        .filter(
                            AffiliateClick.user_id == order.user_id,
                            AffiliateClick.affiliate_id == order.affiliate_id,
                            AffiliateClick.converted_at.is_(None),
                        )
                        .all()
                    ):
                        c.converted_at = now

        db.commit()
        return {"received": True}
    finally:
        db.close()
