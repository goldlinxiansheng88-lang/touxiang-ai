from typing import Any, Optional

from pydantic import BaseModel, Field


class ConfigPatchItem(BaseModel):
    key: str
    value: str
    value_type: Optional[str] = None


class ConfigBatchPatch(BaseModel):
    items: list[ConfigPatchItem] = Field(default_factory=list)


class ConnectionTestBody(BaseModel):
    """测试当前输入或已保存的配置是否连通；value 为空则从库/env 读取。"""

    key: str
    value: str | None = None
    related: dict[str, str] | None = None


class CreateAffiliateBody(BaseModel):
    name: str
    commission_rate: float = 0.30
    code: Optional[str] = None


class PayoutActionBody(BaseModel):
    status: str  # COMPLETED / REJECTED


class CreditTopupBody(BaseModel):
    public_id: str
    confirm_username: str
    credits: int = Field(ge=1, le=1_000_000)
    note: str | None = None
