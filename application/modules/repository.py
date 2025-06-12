from abc import ABC, abstractmethod
from sqlalchemy import select
from typing import Any, Sequence, TypeVar, Generic

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T], ABC):
    @abstractmethod
    def get_db_session(self) -> AsyncSession:
        raise NotImplementedError

    @abstractmethod
    async def lista(self) -> Sequence[T]:
        raise NotImplementedError


class BaseRepositoryImpl(BaseRepository[T]):
    __db_session: AsyncSession
    __model_class: type[T]

    def __init__(self, db_session: AsyncSession, model_class: type[T]):
        self.__db_session = db_session
        self.__model_class = model_class

    def get_db_session(self) -> AsyncSession:
        return self.__db_session

    async def lista(self) -> Sequence[T]:
        results = await self.__db_session.execute(select(self.__model_class))
        return results.scalars().all()
