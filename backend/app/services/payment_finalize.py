"""订单支付完成后的统一处理（Stripe / Lemon Squeezy / 管理员确认 USDT）。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import Affiliate, AffiliateClick, Order, Task


def finalize_order_paid(db: Session, order: Order) -> None:
    """将订单与关联任务标为已付，并结算分销佣金（幂等：已 PAID 则只补任务标记）。"""
    if order.status == "PAID":
        task = db.query(Task).filter(Task.id == order.task_id).first()
        if task and not task.is_paid:
            task.is_paid = True
        return

    task = db.query(Task).filter(Task.id == order.task_id).first()
    if task:
        task.is_paid = True

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


def finalize_order_paid_by_ids(db: Session, *, task_id: uuid.UUID, order_id: uuid.UUID) -> bool:
    """按 task_id + order_id 查找订单并完成支付；找不到订单返回 False。"""
    order = db.query(Order).filter(Order.id == order_id, Order.task_id == task_id).first()
    if not order:
        return False
    finalize_order_paid(db, order)
    return True
