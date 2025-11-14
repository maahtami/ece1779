# app/services/inventory_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.item import Item
from app.services.notifications import notify_low_stock

def adjust_stock(db: Session, item_id: int, delta: int) -> Item:
    item = db.query(Item).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    new_qty = item.quantity + delta
    if new_qty < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    item.quantity = new_qty
    db.commit()
    db.refresh(item)

    if item.quantity <= item.low_stock_threshold:
        notify_low_stock(item)  # hook for real-time + notification

    return item