from fastapi import FastAPI
from fastapi.responses import FileResponse

import logging
from logging import getLogger, Filter, LogRecord

logging.basicConfig(level=logging.INFO, format="%(levelname)s:\t%(message)s")


from modules.navegador.impl.playwright import NavegadorPlaywright
from modules.navegador.service import NavegadorService


description = f"""
# Icatu Vanguarda | Dependências externas

## Páginas
- [Home](/docs)
"""

app = FastAPI(description=description, title="Home")


@app.get("/healthcheck")
def main():
    return {"healthy": True}


@app.get('/navegador/teste')
async def navegador_teste():
    svc = NavegadorService(navegador_factory=NavegadorPlaywright)
    caminho = await svc.teste()
    if caminho == None:
        return
    return FileResponse(caminho, media_type='application/pdf')


# Prevent log pollution
class HealthCheckFilter(Filter):
    def filter(self, record: LogRecord) -> bool:
        return record.getMessage().find("/healthcheck") == -1

getLogger("uvicorn.access").addFilter(HealthCheckFilter())
