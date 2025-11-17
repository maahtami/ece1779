from sqlalchemy.orm import Session
from app.models.item import Item
from app.models.transaction import Transaction, TransactionType
from enum import Enum

class TransactionType(str, Enum):
    IN = "in"
    OUT = "out"
class InsufficientStockError(Exception):
    """Raised when stock is insufficient for an outbound transaction."""
    pass

def apply_stock_change(
    db: Session,
    item: Item,
    type: str,
    quantity: int,
    user_id: int,
) -> Transaction:
    """
    Apply a stock change (in or out) and create a transaction record.
    """
    # Validate type
    if type not in ("in", "out"):
        raise ValueError(f"Invalid transaction type: {type}. Must be 'in' or 'out'.")

    # Convert string type to enum
    type_enum = TransactionType.IN if type == "in" else TransactionType.OUT

    # Calculate delta
    delta = quantity if type_enum == TransactionType.IN else -quantity

    # Check stock for outbound
    if delta < 0 and item.quantity + delta < 0:
        raise InsufficientStockError(
            f"Insufficient stock for item {item.sku}. "
            f"Available: {item.quantity}, Requested: {quantity}"
        )

    # Update stock
    item.quantity += delta
    db.commit()
    db.refresh(item)

    # Create transaction record
    tx = Transaction(
        user_id=user_id,
        item_id=item.id,
        quantity=quantity,
        type=type_enum.value,  # Send string matching DB constraint
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    # Check low stock
    is_low_stock = item.quantity <= item.low_stock_threshold

    return tx, is_low_stock
