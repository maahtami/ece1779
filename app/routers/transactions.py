from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.item import Item
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionOut
from app.routers.dependencies import get_current_user
from app.services.transaction_service import apply_stock_change, InsufficientStockError

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionOut)
def create_transaction(
    tx_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = db.query(Item).get(tx_in.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    try:
        tx = apply_stock_change(
            db=db,
            item=item,
            type=tx_in.type,
            quantity=tx_in.quantity,
            user_id=current_user.id,
        )
    except InsufficientStockError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return tx


@router.get("/", response_model=list[TransactionOut])
def list_transactions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Transaction).order_by(Transaction.created_at.desc()).all()