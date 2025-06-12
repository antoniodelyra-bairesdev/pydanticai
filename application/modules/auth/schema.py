from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel as Schema
from starlette.datastructures import Address

from .model import (
    Usuario as UserModel,
    Funcao as RoleModel,
    Dispositivo as DeviceModel,
)


class RoleSchema(Schema):
    id: int
    nome: str
    parent_id: int | None = None

    @staticmethod
    def from_model(model: RoleModel):
        return RoleSchema(id=model.id, nome=model.nome)


@dataclass
class ClientSchema:
    user_agent: str
    address: str


class DeviceSchema(Schema):
    id: int
    address: str
    user_agent: str
    last_active: datetime
    session_started: datetime
    location: str | None

    @staticmethod
    def from_model(model: DeviceModel):
        return DeviceSchema(
            id=model.id,
            user_agent=model.agente,
            address=model.endereco,
            location=model.localizacao,
            last_active=model.ultima_atividade,
            session_started=model.data_login,
        )


class UserSchema(Schema):
    id: int
    nome: str
    email: str
    roles: list[RoleSchema]
    devices: list[DeviceSchema]

    @staticmethod
    def from_model(model: UserModel):
        return UserSchema(
            id=model.id,
            nome=model.nome,
            email=model.email,
            roles=[RoleSchema.from_model(p) for p in model.funcoes],
            devices=[DeviceSchema.from_model(d) for d in model.dispositivos],
        )


class LoginRequest(Schema):
    email: str
    password: str


class RedefinirSenhaRequest(Schema):
    senha_antiga: str
    senha_nova: str


class LoginResponse(Schema):
    user: UserSchema
    token: str
