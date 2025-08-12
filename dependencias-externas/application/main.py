import logging
from logging import Filter, LogRecord, getLogger

from fastapi import FastAPI
from fastapi.responses import FileResponse

logging.basicConfig(level=logging.INFO, format="%(levelname)s:\t%(message)s")

from modules.leitor_documentos.handlers import register_exception_handlers
from modules.leitor_documentos.router import router as leitor_documentos_router
from modules.navegador.impl.playwright import NavegadorPlaywright
from modules.navegador.service import NavegadorService

description = f"""
# Icatu Vanguarda | Dependências externas

## Páginas
- [Home](/docs)
"""

app = FastAPI(description=description, title="Home")

# Registrar exception handlers do módulo leitor_documentos
register_exception_handlers(app)

# Incluir routers dos módulos
app.include_router(leitor_documentos_router)


@app.get("/healthcheck")
def main():
    return {"healthy": True}


@app.get("/navegador/teste")
async def navegador_teste():
    svc = NavegadorService(navegador_factory=NavegadorPlaywright)
    caminho = await svc.teste()
    if caminho == None:
        return
    return FileResponse(caminho, media_type="application/pdf")


# Prevent log pollution
class HealthCheckFilter(Filter):
    def filter(self, record: LogRecord) -> bool:
        return record.getMessage().find("/healthcheck") == -1


getLogger("uvicorn.access").addFilter(HealthCheckFilter())
