---
name: websocket
description: |
  실시간 통신, WebSocket 연결 관리를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# WebSocket Skill

실시간 통신, WebSocket 연결 관리를 구현합니다.

## Triggers

- "웹소켓", "websocket", "실시간", "real-time", "채팅"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### Connection Manager

```python
# app/core/websocket.py
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket

import structlog

logger = structlog.get_logger()


@dataclass
class Connection:
    """WebSocket connection wrapper."""

    websocket: WebSocket
    user_id: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ConnectionManager:
    """Manage WebSocket connections.

    Note: This base manager includes instance_id for message deduplication.
    Even in single-instance deployments, this ensures consistency if you
    later scale to multiple instances using ScalableConnectionManager.
    """

    def __init__(self) -> None:
        # Unique instance ID for message deduplication
        # Prevents processing self-originated messages in multi-instance setups
        from uuid import uuid4
        self._instance_id = str(uuid4())

        # All active connections
        self._connections: dict[str, Connection] = {}
        # User ID to connection IDs mapping (for targeting specific users)
        self._user_connections: dict[int, set[str]] = {}
        # Room/channel to connection IDs mapping
        self._rooms: dict[str, set[str]] = {}

    @property
    def instance_id(self) -> str:
        """Get this manager's unique instance ID."""
        return self._instance_id

    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: int | None = None,
    ) -> Connection:
        """Accept a new WebSocket connection."""
        await websocket.accept()

        connection = Connection(
            websocket=websocket,
            user_id=user_id,
        )
        self._connections[connection_id] = connection

        # Track user connections
        if user_id:
            if user_id not in self._user_connections:
                self._user_connections[user_id] = set()
            self._user_connections[user_id].add(connection_id)

        await logger.ainfo(
            "WebSocket connected",
            connection_id=connection_id,
            user_id=user_id,
        )

        return connection

    async def disconnect(self, connection_id: str) -> None:
        """Remove a WebSocket connection."""
        connection = self._connections.pop(connection_id, None)
        if not connection:
            return

        # Remove from user connections
        if connection.user_id:
            user_conns = self._user_connections.get(connection.user_id)
            if user_conns:
                user_conns.discard(connection_id)
                if not user_conns:
                    del self._user_connections[connection.user_id]

        # Remove from all rooms
        for room_connections in self._rooms.values():
            room_connections.discard(connection_id)

        await logger.ainfo(
            "WebSocket disconnected",
            connection_id=connection_id,
            user_id=connection.user_id,
        )

    async def join_room(self, connection_id: str, room: str) -> None:
        """Add connection to a room."""
        if room not in self._rooms:
            self._rooms[room] = set()
        self._rooms[room].add(connection_id)

        await logger.ainfo(
            "Joined room",
            connection_id=connection_id,
            room=room,
        )

    async def leave_room(self, connection_id: str, room: str) -> None:
        """Remove connection from a room."""
        if room in self._rooms:
            self._rooms[room].discard(connection_id)
            if not self._rooms[room]:
                del self._rooms[room]

        await logger.ainfo(
            "Left room",
            connection_id=connection_id,
            room=room,
        )

    async def send_personal(
        self,
        connection_id: str,
        message: dict[str, Any],
    ) -> bool:
        """Send message to a specific connection."""
        connection = self._connections.get(connection_id)
        if not connection:
            return False

        try:
            await connection.websocket.send_json(message)
            return True
        except Exception as e:
            await logger.awarning(
                "Failed to send message",
                connection_id=connection_id,
                error=str(e),
            )
            return False

    async def send_to_user(
        self,
        user_id: int,
        message: dict[str, Any],
    ) -> int:
        """Send message to all connections of a user.

        Returns:
            Number of successful sends.
        """
        connection_ids = self._user_connections.get(user_id, set())
        sent_count = 0

        for conn_id in connection_ids:
            if await self.send_personal(conn_id, message):
                sent_count += 1

        return sent_count

    async def broadcast_to_room(
        self,
        room: str,
        message: dict[str, Any],
        exclude: set[str] | None = None,
    ) -> int:
        """Broadcast message to all connections in a room.

        Returns:
            Number of successful sends.
        """
        connection_ids = self._rooms.get(room, set())
        exclude = exclude or set()
        sent_count = 0

        for conn_id in connection_ids:
            if conn_id not in exclude:
                if await self.send_personal(conn_id, message):
                    sent_count += 1

        return sent_count

    async def broadcast(
        self,
        message: dict[str, Any],
        exclude: set[str] | None = None,
    ) -> int:
        """Broadcast message to all connections.

        Returns:
            Number of successful sends.
        """
        exclude = exclude or set()
        sent_count = 0

        for conn_id in self._connections:
            if conn_id not in exclude:
                if await self.send_personal(conn_id, message):
                    sent_count += 1

        return sent_count

    def get_connection(self, connection_id: str) -> Connection | None:
        """Get connection by ID."""
        return self._connections.get(connection_id)

    def get_room_connections(self, room: str) -> set[str]:
        """Get all connection IDs in a room."""
        return self._rooms.get(room, set()).copy()

    def get_user_connections(self, user_id: int) -> set[str]:
        """Get all connection IDs for a user."""
        return self._user_connections.get(user_id, set()).copy()

    @property
    def connection_count(self) -> int:
        """Get total number of active connections."""
        return len(self._connections)


# Global connection manager instance
manager = ConnectionManager()
```

### WebSocket Message Types

```python
# app/schemas/websocket.py
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


class MessageType(str, Enum):
    """WebSocket message types."""

    # Client -> Server
    PING = "ping"
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    CHAT_MESSAGE = "chat_message"
    TYPING = "typing"

    # Server -> Client
    PONG = "pong"
    ROOM_JOINED = "room_joined"
    ROOM_LEFT = "room_left"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    NEW_MESSAGE = "new_message"
    USER_TYPING = "user_typing"
    ERROR = "error"


class WebSocketMessage(BaseModel):
    """Base WebSocket message."""

    type: MessageType
    data: dict[str, Any] = {}
    timestamp: datetime = None

    def __init__(self, **data):
        if "timestamp" not in data:
            data["timestamp"] = datetime.now()
        super().__init__(**data)


class ChatMessage(BaseModel):
    """Chat message payload."""

    room: str
    content: str
    sender_id: int
    sender_name: str
    timestamp: datetime = None

    def __init__(self, **data):
        if "timestamp" not in data:
            data["timestamp"] = datetime.now()
        super().__init__(**data)


class RoomAction(BaseModel):
    """Room join/leave payload."""

    room: str


class TypingIndicator(BaseModel):
    """Typing indicator payload."""

    room: str
    is_typing: bool
```

### WebSocket Route with Authentication

```python
# app/api/v1/routes/ws.py
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from jwt.exceptions import InvalidTokenError

from app.core.security import decode_access_token
from app.core.websocket import manager
from app.schemas.websocket import (
    ChatMessage,
    MessageType,
    RoomAction,
    TypingIndicator,
    WebSocketMessage,
)

router = APIRouter(prefix="/ws", tags=["websocket"])


async def get_user_from_token(token: str) -> dict | None:
    """Authenticate user from token."""
    try:
        payload = decode_access_token(token)
        if payload:
            return {
                "user_id": int(payload.get("sub")),
                "email": payload.get("email"),
            }
    except InvalidTokenError:
        pass
    return None


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    """Main WebSocket endpoint with JWT authentication."""
    # Authenticate
    user = await get_user_from_token(token)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    connection_id = str(uuid4())
    user_id = user["user_id"]

    # Connect
    connection = await manager.connect(
        websocket=websocket,
        connection_id=connection_id,
        user_id=user_id,
    )

    try:
        # Send welcome message
        await manager.send_personal(
            connection_id,
            WebSocketMessage(
                type=MessageType.PONG,
                data={"message": "Connected", "connection_id": connection_id},
            ).model_dump(mode="json"),
        )

        # Message loop
        while True:
            data = await websocket.receive_json()
            await handle_message(connection_id, user, data)

    except WebSocketDisconnect:
        await manager.disconnect(connection_id)


async def handle_message(
    connection_id: str,
    user: dict,
    data: dict,
) -> None:
    """Handle incoming WebSocket message."""
    try:
        message = WebSocketMessage(**data)
    except Exception:
        await manager.send_personal(
            connection_id,
            WebSocketMessage(
                type=MessageType.ERROR,
                data={"message": "Invalid message format"},
            ).model_dump(mode="json"),
        )
        return

    match message.type:
        case MessageType.PING:
            await manager.send_personal(
                connection_id,
                WebSocketMessage(type=MessageType.PONG).model_dump(mode="json"),
            )

        case MessageType.JOIN_ROOM:
            room_data = RoomAction(**message.data)
            await manager.join_room(connection_id, room_data.room)

            # Notify user
            await manager.send_personal(
                connection_id,
                WebSocketMessage(
                    type=MessageType.ROOM_JOINED,
                    data={"room": room_data.room},
                ).model_dump(mode="json"),
            )

            # Notify room
            await manager.broadcast_to_room(
                room_data.room,
                WebSocketMessage(
                    type=MessageType.USER_JOINED,
                    data={
                        "user_id": user["user_id"],
                        "room": room_data.room,
                    },
                ).model_dump(mode="json"),
                exclude={connection_id},
            )

        case MessageType.LEAVE_ROOM:
            room_data = RoomAction(**message.data)
            await manager.leave_room(connection_id, room_data.room)

            # Notify user
            await manager.send_personal(
                connection_id,
                WebSocketMessage(
                    type=MessageType.ROOM_LEFT,
                    data={"room": room_data.room},
                ).model_dump(mode="json"),
            )

            # Notify room
            await manager.broadcast_to_room(
                room_data.room,
                WebSocketMessage(
                    type=MessageType.USER_LEFT,
                    data={
                        "user_id": user["user_id"],
                        "room": room_data.room,
                    },
                ).model_dump(mode="json"),
            )

        case MessageType.CHAT_MESSAGE:
            chat_data = message.data
            room = chat_data.get("room")

            if not room:
                await manager.send_personal(
                    connection_id,
                    WebSocketMessage(
                        type=MessageType.ERROR,
                        data={"message": "Room is required"},
                    ).model_dump(mode="json"),
                )
                return

            # Broadcast to room
            await manager.broadcast_to_room(
                room,
                WebSocketMessage(
                    type=MessageType.NEW_MESSAGE,
                    data=ChatMessage(
                        room=room,
                        content=chat_data.get("content", ""),
                        sender_id=user["user_id"],
                        sender_name=user.get("email", "Unknown"),
                    ).model_dump(mode="json"),
                ).model_dump(mode="json"),
            )

        case MessageType.TYPING:
            typing_data = TypingIndicator(**message.data)

            # Broadcast typing status to room
            await manager.broadcast_to_room(
                typing_data.room,
                WebSocketMessage(
                    type=MessageType.USER_TYPING,
                    data={
                        "user_id": user["user_id"],
                        "room": typing_data.room,
                        "is_typing": typing_data.is_typing,
                    },
                ).model_dump(mode="json"),
                exclude={connection_id},
            )

        case _:
            await manager.send_personal(
                connection_id,
                WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"message": f"Unknown message type: {message.type}"},
                ).model_dump(mode="json"),
            )
```

### WebSocket with Redis Pub/Sub (Scalable)

```python
# app/infrastructure/pubsub/redis.py
import asyncio
import json
from typing import Any, Callable, Coroutine

import redis.asyncio as redis

from app.core.config import settings

import structlog

logger = structlog.get_logger()


class RedisPubSub:
    """Redis Pub/Sub for scalable WebSocket broadcasting."""

    def __init__(self) -> None:
        self._redis: redis.Redis | None = None
        self._pubsub: redis.client.PubSub | None = None
        self._handlers: dict[str, list[Callable]] = {}
        self._listener_task: asyncio.Task | None = None

    async def connect(self) -> None:
        """Connect to Redis."""
        self._redis = redis.from_url(settings.REDIS_URL)
        self._pubsub = self._redis.pubsub()
        await logger.ainfo("Redis Pub/Sub connected")

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass

        if self._pubsub:
            await self._pubsub.close()

        if self._redis:
            await self._redis.close()

        await logger.ainfo("Redis Pub/Sub disconnected")

    async def subscribe(
        self,
        channel: str,
        handler: Callable[[dict], Coroutine[Any, Any, None]],
    ) -> None:
        """Subscribe to a channel with a handler."""
        if channel not in self._handlers:
            self._handlers[channel] = []
            await self._pubsub.subscribe(channel)

        self._handlers[channel].append(handler)

        # Start listener if not running
        if not self._listener_task:
            self._listener_task = asyncio.create_task(self._listen())

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a channel."""
        if channel in self._handlers:
            del self._handlers[channel]
            await self._pubsub.unsubscribe(channel)

    async def publish(self, channel: str, message: dict) -> int:
        """Publish message to a channel.

        Returns:
            Number of subscribers that received the message.
        """
        return await self._redis.publish(channel, json.dumps(message))

    async def _listen(self) -> None:
        """Listen for messages."""
        try:
            async for message in self._pubsub.listen():
                if message["type"] == "message":
                    channel = message["channel"].decode()
                    data = json.loads(message["data"])

                    handlers = self._handlers.get(channel, [])
                    for handler in handlers:
                        try:
                            await handler(data)
                        except Exception as e:
                            await logger.aexception(
                                "Pub/Sub handler error",
                                channel=channel,
                                error=str(e),
                            )
        except asyncio.CancelledError:
            pass


# Global instance
pubsub = RedisPubSub()
```

### Scalable WebSocket Manager

```python
# app/core/websocket_scalable.py
import uuid
from typing import Any

from app.core.websocket import ConnectionManager, manager
from app.infrastructure.pubsub.redis import pubsub


class ScalableConnectionManager(ConnectionManager):
    """Connection manager with Redis Pub/Sub for horizontal scaling.

    Inherits instance_id from ConnectionManager for message deduplication.
    Uses Redis Pub/Sub to broadcast messages across multiple instances.
    """

    def __init__(self) -> None:
        super().__init__()
        # instance_id is inherited from ConnectionManager

    async def setup(self) -> None:
        """Setup Redis Pub/Sub handlers."""
        await pubsub.connect()

        # Subscribe to broadcast channel
        await pubsub.subscribe("ws:broadcast", self._handle_broadcast)

    async def teardown(self) -> None:
        """Cleanup Redis Pub/Sub."""
        await pubsub.disconnect()

    async def _handle_broadcast(self, message: dict) -> None:
        """Handle broadcast message from Redis."""
        # Skip messages from self to prevent duplicate processing
        source_instance = message.get("source_instance")
        if source_instance == self._instance_id:
            return

        msg_type = message.get("type")
        data = message.get("data", {})

        if msg_type == "room_broadcast":
            room = data.get("room")
            payload = data.get("payload")
            exclude = set(data.get("exclude", []))
            await super().broadcast_to_room(room, payload, exclude)

        elif msg_type == "user_broadcast":
            user_id = data.get("user_id")
            payload = data.get("payload")
            await super().send_to_user(user_id, payload)

        elif msg_type == "global_broadcast":
            payload = data.get("payload")
            exclude = set(data.get("exclude", []))
            await super().broadcast(payload, exclude)

    async def broadcast_to_room(
        self,
        room: str,
        message: dict[str, Any],
        exclude: set[str] | None = None,
    ) -> int:
        """Broadcast to room via Redis for multi-instance support."""
        # Publish to Redis for other instances
        await pubsub.publish(
            "ws:broadcast",
            {
                "type": "room_broadcast",
                "source_instance": self._instance_id,  # Include source for dedup
                "data": {
                    "room": room,
                    "payload": message,
                    "exclude": list(exclude or []),
                },
            },
        )

        # Also handle locally
        return await super().broadcast_to_room(room, message, exclude)

    async def send_to_user(
        self,
        user_id: int,
        message: dict[str, Any],
    ) -> int:
        """Send to user via Redis for multi-instance support."""
        await pubsub.publish(
            "ws:broadcast",
            {
                "type": "user_broadcast",
                "source_instance": self._instance_id,  # Include source for dedup
                "data": {
                    "user_id": user_id,
                    "payload": message,
                },
            },
        )

        return await super().send_to_user(user_id, message)


# Use scalable manager for production
scalable_manager = ScalableConnectionManager()
```

### Lifespan Integration

```python
# app/main.py
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.core.websocket_scalable import scalable_manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan events."""
    # Startup
    await scalable_manager.setup()
    yield
    # Shutdown
    await scalable_manager.teardown()
```

## Client Example

```javascript
// JavaScript WebSocket client example
const token = "your-jwt-token";
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws?token=${token}`);

ws.onopen = () => {
  console.log("Connected");

  // Join a room
  ws.send(
    JSON.stringify({
      type: "join_room",
      data: { room: "general" },
    })
  );
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("Received:", message);

  switch (message.type) {
    case "new_message":
      // Handle new chat message
      break;
    case "user_joined":
      // Handle user joined notification
      break;
  }
};

// Send a chat message
function sendMessage(room, content) {
  ws.send(
    JSON.stringify({
      type: "chat_message",
      data: { room, content },
    })
  );
}

// Send typing indicator
function sendTyping(room, isTyping) {
  ws.send(
    JSON.stringify({
      type: "typing",
      data: { room, is_typing: isTyping },
    })
  );
}
```

---

## Server-Sent Events (SSE)

SSE is ideal for **one-way server-to-client** streaming. Use SSE when:
- Only server needs to push updates (notifications, logs, progress)
- Simpler than WebSocket for read-only streams
- Auto-reconnection built into browsers
- Works over standard HTTP (firewall-friendly)

### SSE vs WebSocket

| Feature | SSE | WebSocket |
|---------|-----|-----------|
| Direction | Server → Client | Bidirectional |
| Protocol | HTTP | WS |
| Reconnection | Automatic | Manual |
| Complexity | Simple | More complex |
| Use Case | Notifications, logs | Chat, gaming |

### SSE Implementation

```python
# app/api/v1/routes/sse.py
import asyncio
from typing import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/sse", tags=["sse"])


async def event_generator(request: Request) -> AsyncIterator[str]:
    """Generate SSE events.

    SSE format:
    - event: <event-type> (optional)
    - data: <message>
    - id: <event-id> (optional)
    - retry: <milliseconds> (optional)
    - Blank line to end message
    """
    event_id = 0

    while True:
        # Check if client disconnected
        if await request.is_disconnected():
            await logger.ainfo("SSE client disconnected")
            break

        # Yield event (format: "data: <json>\n\n")
        event_id += 1
        yield f"id: {event_id}\nevent: heartbeat\ndata: {{\"status\": \"alive\", \"id\": {event_id}}}\n\n"

        # Wait before next event
        await asyncio.sleep(30)  # Heartbeat every 30 seconds


@router.get("/stream")
async def sse_stream(request: Request):
    """Server-Sent Events stream endpoint.

    Client connects and receives events as they occur.
    """
    return StreamingResponse(
        event_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
```

### SSE with User-Specific Events

```python
# app/core/sse.py
import asyncio
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger()


@dataclass
class SSEClient:
    """SSE client connection."""

    user_id: int
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)


class SSEManager:
    """Manage SSE connections and event broadcasting."""

    def __init__(self) -> None:
        self._clients: dict[str, SSEClient] = {}
        self._user_clients: dict[int, set[str]] = {}

    def register(self, client_id: str, user_id: int) -> SSEClient:
        """Register a new SSE client."""
        client = SSEClient(user_id=user_id)
        self._clients[client_id] = client

        if user_id not in self._user_clients:
            self._user_clients[user_id] = set()
        self._user_clients[user_id].add(client_id)

        return client

    def unregister(self, client_id: str) -> None:
        """Unregister an SSE client."""
        if client_id in self._clients:
            client = self._clients.pop(client_id)
            if client.user_id in self._user_clients:
                self._user_clients[client.user_id].discard(client_id)

    async def send_to_user(
        self,
        user_id: int,
        event_type: str,
        data: dict[str, Any],
    ) -> int:
        """Send event to all connections of a specific user."""
        sent = 0
        client_ids = self._user_clients.get(user_id, set())

        for client_id in client_ids:
            client = self._clients.get(client_id)
            if client:
                await client.queue.put({
                    "event": event_type,
                    "data": data,
                })
                sent += 1

        return sent

    async def broadcast(
        self,
        event_type: str,
        data: dict[str, Any],
    ) -> int:
        """Broadcast event to all connected clients."""
        sent = 0
        for client in self._clients.values():
            await client.queue.put({
                "event": event_type,
                "data": data,
            })
            sent += 1
        return sent


# Singleton manager
sse_manager = SSEManager()
```

### SSE Route with Authentication

```python
# app/api/v1/routes/notifications.py
import asyncio
import json
from uuid import uuid4

from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse

from app.api.v1.dependencies import CurrentUser
from app.core.sse import sse_manager

router = APIRouter(prefix="/notifications", tags=["notifications"])


async def notification_stream(
    request: Request,
    client_id: str,
    user_id: int,
) -> AsyncIterator[str]:
    """Generate notification events for authenticated user."""
    client = sse_manager.register(client_id, user_id)

    try:
        while True:
            if await request.is_disconnected():
                break

            try:
                # Wait for event with timeout (for heartbeat)
                event = await asyncio.wait_for(
                    client.queue.get(),
                    timeout=30.0,
                )
                yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"

            except asyncio.TimeoutError:
                # Send heartbeat
                yield f"event: heartbeat\ndata: {{\"status\": \"alive\"}}\n\n"

    finally:
        sse_manager.unregister(client_id)


@router.get("/stream")
async def get_notification_stream(
    request: Request,
    current_user: CurrentUser,
):
    """Get real-time notifications via SSE.

    Requires authentication. Each user receives their own events.
    """
    client_id = str(uuid4())

    return StreamingResponse(
        notification_stream(request, client_id, current_user.id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# Usage from other services:
# await sse_manager.send_to_user(user_id, "order_update", {"order_id": 123, "status": "shipped"})
```

### SSE JavaScript Client

```javascript
// SSE client with auto-reconnection
class SSEClient {
  constructor(url, options = {}) {
    this.url = url;
    this.options = options;
    this.eventSource = null;
    this.handlers = {};
  }

  connect() {
    this.eventSource = new EventSource(this.url, this.options);

    this.eventSource.onopen = () => {
      console.log("SSE connected");
    };

    this.eventSource.onerror = (e) => {
      console.error("SSE error:", e);
      // Auto-reconnection is handled by browser
    };

    // Generic message handler
    this.eventSource.onmessage = (e) => {
      console.log("SSE message:", e.data);
    };

    // Register custom event handlers
    Object.entries(this.handlers).forEach(([event, handler]) => {
      this.eventSource.addEventListener(event, (e) => {
        handler(JSON.parse(e.data));
      });
    });
  }

  on(eventType, handler) {
    this.handlers[eventType] = handler;
    if (this.eventSource) {
      this.eventSource.addEventListener(eventType, (e) => {
        handler(JSON.parse(e.data));
      });
    }
    return this;
  }

  close() {
    if (this.eventSource) {
      this.eventSource.close();
    }
  }
}

// Usage
const sse = new SSEClient("/api/v1/notifications/stream");
sse
  .on("order_update", (data) => {
    console.log("Order updated:", data);
  })
  .on("notification", (data) => {
    showNotification(data.title, data.message);
  })
  .connect();
```

---

## SSE Reconnection Policy

SSE provides automatic reconnection with `Last-Event-ID` support for resuming streams.

### Server-Side Reconnection Support

```python
# app/api/v1/routes/sse_reconnect.py
import asyncio
import json
from typing import AsyncIterator
from uuid import uuid4

from fastapi import APIRouter, Request, Header, Depends
from fastapi.responses import StreamingResponse

from app.api.v1.dependencies import CurrentUser
from app.core.sse import sse_manager

router = APIRouter(prefix="/events", tags=["sse"])


async def resilient_event_stream(
    request: Request,
    client_id: str,
    user_id: int,
    last_event_id: str | None = None,
) -> AsyncIterator[str]:
    """SSE stream with reconnection support.

    Features:
    - Last-Event-ID: Resume from last received event
    - retry: Client reconnection delay (milliseconds)
    - Heartbeat: Keep connection alive
    """
    client = sse_manager.register(client_id, user_id)
    event_counter = 0

    # Resume from last event if reconnecting
    if last_event_id:
        # Replay missed events from event store (Redis, DB, etc.)
        missed_events = await get_events_since(user_id, last_event_id)
        for event in missed_events:
            event_counter += 1
            yield format_sse_event(
                event_id=event["id"],
                event_type=event["type"],
                data=event["data"],
            )

    # Set retry interval (3 seconds)
    yield "retry: 3000\n\n"

    try:
        while True:
            if await request.is_disconnected():
                break

            try:
                event = await asyncio.wait_for(
                    client.queue.get(),
                    timeout=30.0,
                )
                event_counter += 1
                event_id = f"{client_id}-{event_counter}"

                # Store event for replay on reconnection
                await store_event(user_id, event_id, event)

                yield format_sse_event(
                    event_id=event_id,
                    event_type=event["event"],
                    data=event["data"],
                )

            except asyncio.TimeoutError:
                # Heartbeat with id for reconnection tracking
                event_counter += 1
                yield format_sse_event(
                    event_id=f"{client_id}-{event_counter}",
                    event_type="heartbeat",
                    data={"status": "alive"},
                )
    finally:
        sse_manager.unregister(client_id)


def format_sse_event(
    event_id: str,
    event_type: str,
    data: dict,
) -> str:
    """Format SSE event with proper structure.

    SSE Format:
    id: <event-id>
    event: <event-type>
    data: <json-data>
    <blank line>
    """
    return f"id: {event_id}\nevent: {event_type}\ndata: {json.dumps(data)}\n\n"


@router.get("/stream")
async def get_event_stream(
    request: Request,
    current_user: CurrentUser,
    last_event_id: str | None = Header(None, alias="Last-Event-ID"),
):
    """SSE endpoint with reconnection support.

    Headers:
    - Last-Event-ID: Resume from specific event (sent automatically by browser)

    Response directives:
    - retry: Reconnection delay in milliseconds
    - id: Event ID for tracking
    """
    client_id = str(uuid4())

    return StreamingResponse(
        resilient_event_stream(
            request,
            client_id,
            current_user.id,
            last_event_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",  # Configure for your domain
        },
    )


# Event store helpers (implement with Redis or DB)
async def store_event(user_id: int, event_id: str, event: dict) -> None:
    """Store event for replay. TTL: 5 minutes."""
    # Example: Redis ZADD with timestamp score
    # await redis.zadd(f"events:{user_id}", {json.dumps(event): time.time()})
    pass


async def get_events_since(user_id: int, last_event_id: str) -> list[dict]:
    """Get events after last_event_id for replay."""
    # Example: Redis ZRANGEBYSCORE
    # return await redis.zrangebyscore(f"events:{user_id}", last_timestamp, "+inf")
    return []
```

### SSE Reconnection Summary

| Directive | Purpose | Example |
|-----------|---------|---------|
| `id:` | Event ID for Last-Event-ID header | `id: evt-123` |
| `retry:` | Reconnection delay (ms) | `retry: 3000` |
| `event:` | Event type for addEventListener | `event: notification` |
| `data:` | JSON payload | `data: {"msg": "hi"}` |

---

## WebSocket Ping-Pong Heartbeat

Implement application-level heartbeat to detect dead connections.

### Connection Manager with Heartbeat

```python
# app/core/websocket_heartbeat.py
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from fastapi import WebSocket

import structlog

logger = structlog.get_logger()


@dataclass
class HeartbeatConnection:
    """Connection with heartbeat tracking."""

    websocket: WebSocket
    user_id: int | None = None
    last_ping: datetime = field(default_factory=datetime.now)
    last_pong: datetime = field(default_factory=datetime.now)
    missed_pongs: int = 0


class HeartbeatConnectionManager:
    """WebSocket manager with ping-pong heartbeat.

    Features:
    - Server sends PING every interval
    - Client must respond with PONG
    - Disconnect after max missed pongs
    """

    PING_INTERVAL = 30  # seconds
    PONG_TIMEOUT = 10   # seconds to wait for pong
    MAX_MISSED_PONGS = 3

    def __init__(self) -> None:
        self._connections: dict[str, HeartbeatConnection] = {}
        self._heartbeat_task: asyncio.Task | None = None

    async def start_heartbeat(self) -> None:
        """Start the heartbeat loop."""
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def stop_heartbeat(self) -> None:
        """Stop the heartbeat loop."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

    async def _heartbeat_loop(self) -> None:
        """Periodic ping to all connections."""
        while True:
            await asyncio.sleep(self.PING_INTERVAL)
            await self._send_pings()

            # Check for stale connections after pong timeout
            await asyncio.sleep(self.PONG_TIMEOUT)
            await self._check_stale_connections()

    async def _send_pings(self) -> None:
        """Send PING to all connections."""
        now = datetime.now()

        for conn_id, conn in list(self._connections.items()):
            try:
                await conn.websocket.send_json({
                    "type": "ping",
                    "timestamp": now.isoformat(),
                })
                conn.last_ping = now

            except Exception as e:
                await logger.awarning(
                    "Failed to send ping",
                    connection_id=conn_id,
                    error=str(e),
                )
                await self.disconnect(conn_id)

    async def _check_stale_connections(self) -> None:
        """Disconnect connections that missed too many pongs."""
        now = datetime.now()
        stale_threshold = now - timedelta(
            seconds=self.PING_INTERVAL + self.PONG_TIMEOUT
        )

        for conn_id, conn in list(self._connections.items()):
            if conn.last_pong < stale_threshold:
                conn.missed_pongs += 1

                await logger.awarning(
                    "Missed pong",
                    connection_id=conn_id,
                    missed_count=conn.missed_pongs,
                )

                if conn.missed_pongs >= self.MAX_MISSED_PONGS:
                    await logger.ainfo(
                        "Disconnecting stale connection",
                        connection_id=conn_id,
                    )
                    await self.disconnect(conn_id)

    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: int | None = None,
    ) -> HeartbeatConnection:
        """Accept and register connection."""
        await websocket.accept()

        connection = HeartbeatConnection(
            websocket=websocket,
            user_id=user_id,
        )
        self._connections[connection_id] = connection

        return connection

    async def disconnect(self, connection_id: str) -> None:
        """Remove connection."""
        if conn := self._connections.pop(connection_id, None):
            try:
                await conn.websocket.close()
            except Exception:
                pass

    def handle_pong(self, connection_id: str) -> None:
        """Record pong response from client."""
        if conn := self._connections.get(connection_id):
            conn.last_pong = datetime.now()
            conn.missed_pongs = 0  # Reset counter

    async def send(
        self,
        connection_id: str,
        message: dict[str, Any],
    ) -> bool:
        """Send message to connection."""
        if conn := self._connections.get(connection_id):
            try:
                await conn.websocket.send_json(message)
                return True
            except Exception:
                await self.disconnect(connection_id)
        return False


heartbeat_manager = HeartbeatConnectionManager()
```

### WebSocket Endpoint with Heartbeat

```python
# app/api/v1/routes/ws_heartbeat.py
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status

from app.core.security import decode_access_token
from app.core.websocket_heartbeat import heartbeat_manager

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/v2")
async def websocket_with_heartbeat(
    websocket: WebSocket,
    token: str = Query(...),
):
    """WebSocket endpoint with ping-pong heartbeat.

    Protocol:
    1. Server sends {"type": "ping", "timestamp": "..."} every 30s
    2. Client MUST respond with {"type": "pong"}
    3. Connection closed after 3 missed pongs
    """
    # Authenticate
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    connection_id = str(uuid4())
    await heartbeat_manager.connect(websocket, connection_id, user_id)

    try:
        while True:
            data = await websocket.receive_json()

            # Handle pong response
            if data.get("type") == "pong":
                heartbeat_manager.handle_pong(connection_id)
                continue

            # Handle other messages...
            await handle_message(connection_id, user_id, data)

    except WebSocketDisconnect:
        await heartbeat_manager.disconnect(connection_id)
```

### JavaScript Client with Pong Response

```javascript
// WebSocket client with automatic pong response
class HeartbeatWebSocket {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  connect() {
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log("WebSocket connected");
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      // Respond to server ping
      if (message.type === "ping") {
        this.ws.send(JSON.stringify({ type: "pong" }));
        return;
      }

      // Handle other messages
      this.onMessage(message);
    };

    this.ws.onclose = (event) => {
      console.log("WebSocket closed:", event.code, event.reason);
      this.attemptReconnect();
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

      setTimeout(() => this.connect(), delay);
    } else {
      console.error("Max reconnect attempts reached");
    }
  }

  onMessage(message) {
    // Override this method
    console.log("Received:", message);
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  close() {
    this.maxReconnectAttempts = 0; // Prevent reconnection
    this.ws?.close();
  }
}

// Usage
const ws = new HeartbeatWebSocket("ws://localhost:8000/api/v1/ws/v2?token=...");
ws.onMessage = (message) => {
  switch (message.type) {
    case "new_message":
      displayMessage(message.data);
      break;
  }
};
ws.connect();
```

### Heartbeat Summary

| Parameter | Value | Description |
|-----------|-------|-------------|
| `PING_INTERVAL` | 30s | Time between server pings |
| `PONG_TIMEOUT` | 10s | Max wait for pong response |
| `MAX_MISSED_PONGS` | 3 | Disconnect after N misses |
| Reconnect delay | Exponential | 1s, 2s, 4s, 8s, 16s |

## References

- `_references/ARCHITECTURE-PATTERN.md`
