from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import CreditLedger, User


@dataclass(frozen=True)
class CreditCost:
    base: int
    background_remove_addon: int
    regenerate_discounted: bool

    @property
    def total(self) -> int:
        return int(self.base + self.background_remove_addon)


BASE_COST_BY_RESOLUTION: dict[int, int] = {
    512: 2,
    1024: 4,
    2048: 9,
    4096: 20,
}

BACKGROUND_REMOVE_ADDON = 2


def compute_generation_cost(
    *,
    resolution: int,
    remove_background: bool,
    is_regenerate: bool,
) -> CreditCost:
    if resolution not in BASE_COST_BY_RESOLUTION:
        raise HTTPException(status_code=400, detail=f"Unsupported resolution: {resolution}")
    base = int(BASE_COST_BY_RESOLUTION[resolution])
    addon = int(BACKGROUND_REMOVE_ADDON if remove_background else 0)
    if is_regenerate:
        # 重新生成：原价 50%（向上取整）。按“总价”打折更符合用户直觉。
        discounted = int(math.ceil((base + addon) * 0.5))
        # keep breakdown meaningful in logs
        return CreditCost(base=discounted, background_remove_addon=0, regenerate_discounted=True)
    return CreditCost(base=base, background_remove_addon=addon, regenerate_discounted=False)


def get_balance(db: Session, user_id) -> int:
    u = db.query(User).filter(User.id == user_id).first()
    return int(u.credits_balance) if u else 0


def _apply_delta(
    db: Session,
    *,
    user_id,
    delta: int,
    kind: str,
    meta: Optional[dict[str, Any]] = None,
    source_id: str | None = None,
) -> int:
    """
    Atomically update user's balance and write a ledger row.
    Returns new balance.
    """
    # Lock row to avoid concurrent negative balances.
    u = db.query(User).filter(User.id == user_id).with_for_update().first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    before = int(u.credits_balance or 0)
    after = before + int(delta)
    if after < 0:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    u.credits_balance = after
    db.add(
        CreditLedger(
            user_id=u.id,
            delta=int(delta),
            balance_after=int(after),
            kind=str(kind)[:50],
            source_id=(str(source_id)[:120] if source_id else None),
            meta=meta or None,
        )
    )
    db.flush()
    return after


def consume_for_task(
    db: Session,
    *,
    user_id,
    task_id: str,
    cost: int,
    meta: Optional[dict[str, Any]] = None,
) -> int:
    return _apply_delta(
        db,
        user_id=user_id,
        delta=-int(cost),
        kind="consume_generate",
        meta={"task_id": task_id, **(meta or {})},
    )


def grant_signup_bonus_once(db: Session, *, user_id) -> int:
    u = db.query(User).filter(User.id == user_id).with_for_update().first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if bool(u.signup_bonus_granted):
        return int(u.credits_balance or 0)
    u.signup_bonus_granted = True
    bonus = 5
    # Use internal helper to also write ledger.
    # We already hold a row lock; call _apply_delta via SQL-level lock bypass by updating directly.
    # Simpler: do it manually to avoid nested locking logic.
    before = int(u.credits_balance or 0)
    after = before + bonus
    u.credits_balance = after
    db.add(
        CreditLedger(
            user_id=u.id,
            delta=bonus,
            balance_after=after,
            kind="signup_bonus",
            source_id=None,
            meta=None,
        )
    )
    db.flush()
    return after


def ensure_credit_schema(db: Session) -> None:
    """
    Best-effort migrations for older DBs (project uses create_all + ALTER IF NOT EXISTS patterns).
    """
    # no-op: schema is managed in app.main lifespan using engine.begin() + ALTER TABLE.
    return
