import asyncio
from dataclasses import dataclass
import json
import logging
from fastapi import WebSocket
from typing import Any, ClassVar, Literal
from uuid import uuid4

from modules.auth.repository import AuthRepository

from starlette.websockets import WebSocketState

from .schema import ListedUser, WSJSONMessage, WSMessage, WSMessageType, WSNotification


@dataclass
class WebSocketService:
    """
    Um usuário poderá ter múltiplas conexões ao mesmo tempo e, por enquanto,
    não faremos distinção de dispositivos por usuário. A ideia é tentar enviar
    notificações para um usuário e automaticamente detectarmos todas as suas
    conexões em aberto e distribuirmos a mensagem para todas elas.

    Guardaremos estas informações em um dicionário no seguinte formato:
    ```json
    {
        [ID Usuário]: {
            [ID Conexão]: "<Instância da conexão>"
        }
    }
    ```

    Independente do dispositivo, aceitaremos a conexão, atribuiremos um ID
    aleatório para ela e adicionaremos no dicionário. Caso a chave do usuário
    não exista, criaremos. Quando ela for desconectada, pegaremos o ID da conexão
    e removeremos do dicionário. Caso o dicionário do usuário fique vazio,
    removeremos o usuário do dicionário.

    Exemplo de representação da estrutura:

    ```json
    {
        1: {
            "11a90158-c962-4571-8acb-8f8ca2432d14": "<class 'WebSocket'>"
        },
        4: {
            "55d3fc77-86fd-465d-b530-cda63d294959": "<class 'WebSocket'>"
        },
        7: {
            "d8f9098f-5cc5-4ea8-95c3-962d72106aa1": "<class 'WebSocket'>",
            "1f92fde4-fb1c-4bb8-9a7b-32bebc3337f7": "<class 'WebSocket'>",
            "b12a74c1-986a-4055-9020-f99eca8cf070": "<class 'WebSocket'>"
        }
    }
    ```

    Neste caso, se os usuários 1 e 7 fossem do time de crédito e se o sistema
    enviasse uma notificação para este time, os usuários de id 1 e 7 receberiam
    a notificação em todas as suas conexões, ou seja, o usuário 1 na conexão
    `11a9...` e o usuário 7 nas conexões `d8f9...`, `1f92...` e `b12a...`.

    As conexões do usuário 7 podem ser do mesmo dispositivo ou não. Por exemplo,
    a conexão `d8f9...` pode ser de notebook pela VPN e as conexões `1f92...` e
    `b12a...` de abas diferentes do mesmo navegador em um desktop no AQWA.

    Caso a conexão `55d3...` do usuário 4 sofra uma desconexão, ela seria
    removida do dicionário e, por seu dicionário de conexões estar vazio, o
    usuário 4 seria removido do dicionário de usuários conectados.
    """

    connections: ClassVar[dict[int, dict[str, WebSocket]]] = {}

    @classmethod
    def get_connections(cls, user_id: int):
        if user_id not in cls.connections:
            return None
        return cls.connections[user_id]

    @classmethod
    def register_connection(cls, user_id: int, websocket: WebSocket):
        if user_id not in cls.connections:
            cls.connections[user_id] = {}
        connection_id = str(uuid4())
        cls.connections[user_id][connection_id] = websocket
        return connection_id

    @classmethod
    def forget_connection(cls, user_id: int, connection_id: str):
        if (
            user_id not in cls.connections
            or connection_id not in cls.connections[user_id]
        ):
            return
        del cls.connections[user_id][connection_id]
        if len(cls.connections[user_id]) == 0:
            del cls.connections[user_id]

    @classmethod
    async def disconnect_user(cls, user_id: int):
        if user_id not in cls.connections:
            return
        connections = cls.connections[user_id]

        closing = []
        for connection_id in connections:
            connection = connections[connection_id]
            if connection.client_state == WebSocketState.CONNECTED:
                closing.append(connection.close(reason="Disconnected."))

        del cls.connections[user_id]

        if len(closing) > 0:
            await asyncio.gather(*closing)

    @classmethod
    async def send_message_to_user(cls, user_id: int, message: WSMessage):
        if user_id not in cls.connections:
            return
        connections = cls.connections[user_id]

        sending = []
        for connection_id in connections:
            connection = connections[connection_id]
            sending.append(connection.send_json(json.loads(message.model_dump_json())))

        if len(sending) > 0:
            await asyncio.gather(*sending)

    @classmethod
    async def broadcast(cls, message: WSMessage):
        sending = []
        for user_id in cls.connections:
            sending.append(cls.send_message_to_user(user_id, message))
        if len(sending) > 0:
            await asyncio.gather(*sending)

    @classmethod
    async def notify(
        cls,
        user_ids: list[int],
        *,
        text: str,
        link: str | None = None,
        level: Literal["INFO", "ERROR"] = "INFO"
    ):
        sending = []
        for user_id in user_ids:
            sending.append(
                cls.send_message_to_user(
                    user_id=user_id,
                    message=WSMessage(
                        type=WSMessageType.NOTIFICATION,
                        content=WSNotification(text=text, link=link, level=level),
                    ),
                )
            )
        if sending:
            await asyncio.gather(*sending)

    @classmethod
    async def send_json(cls, body: Any, *, user_ids: list[int] | None = None):
        sending = []
        for user_id in user_ids or cls.connections:
            sending.append(
                cls.send_message_to_user(
                    user_id=user_id,
                    message=WSMessage(
                        type=WSMessageType.JSON,
                        content=WSJSONMessage(body=body),
                    ),
                )
            )
        if sending:
            await asyncio.gather(*sending)

    @classmethod
    async def get_users(cls):
        return []
        # todos_usuarios = await cls.auth_repository.listar_usuarios()
        # return [
        #     ListedUser.from_model(usuario, usuario.id in WebSocketService.connections)
        #     for usuario in todos_usuarios
        # ]
