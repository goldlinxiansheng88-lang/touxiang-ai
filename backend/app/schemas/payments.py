from pydantic import BaseModel


class CreateCheckoutBody(BaseModel):
    task_id: str
