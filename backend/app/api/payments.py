import uuid
from typing import Any, Literal

import httpx
import stripe
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AffiliateClick, Order, Task
from app.schemas.payments import CreateCheckoutBody
from app.services import config_service

from .deps import DbSession

router = APIRouter(prefix="/api/payments", tags=["payments"])

Provider = Literal["stripe", "creem", "lemon_squeezy", "usdt"]


def _stripe_configured(db: Session, settings) -> bool:
    sk = config_service.get("stripe_secret_key", default=settings.stripe_secret_key, db=db)
    return bool((sk or "").strip())


def _lemon_configured(db: Session) -> bool:
    api = (config_service.get("lemon_squeezy_api_key", default="", db=db) or "").strip()
    store = (config_service.get("lemon_squeezy_store_id", default="", db=db) or "").strip()
    variant = (config_service.get("lemon_squeezy_variant_id", default="", db=db) or "").strip()
    return bool(api and store and variant)


def _usdt_configured(db: Session) -> bool:
    addr = (config_service.get("usdt_receive_address", default="", db=db) or "").strip()
    return bool(addr)


def _creem_configured(db: Session) -> bool:
    api = (config_service.get("creem_api_key", default="", db=db) or "").strip()
    pid = (config_service.get("creem_product_id", default="", db=db) or "").strip()
    return bool(api and pid)


def payment_flags(db: Session, settings) -> dict[str, bool]:
    return {
        "stripe": _stripe_configured(db, settings),
        "creem": _creem_configured(db),
        "lemon_squeezy": _lemon_configured(db),
        "usdt": _usdt_configured(db),
    }


def _pick_default_provider(flags: dict[str, bool]) -> Provider | None:
    for k in ("stripe", "creem", "lemon_squeezy", "usdt"):
        if flags.get(k):
            return k  # type: ignore[return-value]
    return None


def _affiliate_id_for_task(db: Session, task: Task) -> uuid.UUID | None:
    click = (
        db.query(AffiliateClick)
        .filter(
            AffiliateClick.user_id == task.user_id,
            AffiliateClick.converted_at.is_(None),
        )
        .order_by(AffiliateClick.clicked_at.desc())
        .first()
    )
    return click.affiliate_id if click else None


def _create_pending_order(
    db: Session,
    *,
    task: Task,
    amount: float,
    currency: str,
    channel: Provider,
) -> Order:
    aff_id = _affiliate_id_for_task(db, task)
    order = Order(
        task_id=task.id,
        user_id=task.user_id,
        amount=amount,
        currency=currency,
        status="PENDING",
        affiliate_id=aff_id,
        payment_channel=channel,
    )
    db.add(order)
    db.flush()
    return order


@router.get("/methods")
def list_payment_methods(db: DbSession) -> dict[str, Any]:
    """公开：根据后台已填密钥/地址，返回当前可用的收款方式（不含密钥）。"""
    settings = get_settings()
    flags = payment_flags(db, settings)
    usd = config_service.get("checkout_amount_usd", default="2.99", db=db) or "2.99"
    usdt_amt = config_service.get("checkout_amount_usdt", default=usd, db=db) or usd
    net = (config_service.get("usdt_network", default="TRC20", db=db) or "TRC20").strip()
    return {
        "methods": [
            {"id": "stripe", "enabled": flags["stripe"], "label": "Stripe"},
            {"id": "creem", "enabled": flags["creem"], "label": "Creem"},
            {"id": "lemon_squeezy", "enabled": flags["lemon_squeezy"], "label": "Lemon Squeezy"},
            {"id": "usdt", "enabled": flags["usdt"], "label": "USDT"},
        ],
        "checkout_amount_usd": str(usd).strip(),
        "checkout_amount_usdt": str(usdt_amt).strip(),
        "usdt_network": net,
        "default_provider": _pick_default_provider(flags),
    }


@router.post("/create-checkout")
def create_checkout(db: DbSession, body: CreateCheckoutBody) -> dict[str, Any]:
    try:
        tid = uuid.UUID(body.task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task_id")

    task = db.query(Task).filter(Task.id == tid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    settings = get_settings()
    flags = payment_flags(db, settings)
    if not any(flags.values()):
        raise HTTPException(status_code=503, detail="No payment method configured")

    provider = body.provider
    if provider is None:
        provider = _pick_default_provider(flags)
    else:
        if not flags.get(provider):
            raise HTTPException(status_code=400, detail=f"Payment method not available: {provider}")

    if provider == "stripe":
        return _checkout_stripe(db, settings, task)
    if provider == "creem":
        return _checkout_creem(db, settings, task)
    if provider == "lemon_squeezy":
        return _checkout_lemon(db, settings, task)
    return _checkout_usdt(db, task)


def _checkout_stripe(db: Session, settings, task: Task) -> dict[str, Any]:
    secret = config_service.get("stripe_secret_key", default=settings.stripe_secret_key, db=db)
    frontend = config_service.get("frontend_url", default=settings.frontend_url, db=db)
    if not (secret or "").strip():
        raise HTTPException(status_code=503, detail="Stripe not configured")

    stripe.api_key = secret
    amount = float(config_service.get("checkout_amount_usd", default="2.99", db=db) or "2.99")
    amount_cents = int(round(amount * 100))

    order = _create_pending_order(db, task=task, amount=amount, currency="usd", channel="stripe")

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

    return {"provider": "stripe", "checkout_url": session.url}


def _checkout_creem(db: Session, settings, task: Task) -> dict[str, Any]:
    api_key = (config_service.get("creem_api_key", default="", db=db) or "").strip()
    product_id = (config_service.get("creem_product_id", default="", db=db) or "").strip()
    base = (
        config_service.get("creem_api_base_url", default="https://api.creem.io", db=db) or "https://api.creem.io"
    ).rstrip("/")
    if not (api_key and product_id):
        raise HTTPException(status_code=503, detail="Creem not configured")

    frontend = config_service.get("frontend_url", default=settings.frontend_url, db=db)
    amount = float(config_service.get("checkout_amount_usd", default="2.99", db=db) or "2.99")

    order = _create_pending_order(db, task=task, amount=amount, currency="usd", channel="creem")
    fe = str(frontend).rstrip("/")
    success_url = f"{fe}/result/{task.id}"

    payload: dict[str, Any] = {
        "product_id": product_id,
        "request_id": str(order.id),
        "success_url": success_url,
        "metadata": {
            "task_id": str(task.id),
            "order_id": str(order.id),
        },
    }

    try:
        r = httpx.post(
            f"{base}/v1/checkouts",
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=30.0,
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Creem request failed: {e!s}") from e

    if r.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"Creem error HTTP {r.status_code}: {r.text[:800]}",
        )

    try:
        data = r.json()
    except ValueError:
        raise HTTPException(status_code=502, detail="Creem returned invalid JSON")

    checkout_url = (data.get("checkout_url") or "").strip() if isinstance(data, dict) else ""
    if not checkout_url:
        raise HTTPException(status_code=502, detail="Creem did not return checkout_url")

    db.commit()
    return {"provider": "creem", "checkout_url": checkout_url}


def _checkout_lemon(db: Session, settings, task: Task) -> dict[str, Any]:
    api_key = (config_service.get("lemon_squeezy_api_key", default="", db=db) or "").strip()
    store_id = (config_service.get("lemon_squeezy_store_id", default="", db=db) or "").strip()
    variant_id = (config_service.get("lemon_squeezy_variant_id", default="", db=db) or "").strip()
    if not (api_key and store_id and variant_id):
        raise HTTPException(status_code=503, detail="Lemon Squeezy not configured")

    frontend = config_service.get("frontend_url", default=settings.frontend_url, db=db)
    amount = float(config_service.get("checkout_amount_usd", default="2.99", db=db) or "2.99")
    amount_cents = int(round(amount * 100))

    order = _create_pending_order(db, task=task, amount=amount, currency="usd", channel="lemon_squeezy")

    fe = str(frontend).rstrip("/")
    redirect_url = f"{fe}/result/{task.id}"

    payload = {
        "data": {
            "type": "checkouts",
            "attributes": {
                "custom_price": amount_cents,
                "product_options": {
                    "name": "Unlock Full Aura",
                    "redirect_url": redirect_url,
                },
                "checkout_data": {
                    "custom": {
                        "task_id": str(task.id),
                        "order_id": str(order.id),
                    }
                },
                "preview": False,
            },
            "relationships": {
                "store": {"data": {"type": "stores", "id": str(store_id)}},
                "variant": {"data": {"type": "variants", "id": str(variant_id)}},
            },
        }
    }

    try:
        r = httpx.post(
            "https://api.lemonsqueezy.com/v1/checkouts",
            headers={
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/vnd.api+json",
                "Authorization": f"Bearer {api_key}",
            },
            json=payload,
            timeout=30.0,
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Lemon Squeezy request failed: {e!s}") from e

    if r.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"Lemon Squeezy error HTTP {r.status_code}: {r.text[:800]}",
        )

    data = r.json()
    attrs = (data.get("data") or {}).get("attributes") or {}
    url = attrs.get("url")
    if not url:
        raise HTTPException(status_code=502, detail="Lemon Squeezy did not return checkout URL")

    db.commit()
    return {"provider": "lemon_squeezy", "checkout_url": url}


def _checkout_usdt(db: Session, task: Task) -> dict[str, Any]:
    addr = (config_service.get("usdt_receive_address", default="", db=db) or "").strip()
    if not addr:
        raise HTTPException(status_code=503, detail="USDT address not configured")

    usd = config_service.get("checkout_amount_usd", default="2.99", db=db) or "2.99"
    usdt_amt = config_service.get("checkout_amount_usdt", default=usd, db=db) or usd
    network = (config_service.get("usdt_network", default="TRC20", db=db) or "TRC20").strip()

    try:
        amount_usd = float(usd)
        amount_usdt = float(usdt_amt)
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid amount in configuration")

    order = _create_pending_order(db, task=task, amount=amount_usd, currency="usd", channel="usdt")
    db.commit()

    return {
        "provider": "usdt",
        "checkout_url": None,
        "usdt": {
            "order_id": str(order.id),
            "address": addr,
            "network": network,
            "amount": f"{amount_usdt:.6f}".rstrip("0").rstrip("."),
        },
    }
