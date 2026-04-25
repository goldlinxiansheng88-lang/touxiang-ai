from __future__ import annotations

import re
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User


def _norm_country(cc: str | None) -> str:
    cc = (cc or "").strip().upper()
    if not cc:
        return "ZZ"
    if not re.fullmatch(r"[A-Z]{2}", cc):
        return "ZZ"
    return cc


def _today_yyyymmdd(dt: datetime | None = None) -> str:
    d = dt or datetime.now(timezone.utc)
    return d.astimezone(timezone.utc).strftime("%Y%m%d")


def allocate_public_user_id(db: Session, *, created_at: datetime | None, country_code: str | None) -> str:
    """
    Allocate a unique public id: U{YYYYMMDD}{CC}{SEQ6}.

    Uses a per-day-per-country counter table with an atomic UPSERT.
    """
    day = _today_yyyymmdd(created_at)
    cc = _norm_country(country_code)
    row = db.execute(
        text(
            """
            INSERT INTO user_public_id_counters(day, country_code, seq)
            VALUES (:day, :cc, 1)
            ON CONFLICT (day, country_code)
            DO UPDATE SET seq = user_public_id_counters.seq + 1
            RETURNING seq
            """
        ),
        {"day": day, "cc": cc},
    ).first()
    seq = int(row[0]) if row else 1
    return f"U{day}{cc}{seq:06d}"


def ensure_public_user_id(
    db: Session,
    *,
    user: User,
    country_code: str | None = None,
) -> str:
    """
    Ensure user.public_id exists (best-effort).
    Writes to DB but does not commit.
    """
    if (user.public_id or "").strip():
        return str(user.public_id)

    # Prefer persisted signup_country when present
    cc = (user.signup_country or "").strip().upper() or country_code
    # created_at is server_default; for brand-new rows it may be None before refresh, so fallback to now.
    created = user.created_at if getattr(user, "created_at", None) else datetime.now(timezone.utc)

    # Retry on rare unique collisions
    for _ in range(3):
        pid = allocate_public_user_id(db, created_at=created, country_code=cc)
        user.public_id = pid[:32]
        try:
            db.flush()
            return pid
        except IntegrityError:
            db.rollback()
            continue
    # Last resort: fall back to time-derived id without counter (still bounded length)
    pid = f"U{_today_yyyymmdd(created)}{_norm_country(cc)}{int(datetime.now(timezone.utc).timestamp())%1_000_000:06d}"
    user.public_id = pid[:32]
    db.flush()
    return str(user.public_id)


def ensure_system_display_name(db: Session, *, user: User) -> str:
    """
    Ensure a short system username (<=16 chars) when the user hasn't set one.
    Format: Aura{MMDD}{CC}{SEQ4}
    Example: Aura0425CN0001
    """
    cur = (user.display_name or "").strip()
    if cur:
        return cur[:255]

    pid = (user.public_id or "").strip()
    if pid.startswith("U") and len(pid) >= 17:
        day = pid[1:9]  # YYYYMMDD
        cc = pid[9:11]  # CC
        seq = pid[-6:]  # SEQ6
        name = f"Aura{day[4:]}{cc}{seq[-4:]}"
    else:
        # fallback: Aura + last 12 of UUID hex
        raw = str(getattr(user, "id", "")).replace("-", "")
        name = "Aura" + (raw[-12:] if raw else "User")

    name = name[:16]
    user.display_name = name
    db.flush()
    return name

