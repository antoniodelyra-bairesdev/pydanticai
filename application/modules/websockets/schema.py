from datetime import datetime
from enum import Enum
from typing import Literal
from pydantic import BaseModel as Schema

from modules.auth.model import Usuario


class ListedUser(Schema):
    id: int
    nome: str
    email: str
    conectado: bool

    @staticmethod
    def from_model(model: Usuario, conectado: bool):
        return ListedUser(
            id=model.id, nome=model.nome, email=model.email, conectado=conectado
        )


class WSMessageType(Enum):
    CONNECTION = 0
    CHAT = 1
    NOTIFICATION = 2

    JSON = 255


class WSConnectionMessage(Schema):
    user: ListedUser
    online: bool


class WSChatMessageTo(Schema):
    to_user_id: int
    message: str

    @staticmethod
    def from_content(data):
        if type(data) != WSChatMessageTo:
            raise TypeError("Estrutura errada de mensagem.")
        return WSChatMessageTo(message=data.message, to_user_id=data.to_user_id)


class WSChatMessageFrom(Schema):
    from_user: ListedUser
    message: str


class WSNotification(Schema):
    text: str
    link: str | None = None
    level: Literal["INFO", "ERROR"] = "INFO"


class WSJSONMessage(Schema):
    body: dict

    @staticmethod
    def from_content(data):
        if type(data) != WSJSONMessage:
            raise TypeError("Estrutura errada de mensagem.")
        return WSJSONMessage(body=data.body)


class WSMessage(Schema):
    type: WSMessageType
    content: (
        WSConnectionMessage
        | WSChatMessageTo
        | WSChatMessageFrom
        | WSNotification
        | WSJSONMessage
    )
