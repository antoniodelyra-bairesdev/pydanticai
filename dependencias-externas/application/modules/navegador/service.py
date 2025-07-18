from dataclasses import dataclass
from shutil import move
from uuid import uuid4

from .base import Navegador

@dataclass
class NavegadorService:
    navegador_factory: type[Navegador]

    async def teste(self):
        async with self.navegador_factory.iniciar('/home/host_user/app/files/temp') as navegador:
            await navegador.navegar('http://localhost:8000/docs')
            healthcheck = await navegador.buscar_elemento_por_css('span[data-path="/healthcheck"]')
            if healthcheck == None:
                return None
            await healthcheck.clicar()
            resultado = await navegador.exportar_pagina_pdf('docs.pdf')
            exemplo = f'/home/host_user/docs-{uuid4().hex}.pdf'
            move(resultado, exemplo)
        return exemplo
