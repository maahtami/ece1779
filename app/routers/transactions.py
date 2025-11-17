from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.item import Item
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionOut
from app.routers.dependencies import get_current_user
from app.services.transaction_service import apply_stock_change, InsufficientStockError
from app.services.websocket_manager import manager
import requests, os

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionOut)
async def create_transaction(
    tx_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = db.query(Item).get(tx_in.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    try:
        tx, is_low_stock = apply_stock_change(
            db=db,
            item=item,
            type=tx_in.type,
            quantity=tx_in.quantity,
            user_id=current_user.id,
        )
    except InsufficientStockError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    
    # Broadcast transaction creation
    await manager.broadcast({
        "type": "transaction_created",
        "data": {
            "id": tx.id,
            "item_id": tx.item_id,
            "type": tx.type.value,
            "quantity": tx.quantity,
        }
    })
    
    # Also broadcast item update since stock changed
    await manager.broadcast({
        "type": "item_updated",
        "data": {
            "id": item.id,
            "name": item.name,
            "quantity": item.quantity
        }
    })

    # Broadcast low stock alert if needed
    if is_low_stock:
        await manager.broadcast({
            "type": "low_stock_alert",
            "data": {
                "item_id": item.id,
                "name": item.name,
                "quantity": item.quantity,
                "sku": item.sku,
                "threshold": item.low_stock_threshold,
                "message": f"⚠️ Low stock alert: {item.name} has only {item.quantity} left!"
            }
        })
        # use serverless integration to send email notifications
        response = requests.post(os.environ.get('SERVERLESS_EMAIL_URL'), 
                      headers={"Authorization": f"Bearer {os.environ.get('EMAIL_API_KEY')}", "Content-Type": "application/json"},
                      json={"subject": f"Low Stock Alert - {item.name}",
                            "text": f"⚠️ Low stock alert: {item.name} - {item.sku} has only {item.quantity} left!"}
        )
        print(f"INFO: Email API Response Status: {response.status_code}")
        print(f"INFO: Email API Response Body: {response.text}")
    
    return tx


@router.get("/", response_model=list[TransactionOut])
async def list_transactions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Transaction).order_by(Transaction.created_at.desc()).all()