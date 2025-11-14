from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: str | None = None
    sku: str
    quantity: int
    low_stock_threshold: int = 5
    price: float = 0.0

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    quantity: int | None = None
    low_stock_threshold: int | None = None
    price: float | None = None

class ItemRead(ItemBase):
    id: int

    class Config:
        from_attributes = True