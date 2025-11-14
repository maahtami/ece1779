from sqlalchemy.orm import Session
from app.models.transaction import Transaction, TransactionType
from app.services.inventory_service import adjust_stock

def create_transaction(db: Session, user_id: int, item_id: int, quantity: int, type_: TransactionType) -> Transaction:
    delta = quantity if type_ == TransactionType.in_ else -quantity
    item = adjust_stock(db, item_id, delta)
    tx = Transaction(user_id=user_id, item_id=item_id, quantity=quantity, type=type_)
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx