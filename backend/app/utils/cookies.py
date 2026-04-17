from typing import Optional

from fastapi import Request, Response

AFF_COOKIE = "aff_ref"
DEVICE_COOKIE = "device_id"
AFF_MAX_AGE = 30 * 24 * 60 * 60  # 30 days


def get_device_id(request: Request) -> Optional[str]:
    return request.cookies.get(DEVICE_COOKIE)


def get_aff_ref(request: Request) -> Optional[str]:
    return request.cookies.get(AFF_COOKIE)


def set_cookies(
    response: Response,
    *,
    device_id: Optional[str] = None,
    aff_ref: Optional[str] = None,
) -> None:
    if device_id:
        response.set_cookie(
            key=DEVICE_COOKIE,
            value=device_id,
            max_age=AFF_MAX_AGE,
            httponly=True,
            samesite="lax",
        )
    if aff_ref:
        response.set_cookie(
            key=AFF_COOKIE,
            value=aff_ref,
            max_age=AFF_MAX_AGE,
            httponly=False,
            samesite="lax",
        )
