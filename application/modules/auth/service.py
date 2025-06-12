from dataclasses import dataclass
from http import HTTPStatus

from fastapi import Request
from fastapi.exceptions import HTTPException
from argon2 import PasswordHasher
from secrets import token_hex

from sqlalchemy.ext.asyncio import AsyncSession

from .repository import AuthRepository, LocationRepository
from .schema import ClientSchema, DeviceSchema, UserSchema
from .model import Usuario


class AuthServiceFactory:
    @staticmethod
    def criarService(db: AsyncSession):
        return AuthService(
            auth_repository=AuthRepository(db),
            location_repository=LocationRepository(db),
        )


@dataclass
class AuthService:
    auth_repository: AuthRepository
    location_repository: LocationRepository

    @classmethod
    def usuario_possui_funcao(cls, nome_funcao: str, usuario: Usuario):
        return any([funcao.nome == nome_funcao for funcao in usuario.funcoes])

    async def usuario_a_partir_de_email(self, email: str):
        return await self.auth_repository.find_user_from_email(email)

    async def user_from_token(self, token: str):
        return await self.auth_repository.find_user_from_token(token)

    async def login(
        self, email: str, password: str, device: ClientSchema
    ) -> tuple[UserSchema, str]:
        user = await self.auth_repository.find_user_from_email(email)
        if not user:
            raise HTTPException(HTTPStatus.NOT_FOUND)

        equal_passwords = self.compare(password, user.senha)
        if not equal_passwords:
            raise HTTPException(HTTPStatus.UNAUTHORIZED)

        location = await self.location_repository.from_address(device.address)
        token = self.create_token()
        (
            id,
            address,
            user_agent,
            location,
            last_active,
            session_started,
        ) = await self.auth_repository.save_login_credentials(
            user.id, device.user_agent, device.address, token, location
        )
        user_schema = UserSchema.from_model(user)
        user_schema.devices.append(
            DeviceSchema(
                id=id,
                address=address,
                user_agent=user_agent,
                location=location,
                last_active=last_active,
                session_started=session_started,
            )
        )

        return user_schema, token

    async def logout(self, token: str):
        await self.auth_repository.remove_device(token)

    async def apagar_sessoes(self, token: str):
        await self.auth_repository.apagar_sessoes(token)

    async def redefinir_senha(
        self, user_token: str, senha_antiga: str, senha_nova: str
    ):
        user = await self.auth_repository.find_user_from_token(user_token)
        if not user:
            raise HTTPException(HTTPStatus.NOT_FOUND)

        equal_passwords = self.compare(senha_antiga, user.senha)
        if not equal_passwords:
            raise HTTPException(HTTPStatus.UNAUTHORIZED)

        if senha_nova == senha_antiga:
            raise HTTPException(
                HTTPStatus.FORBIDDEN, "A senha nova não pode ser igual à antiga"
            )

        senha_hash = self.hash(senha_nova)

        await self.auth_repository.redefinir_senha(user.email, senha_hash)

    async def listar_sessoes(self, token: str):
        return await self.auth_repository.listar_sessoes(token)

    async def usuario(self, token: str):
        usuario = await self.auth_repository.find_user_from_token(token)
        if not usuario:
            raise HTTPException(HTTPStatus.NOT_FOUND, "Usuário inexistente")
        return usuario

    def device_from_request(self, request: Request) -> ClientSchema:
        return ClientSchema(
            user_agent=request.headers.get("user-agent", ""),
            address=request.client.host if request.client else "---",
        )

    def hash(self, value: str | bytes) -> str:
        return PasswordHasher().hash(value)

    def compare(self, value: str | bytes, hash: str | bytes) -> bool:
        try:
            return PasswordHasher().verify(hash, value)
        except:
            return False

    def create_token(self) -> str:
        return token_hex(32)
