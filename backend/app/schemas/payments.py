from typing import Literal

from pydantic import BaseModel


class CreateCheckoutBody(BaseModel):
    task_id: str
    provider: Literal["stripe", "creem", "lemon_squeezy", "usdt"] | None = None
