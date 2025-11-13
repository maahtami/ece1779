from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    description: str | None = None
    low_stock_threshold: int = 5


class ItemCreate(ItemBase):
    quantity: int = 0


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    quantity: int | None = None
    low_stock_threshold: int | None = None


class ItemOut(ItemBase):
    id: int
    quantity: int
    is_low_stock: bool

    class Config:
        orm_mode = True