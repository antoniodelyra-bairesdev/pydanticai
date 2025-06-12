from http import HTTPStatus
from fastapi import Request, Query
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession

from modules.auth.model import Usuario
from modules.auth.service import AuthService


def db(request: Request) -> AsyncSession:
    return request.state.db


def get_user(request: Request) -> Usuario:
    return request.state.user


def user_with_role(role: str):
    def wrapper(request: Request) -> Usuario:
        usuario: Usuario = request.state.user
        if not AuthService.usuario_possui_funcao(role, usuario):
            raise HTTPException(
                HTTPStatus.FORBIDDEN,
                "O usuário não possui autorização necessária.",
            )
        return usuario

    return wrapper


def query_int_list(query_param: str, notempty=True):
    def wrapper(q: str | None = Query(alias=query_param, default=None)) -> list[int]:
        if not q:
            raise HTTPException(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                f"O parâmetro {query_param} precisa ser informado",
            )
        try:
            ids = [int(id) for id in q.split(",")]
        except:
            raise HTTPException(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                "Os IDs informados precisam ser inteiros válidos separados por vírgulas.",
            )
        if notempty and not ids:
            raise HTTPException(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                "Pelo menos um ID precisa ser informado.",
            )
        return ids

    return wrapper
