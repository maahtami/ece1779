# app/routers/ws.py
"""
WebSocket endpoint for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from app.services.websocket_manager import manager

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    Clients connect here to receive real-time notifications about items and transactions.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for messages from client
            data = await websocket.receive_text()
            print(f"📨 Received from client: {data}")
            # Currently just echo, can be extended for client->server messaging
    except WebSocketDisconnect:
        print("Client disconnected")
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
