# app/routers/inventory.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.item import ItemCreate, ItemUpdate, ItemRead
from app.models.item import Item
from app.routers.dependencies import get_current_staff_or_manager

router = APIRouter(prefix="/items", tags=["items"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ItemRead)
def create_item(
    item_in: ItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_staff_or_manager),
):
    existing = db.query(Item).filter(Item.sku == item_in.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    item = Item(**item_in.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/", response_model=list[ItemRead])
def list_items(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_staff_or_manager),
):
    return db.query(Item).all()

@router.get("/{item_id}", response_model=ItemRead)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_staff_or_manager),
):
    item = db.query(Item).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=ItemRead)
def update_item(
    item_id: int,
    item_in: ItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_staff_or_manager),
):
    item = db.query(Item).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in item_in.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_staff_or_manager),
):
    item = db.query(Item).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()