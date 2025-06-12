from abc import ABC, abstractmethod
from typing import Sequence
from sqlalchemy import select

from .model import Moeda
from modules.repository import BaseRepository


class MoedasRepository(ABC):
    @abstractmethod
    async def lista(self) -> Sequence[Moeda]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_codigo(self, codigo: str) -> Moeda | None:
        raise NotImplementedError


class MoedasRepositoryImpl(MoedasRepository):
    __base_repository: BaseRepository[Moeda]

    def __init__(self, base_repository: BaseRepository[Moeda]):
        self.__base_repository = base_repository

    async def lista(self) -> Sequence[Moeda]:
        return await self.__base_repository.lista()

    async def get_by_codigo(self, codigo: str) -> Moeda | None:
        query = select(Moeda).where(Moeda.codigo == codigo)

        result = await self.__base_repository.get_db_session().execute(query)
        return result.scalar_one_or_none()
