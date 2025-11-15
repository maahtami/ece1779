from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: str | None = None
    quantity: int

class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    sku: str
    quantity: int = 0
    low_stock_threshold: int = 5
    price: float = 0.0

class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    quantity: int | None = None
    low_stock_threshold: int | None = None
    price: float | None = None

class ItemRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    sku: str
    quantity: int
    low_stock_threshold: int
    price: float

    class Config:
        from_attributes = True   # Pydantic v2 replacement for orm_mode