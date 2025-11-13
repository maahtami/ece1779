from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate
from app.routers.dependencies import get_current_user, get_current_manager_user
from app.services.inventory_service import create_item, update_item

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/", response_model=ItemOut)
def create_inventory_item(
    item_in: ItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_manager_user),
):
    existing = db.query(Item).filter(Item.name == item_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Item name already exists")
    return create_item(
        db=db,
        name=item_in.name,
        description=item_in.description,
        quantity=item_in.quantity,
        low_stock_threshold=item_in.low_stock_threshold,
    )


@router.get("/", response_model=list[ItemOut])
def list_items(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Item).all()


@router.get("/{item_id}", response_model=ItemOut)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = db.query(Item).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=ItemOut)
def update_item_endpoint(
    item_id: int,
    item_in: ItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_manager_user),
):
    item = db.query(Item).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return update_item(
        db,
        item,
        name=item_in.name,
        description=item_in.description,
        quantity=item_in.quantity,
        low_stock_threshold=item_in.low_stock_threshold,
    )


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_manager_user),
):
    item = db.query(Item).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return