from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Awaitable, Generator

class ElementoHTML:
    def clicar(self) -> Awaitable[None]:
        raise NotImplementedError()
    
    def ler_input(self) -> Awaitable[str]:
        raise NotImplementedError()
    
    def definir_input(self, valor: str) -> Awaitable[None]:
        raise NotImplementedError()

@dataclass
class Navegador:
    id_execucao: str
    caminho_download: str

    @classmethod
    @asynccontextmanager
    def iniciar(cls, caminho_downloads: str) -> AsyncGenerator['Navegador', Any]:
        raise NotImplementedError()

    def navegar(self, url: str) -> Awaitable[None]:
        raise NotImplementedError()

    def buscar_elementos_por_css(self, css: str) -> Awaitable[list[ElementoHTML]]:
        raise NotImplementedError()
    
    def buscar_elemento_por_css(self, css: str) -> Awaitable[ElementoHTML | None]:
        raise NotImplementedError()
    
    def executar_js(self, js: str) -> Awaitable[None]:
        raise NotImplementedError()
    
    def exportar_pagina_pdf(self, nome: str | None = None) -> Awaitable[str]:
        raise NotImplementedError()
