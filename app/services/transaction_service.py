from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.transaction import Transaction
from app.services.inventory_service import recalc_low_stock


class InsufficientStockError(Exception):
    pass


def apply_stock_change(db: Session, item: Item, type: str, quantity: int, user_id: int) -> Transaction:
    if type not in ("in", "out"):
        raise ValueError("Transaction type must be 'in' or 'out'")

    if quantity <= 0:
        raise ValueError("Quantity must be > 0")

    if type == "out" and item.quantity < quantity:
        raise InsufficientStockError("Not enough stock")

    if type == "in":
        item.quantity += quantity
    else:
        item.quantity -= quantity

    recalc_low_stock(item)

    tx = Transaction(
        item_id=item.id,
        user_id=user_id,
        type=type,
        quantity=quantity,
    )

    db.add(tx)
    db.add(item)
    db.commit()
    db.refresh(tx)

    # Hook for real-time/notification integration:
    #   here you could publish an event "stock.changed" or "low_stock.triggered"
    return tx