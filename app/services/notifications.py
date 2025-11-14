# app/services/notifications.py
from app.models.item import Item

def notify_low_stock(item: Item) -> None:
    # This is a stub that others can implement.
    # For now you can just log, or publish to Redis, or send to WebSocket manager.
    print(f"[LOW STOCK] Item {item.sku} - {item.name} has quantity {item.quantity}")