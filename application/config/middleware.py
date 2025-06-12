from http import HTTPStatus
from inspect import signature, Parameter
from functools import wraps
import logging
from sys import exc_info
from traceback import format_exception
from uuid import uuid4

from fastapi import Request, WebSocket

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request


from modules.auth.service import AuthService
from modules.auth.repository import AuthRepository, LocationRepository
from modules.util.request import get_user

import config.database as db


def with_roles(*roles: str):
    def decorator(func):
        @wraps(func)
        async def wrap(request, *args, **kwargs):
            user = get_user(request)
            role_names = [p.nome for p in user.funcoes]
            match = False
            for role in roles:
                if role in role_names:
                    match = True
                    break
            if not match:
                raise HTTPException(HTTPStatus.FORBIDDEN)
            result = await func(*args, **kwargs)
            return result

        fsig = signature(func)
        fsig = fsig.replace(
            parameters=[
                Parameter(
                    "request", Parameter.POSITIONAL_OR_KEYWORD, annotation=Request
                ),
                *fsig.parameters.values(),
            ]
        )
        wrap.__signature__ = fsig  # type: ignore
        return wrap

    return decorator


async def exception_handler_with_request_id(
    request: Request | WebSocket, exc: RequestValidationError | Exception
):
    uuid = request.state.uuid
    logging.error(f"[REQUEST {uuid}]: Erro de processamento.")
    detail = {"request_id": uuid}
    if type(exc) == RequestValidationError:
        detail = {**detail, "errors": exc.errors()}
        logging.error(f"[REQUEST {uuid}]: -> Erro de validação.")
        logging.error({**detail, "body": exc.body})
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {"detail": {"message": "Erro de validação.", **detail}}
        ),
    )


class RequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        uuid = str(uuid4())
        request.state.uuid = uuid
        try:
            if str(request.url).find("/healthcheck") == -1:
                ip = request.client and request.client.host or "Unknown"
                fwd = request.headers.get("X-Forwarded-For", "None")
                logging.info(
                    f"[{uuid}] {{{ip} | FWD: {fwd}}} requested {str(request.url)}"
                )
            result = await call_next(request)
            return result
        except Exception:
            serialized = "".join(format_exception(*exc_info()))
            request_id = request.state.uuid
            logging.error(f"[REQUEST {request_id}]: {serialized}")
            error_str = "Erro do servidor. Entre em contato com o time de tecnologia"
            body = {"detail": {"request_id": request_id, "message": error_str}}
            return JSONResponse(body, 500)


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ):
        async with db.get_session(db.engine) as session:
            request.state.db = session
            result = await call_next(request)
            await session.commit()
        return result


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        path = request.url.path
        db = request.state.db
        auth_service = AuthService(
            auth_repository=AuthRepository(db=db),
            location_repository=LocationRepository(db=db),
        )

        if (not path.endswith("/docs")) and (not path.endswith("/openapi.json")):
            token = request.headers.get("x-user-token", "")
            user = await auth_service.user_from_token(token)
            if not user:
                return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
            request.state.user = user

        return await call_next(request)
