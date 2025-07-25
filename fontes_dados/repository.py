from abc import ABC, abstractmethod
from typing import Sequence
from sqlalchemy import select

from .model import FonteDados
from modules.fornecedores.model import Fornecedor
from modules.repository import BaseRepository


class FontesDadosRepository(ABC):
    @abstractmethod
    async def lista(self) -> Sequence[FonteDados]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_nome_completo_fonte_dado(
        self, nome_fonte_dado: str
    ) -> FonteDados | None:
        raise NotImplementedError

    @abstractmethod
    async def get_fonte_dado_icatuvanguarda_manual(self) -> FonteDados:
        raise NotImplementedError


class FontesDadosRepositoryImpl(FontesDadosRepository):
    __base_repository: BaseRepository[FonteDados]
    __NOME_COMPLETO_FONTE_DADO_ICATUVANGUARDA_MANUAL: str = "IcatuVanguardaManual"

    def __init__(self, base_repository: BaseRepository[FonteDados]):
        self.__base_repository = base_repository

    async def lista(self) -> Sequence[FonteDados]:
        return await self.__base_repository.lista()

    async def get_by_nome_completo_fonte_dado(
        self, nome_fonte_dado: str
    ) -> FonteDados | None:
        query = select(FonteDados).where(
            (Fornecedor.nome + FonteDados.nome) == nome_fonte_dado
        )

        result = await self.__base_repository.get_db_session().execute(query)
        return result.scalar_one_or_none()

    async def get_fonte_dado_icatuvanguarda_manual(self) -> FonteDados:
        query = select(FonteDados).where(
            Fornecedor.nome + FonteDados.nome
            == self.__NOME_COMPLETO_FONTE_DADO_ICATUVANGUARDA_MANUAL
        )

        result = await self.__base_repository.get_db_session().execute(query)
        return result.scalar_one()
