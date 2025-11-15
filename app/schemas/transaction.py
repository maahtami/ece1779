from datetime import datetime
from pydantic import BaseModel


class TransactionBase(BaseModel):
    item_id: int
    type: str  # "in" or "out"
    quantity: int


class TransactionCreate(TransactionBase):
    pass


class TransactionOut(TransactionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True