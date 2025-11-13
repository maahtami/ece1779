from sqlalchemy.orm import Session

from app.models.item import Item
from app.core.config import settings


def recalc_low_stock(item: Item) -> None:
    threshold = item.low_stock_threshold or settings.LOW_STOCK_THRESHOLD
    item.is_low_stock = item.quantity <= threshold


def create_item(db: Session, name: str, description: str | None, quantity: int, low_stock_threshold: int) -> Item:
    item = Item(
        name=name,
        description=description,
        quantity=quantity,
        low_stock_threshold=low_stock_threshold,
    )
    recalc_low_stock(item)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, item: Item, **fields) -> Item:
    for key, value in fields.items():
        if value is not None:
            setattr(item, key, value)
    recalc_low_stock(item)
    db.commit()
    db.refresh(item)
    return item