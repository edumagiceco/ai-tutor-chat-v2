from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect, Depends, status
from jose import JWTError, jwt
import json
import asyncio
from datetime import datetime

from app.core.config import settings
from app.api import deps
from app.models.user import User


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.user_sockets: Dict[WebSocket, User] = {}

    async def connect(self, websocket: WebSocket, user: User):
        await websocket.accept()
        
        # Store connection by user ID
        if user.id not in self.active_connections:
            self.active_connections[user.id] = []
        self.active_connections[user.id].append(websocket)
        
        # Store user info for this socket
        self.user_sockets[websocket] = user
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "user_id": user.id,
            "timestamp": datetime.utcnow().isoformat()
        })

    def disconnect(self, websocket: WebSocket):
        user = self.user_sockets.get(websocket)
        if user and user.id in self.active_connections:
            self.active_connections[user.id].remove(websocket)
            if not self.active_connections[user.id]:
                del self.active_connections[user.id]
        
        if websocket in self.user_sockets:
            del self.user_sockets[websocket]

    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    # Remove dead connections
                    self.disconnect(connection)

    async def broadcast(self, message: dict, exclude_user_id: int = None):
        """Broadcast message to all connected users"""
        for user_id, connections in list(self.active_connections.items()):
            if exclude_user_id and user_id == exclude_user_id:
                continue
            
            for connection in list(connections):
                try:
                    await connection.send_json(message)
                except:
                    # Remove dead connections
                    self.disconnect(connection)

    def get_online_users(self) -> List[Dict]:
        """Get list of online users"""
        online_users = []
        for user_id in self.active_connections:
            # Get first connection's user info
            if self.active_connections[user_id]:
                websocket = self.active_connections[user_id][0]
                user = self.user_sockets.get(websocket)
                if user:
                    online_users.append({
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "role": user.role
                    })
        return online_users


manager = ConnectionManager()


async def get_current_user_websocket(
    websocket: WebSocket,
    token: str
) -> User:
    """Authenticate user from WebSocket connection"""
    credentials_exception = WebSocketDisconnect(
        code=status.WS_1008_POLICY_VIOLATION,
        reason="Could not validate credentials"
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    from sqlalchemy.orm import Session
    from app.core.database import SessionLocal
    
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == username).first()
        if user is None:
            raise credentials_exception
        return user
    finally:
        db.close()


async def websocket_endpoint(websocket: WebSocket, token: str):
    """Main WebSocket endpoint"""
    try:
        # Authenticate user
        user = await get_current_user_websocket(websocket, token)
        
        # Connect user
        await manager.connect(websocket, user)
        
        # Broadcast user joined
        await manager.broadcast({
            "type": "user_joined",
            "user": {
                "id": user.id,
                "name": user.name,
                "role": user.role
            },
            "online_users": manager.get_online_users(),
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user_id=user.id)
        
        try:
            while True:
                # Wait for messages from client
                data = await websocket.receive_json()
                
                # Handle different message types
                message_type = data.get("type")
                
                if message_type == "ping":
                    # Respond to ping
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif message_type == "typing":
                    # Broadcast typing status
                    conversation_id = data.get("conversation_id")
                    if conversation_id:
                        await manager.broadcast({
                            "type": "user_typing",
                            "user_id": user.id,
                            "user_name": user.name,
                            "conversation_id": conversation_id,
                            "timestamp": datetime.utcnow().isoformat()
                        }, exclude_user_id=user.id)
                
                elif message_type == "stop_typing":
                    # Broadcast stop typing status
                    conversation_id = data.get("conversation_id")
                    if conversation_id:
                        await manager.broadcast({
                            "type": "user_stop_typing",
                            "user_id": user.id,
                            "conversation_id": conversation_id,
                            "timestamp": datetime.utcnow().isoformat()
                        }, exclude_user_id=user.id)
                
                elif message_type == "get_online_users":
                    # Send current online users
                    await websocket.send_json({
                        "type": "online_users",
                        "users": manager.get_online_users(),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
        except WebSocketDisconnect:
            # Handle disconnect
            manager.disconnect(websocket)
            
            # Broadcast user left
            await manager.broadcast({
                "type": "user_left",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "role": user.role
                },
                "online_users": manager.get_online_users(),
                "timestamp": datetime.utcnow().isoformat()
            })
            
    except WebSocketDisconnect:
        # Failed to authenticate
        pass