from contextlib import asynccontextmanager
from dataclasses import dataclass
from playwright.async_api import async_playwright, Page, ElementHandle

from modules.navegador.base import ElementoHTML, Navegador

from shutil import rmtree
from uuid import uuid4

@dataclass
class ElementoHTMLPlaywright(ElementoHTML):
    el: ElementHandle

    async def clicar(self) -> None:
        await self.el.click()
    
    async def ler_input(self) -> str:
        return await self.el.input_value()
    
    async def definir_input(self, valor: str) -> None:
        await self.el.type(valor)

@dataclass
class NavegadorPlaywright(Navegador):
    id_execucao: str
    caminho_download: str
    pagina: Page

    @classmethod
    @asynccontextmanager
    async def iniciar(cls, caminho_downloads: str):
        exec_id = uuid4().hex
        download_dir = f"{caminho_downloads}/{exec_id}"
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False, downloads_path=download_dir)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
                    ignore_https_errors=True
                )
                page = await context.new_page()
                await page.emulate_media(media='screen')
                yield NavegadorPlaywright(
                    id_execucao=exec_id,
                    caminho_download=download_dir,
                    pagina=page
                )
        finally:
            rmtree(download_dir, ignore_errors=True)

    async def navegar(self, url: str) -> None:
        await self.pagina.goto(url)

    async def buscar_elementos_por_css(self, css: str) -> list[ElementoHTML]:
        elementos = await self.pagina.locator(css).element_handles()
        return [
            ElementoHTMLPlaywright(el=el)
            for el in elementos
        ]
    
    async def buscar_elemento_por_css(self, css: str) -> ElementoHTML | None:
        elementos = await self.buscar_elementos_por_css(css)
        if elementos:
            return elementos[0]
        return None
    
    async def executar_js(self, js: str) -> None:
        await self.pagina.evaluate(js)
    
    async def exportar_pagina_pdf(self, nome: str | None = None) -> str:
        caminho = f'{self.caminho_download}/{nome if nome else uuid4().hex}.pdf'
        with open(caminho, 'wb') as download:
            download.write(
                await self.pagina.pdf(
                    display_header_footer=False,
                    width='1920px',
                    height='1080px',
                    margin={
                        'top': '0px',
                        'bottom': '0px',
                        'left': '0px',
                        'right': '0px'
                    },
                    print_background=True
                )
            )
        return caminho
