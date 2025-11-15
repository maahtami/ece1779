# app/services/websocket_manager.py
"""
WebSocket connection manager for broadcasting real-time updates to connected clients.
"""
from typing import Set
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"✓ WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        print(f"✓ WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        print(f"📢 Broadcasting to {len(self.active_connections)} clients: {json.dumps(message)}")
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
                print(f"  ✓ Message sent to client")
            except Exception as e:
                print(f"  ✗ Error sending to client: {e}")
                # Connection lost, mark for removal
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.active_connections.discard(connection)

# Global instance
manager = ConnectionManager()
