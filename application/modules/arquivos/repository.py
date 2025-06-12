from abc import ABC, abstractmethod
import base64
from dataclasses import dataclass
from typing import Any, BinaryIO, Coroutine
from uuid import uuid4

from sqlalchemy import delete, insert, select

from sqlalchemy.ext.asyncio.session import AsyncSession

from .model import Arquivo


class ArquivosRepository(ABC):
    @abstractmethod
    def criar(
        self, conteudo: BinaryIO, nome: str | None, tipo: str | None
    ) -> Coroutine[Any, Any, str]: ...
    @abstractmethod
    def buscar(self, id: str) -> Coroutine[Any, Any, Arquivo]: ...
    @abstractmethod
    def apagar(self, id: str) -> Coroutine: ...
    @abstractmethod
    def decodificar(self, arquivo: Arquivo) -> Coroutine[Any, Any, bytes]: ...


@dataclass
class ArquivosDatabaseRepository(ArquivosRepository):
    db: AsyncSession

    async def criar(
        self,
        conteudo: BinaryIO,
        nome: str | None = "unknown",
        tipo: str | None = "application/octet-stream",
    ):
        novo = uuid4().hex
        await self.db.execute(
            insert(Arquivo).values(
                {
                    "id": novo,
                    "provedor": "base64",
                    "nome": nome,
                    "extensao": tipo,
                    "conteudo": base64.b64encode(conteudo.read()).decode(
                        encoding="ascii"
                    ),
                }
            )
        )
        return novo

    async def buscar(self, id: str):
        result = await self.db.execute(select(Arquivo).where(Arquivo.id == id))
        return result.scalars().one()

    async def apagar(self, id: str):
        await self.db.execute(delete(Arquivo).where(Arquivo.id == id))

    async def decodificar(self, arquivo: Arquivo):
        if arquivo.provedor != "base64":
            raise Exception("Arquivo gerado com provedor diferente do solicitado")
        return base64.b64decode(arquivo.conteudo)
