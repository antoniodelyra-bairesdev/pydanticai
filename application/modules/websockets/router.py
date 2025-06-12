import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request

import config.database as db
from modules.auth.service import AuthService
from modules.auth.repository import AuthRepository, LocationRepository
from sqlalchemy.ext.asyncio.session import AsyncSession

from .service import WebSocketService
from .schema import (
    ListedUser,
    WSChatMessageTo,
    WSChatMessageFrom,
    WSMessageType,
    WSMessage,
    WSConnectionMessage,
)

router = APIRouter()


@router.websocket("/connect")
async def websocket_connect(websocket: WebSocket):
    async with db.get_session(db.engine) as session:
        auth_service = AuthService(
            auth_repository=AuthRepository(db=session),
            location_repository=LocationRepository(db=session),
        )
        user = await auth_service.user_from_token(
            websocket.query_params.get("token") or ""
        )

    await websocket.accept()
    if not user:
        return await websocket.close(reason="Unauthorized")

    user = ListedUser.from_model(user, True)
    user_id = user.id
    if user_id not in WebSocketService.connections:
        broadcast_connect = [
            WebSocketService.send_message_to_user(
                user_id,
                WSMessage(
                    type=WSMessageType.CONNECTION,
                    content=WSConnectionMessage(online=True, user=user),
                ),
            )
            for user_id in WebSocketService.connections
        ]
        if len(broadcast_connect) > 0:
            await asyncio.gather(*broadcast_connect)
    connection_id = WebSocketService.register_connection(user_id, websocket)

    try:
        while True:
            raw_data = await websocket.receive_json()
            data = WSMessage(type=raw_data["type"], content=raw_data["content"])
            if data.type == WSMessageType.CHAT:
                rcv = WSChatMessageTo.from_content(data.content)
                await WebSocketService.send_message_to_user(
                    rcv.to_user_id,
                    WSMessage(
                        type=WSMessageType.CHAT,
                        content=WSChatMessageFrom(from_user=user, message=rcv.message),
                    ),
                )
    except WebSocketDisconnect:
        WebSocketService.forget_connection(user_id, connection_id)
        connections = WebSocketService.get_connections(user_id)
        if not connections:
            broadcast_disconnect = [
                WebSocketService.send_message_to_user(
                    user_id,
                    WSMessage(
                        type=WSMessageType.CONNECTION,
                        content=WSConnectionMessage(online=False, user=user),
                    ),
                )
                for user_id in WebSocketService.connections
            ]
            if len(broadcast_disconnect) > 0:
                await asyncio.gather(*broadcast_disconnect)


@router.get("/users")
async def users(request: Request):
    users = await WebSocketService.get_users()
    return [user for user in users if user.id != request.state.user.id]
