import asyncio
import quickfix as fix
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from modules.fundos.router import router as fundos_router
from modules.indicadores.router import router as indicadores_router
from modules.auth.router import router as auth_router
from modules.ativos.router import router as ativos_router
from modules.calculos.router import router as calculos_router
from modules.b3.router import router as b3_router
from modules.websockets.router import router as websockets_router
from modules.notifications.router import router as notificacoes_router
from modules.operacoes.router import router as operacoes_router
from modules.arquivos.router import router as arquivos_router
from modules.regulatorio.router import router as regulatorio_router
from modules.email.router import router as email_router
from modules.mesas.router import router as mesas_router
from modules.liberacao_cotas.router import router as liberacao_cotas_router
from modules.enquadramento.router import router as enquadramento_router
from modules.cobranca.router import router as cobrancas_router
from modules.indices.router import router as indices_router
from modules.rotinas.indices.coleta.router import (
    router as rotinas_indices_coleta_router,
)

from modules.b3.fix.base_application import BaseFIXApplicationSingleton
from modules.b3.fix.order_entry_application import OrderEntryApplicationSingleton
from modules.b3.fix.post_trade_application import PostTradeApplicationSingleton

from modules.queue.service import QueueService


from config.middleware import (
    AuthMiddleware,
    RequestMiddleware,
    SessionMiddleware,
    exception_handler_with_request_id,
)

import logging
from logging import getLogger, Filter, LogRecord, INFO


logging.basicConfig(level=logging.INFO, format="%(levelname)s:\t%(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logging.info("[START-UP] Starting before startup routine...")
    loop = asyncio.get_running_loop()
    await QueueService.connect(loop)
    await QueueService.connect(loop, "recursos.acesso")
    await QueueService.connect(loop, "execucoes.daycoval")
    fix_applications: list[BaseFIXApplicationSingleton] = [
        OrderEntryApplicationSingleton.get_application(),
        PostTradeApplicationSingleton.get_application(),
    ]
    for fix_application in fix_applications:
        logging.info(f"Iniciando FIX Initiator {fix_application.session_type}")
        fix_application.initiator.start()
    logging.info("[START-UP] Before startup routine ended.")

    yield

    logging.info("[SHUTDOWN] Starting shutdown...")
    for fix_application in fix_applications:
        if not fix_application.initiator.isStopped():
            logging.info(
                f"Stopping FIX initiator socket {fix_application.session_type}..."
            )
            fix_application.initiator.stop(True)
    logging.info("[SHUTDOWN] Shutdown ended.")


api_base_path = "v1"
auth_base_path = "auth"
system_base_path = "sistema"
healthcheck_base_path = "healthcheck"

description = f"""
# Icatu Vanguarda | Back-end v2

## Páginas
- [Home](/docs)
- [API](/{api_base_path}/docs)
- [Autenticação](/{auth_base_path}/docs)
- [Sistema](/{system_base_path}/docs)
"""

app = FastAPI(description=description, title="Home", lifespan=lifespan)
api_app = FastAPI(description=description, title="API")
auth_app = FastAPI(description=description, title="Autenticação")
system_app = FastAPI(description=description, title="Sistema")
ws_app = FastAPI(title="WebSockets")

# General config
app.add_middleware(RequestMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(RequestValidationError, exception_handler_with_request_id)


@app.get("/healthcheck")
def main():
    return {"healthy": True}


# Prevent log pollution
class HealthCheckFilter(Filter):
    def filter(self, record: LogRecord) -> bool:
        return record.getMessage().find("/healthcheck") == -1


getLogger("uvicorn.access").addFilter(HealthCheckFilter())
getLogger("sqlalchemy.engine").setLevel(INFO)


# Auth config
auth_app.add_middleware(SessionMiddleware)
for router in [auth_router]:
    auth_app.include_router(router)

# API config
api_app.add_middleware(AuthMiddleware)
api_app.add_middleware(SessionMiddleware)
for router in [
    fundos_router,
    indicadores_router,
    ativos_router,
    calculos_router,
    b3_router,
    operacoes_router,
    regulatorio_router,
    mesas_router,
    liberacao_cotas_router,
    enquadramento_router,
    cobrancas_router,
    indices_router,
    rotinas_indices_coleta_router,
]:
    api_app.include_router(router)

# WS config
ws_app.add_middleware(AuthMiddleware)
ws_app.add_middleware(SessionMiddleware)
ws_app.include_router(websockets_router)

# System config
system_app.add_middleware(AuthMiddleware)
system_app.add_middleware(SessionMiddleware)
for router in [arquivos_router, notificacoes_router, email_router]:
    system_app.include_router(router)


def mount_and_inherit_handlers_and_middlewares(
    parent_app: FastAPI, subapps: dict[str, tuple[str, FastAPI]]
):
    for path, (title, subapp) in subapps.items():
        subapp.user_middleware = [*parent_app.user_middleware, *subapp.user_middleware]
        for exc_cls, handler in parent_app.exception_handlers.items():
            subapp.add_exception_handler(exc_cls, handler)
        parent_app.mount(path, subapp, title)


mount_and_inherit_handlers_and_middlewares(
    app,
    {
        f"/{api_base_path}": ("API", api_app),
        f"/{auth_base_path}": ("Autorização", auth_app),
        f"/{system_base_path}": ("Sistema", system_app),
        "/ws": ("WebSockets", ws_app),
    },
)
