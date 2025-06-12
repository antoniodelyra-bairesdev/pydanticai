from typing import Annotated
from fastapi import APIRouter, Request, Depends, Header

from modules.util.request import db

from .service import AuthService
from .schema import LoginRequest, LoginResponse, RedefinirSenhaRequest, UserSchema
from .repository import AuthRepository, LocationRepository
from .model import Usuario

router = APIRouter(tags=["Autenticação"])


def get_service(request: Request):
    session = db(request)
    return AuthService(
        auth_repository=AuthRepository(db=session),
        location_repository=LocationRepository(db=session),
    )


@router.post("/login")
async def login(
    req: Request, body: LoginRequest, service: AuthService = Depends(get_service)
) -> LoginResponse:
    user, token = await service.login(
        body.email,
        body.password,
        service.device_from_request(req),
    )
    return LoginResponse(user=user, token=token)


@router.delete("/logout")
async def logout(
    x_user_token: Annotated[str | None, Header()],
    service: AuthService = Depends(get_service),
):
    await service.logout(x_user_token or "")


@router.delete("/invalidar-tokens")
async def apagar_sessoes(
    x_user_token: Annotated[str | None, Header()],
    service: AuthService = Depends(get_service),
):
    await service.apagar_sessoes(x_user_token or "")


@router.patch("/redefinir-senha")
async def redefinir_senha(
    x_user_token: Annotated[str | None, Header()],
    body: RedefinirSenhaRequest,
    service: AuthService = Depends(get_service),
):
    await service.redefinir_senha(
        x_user_token or "", body.senha_antiga, body.senha_nova
    )


@router.get("/sessoes-ativas")
async def sessoes_ativas(
    x_user_token: Annotated[str | None, Header()],
    service: AuthService = Depends(get_service),
):
    return await service.listar_sessoes(x_user_token or "")


@router.get("/eu")
async def usuario(
    x_user_token: Annotated[str | None, Header()],
    service: AuthService = Depends(get_service),
):
    user = await service.usuario(x_user_token or "")
    return UserSchema.from_model(user)
