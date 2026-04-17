import uuid

import stripe
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AffiliateClick, Order, Task
from app.schemas.payments import CreateCheckoutBody
from app.services import config_service

from .deps import DbSession

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.post("/create-checkout")
def create_checkout(db: DbSession, body: CreateCheckoutBody):
    try:
        tid = uuid.UUID(body.task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task_id")

    task = db.query(Task).filter(Task.id == tid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    settings = get_settings()
    secret = config_service.get("stripe_secret_key", default=settings.stripe_secret_key, db=db)
    frontend = config_service.get("frontend_url", default=settings.frontend_url, db=db)
    if not secret:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    stripe.api_key = secret

    amount = float(config_service.get("checkout_amount_usd", default="2.99", db=db) or "2.99")
    amount_cents = int(round(amount * 100))

    aff_id = None
    click = (
        db.query(AffiliateClick)
        .filter(
            AffiliateClick.user_id == task.user_id,
            AffiliateClick.converted_at.is_(None),
        )
        .order_by(AffiliateClick.clicked_at.desc())
        .first()
    )
    if click:
        aff_id = click.affiliate_id

    order = Order(
        task_id=task.id,
        user_id=task.user_id,
        amount=amount,
        currency="usd",
        status="PENDING",
        affiliate_id=aff_id,
    )
    db.add(order)
    db.flush()

    fe = str(frontend).rstrip("/")
    success = f"{fe}/result/{task.id}" "?session_id={CHECKOUT_SESSION_ID}"
    cancel = f"{fe}/result/{task.id}"

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": amount_cents,
                    "product_data": {"name": "Unlock Full Aura"},
                },
                "quantity": 1,
            }
        ],
        success_url=success,
        cancel_url=cancel,
        metadata={"task_id": str(task.id), "order_id": str(order.id)},
    )

    order.stripe_session_id = session.id
    db.commit()

    return {"checkout_url": session.url}
