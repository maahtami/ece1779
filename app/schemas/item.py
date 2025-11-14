from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: str | None = None
    quantity: int

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    quantity: int | None = None

class ItemOut(ItemBase):
    id: int

    class Config:
        from_attributes = True   # Pydantic v2 replacement for orm_mode