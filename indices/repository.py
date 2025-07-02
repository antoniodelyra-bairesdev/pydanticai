from abc import ABC, abstractmethod
from datetime import date
from typing import Sequence
from sqlalchemy import select, insert
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload, noload

from .model import Indice, IndiceCotacao, IndiceIdentificador
from .schema import IndiceCotacaoSchema
from modules.repository import BaseRepository
from modules.moedas.model import Moeda


class IndicesRepository(ABC):
    @abstractmethod
    async def lista(self) -> Sequence[Indice]:
        raise NotImplementedError

    @abstractmethod
    async def lista_indices_sem_cotacoes(self) -> Sequence[Indice]:
        raise NotImplementedError

    @abstractmethod
    async def lista_by_identificadores(
        self,
        identificadores: list[str],
    ) -> Sequence[Indice]:
        raise NotImplementedError

    @abstractmethod
    async def lista_by_nomes(self, nomes: list[str]) -> Sequence[Indice]:
        raise NotImplementedError

    @abstractmethod
    async def lista_sinteticos(self) -> Sequence[Indice]:
        raise NotImplemented

    @abstractmethod
    async def get_by_nome(self, nome: str) -> Indice | None:
        raise NotImplementedError

    @abstractmethod
    async def get_cotacao(
        self,
        indice_id: int,
        data_referente: date,
        codigo_moeda: str | None = None,
    ) -> IndiceCotacao | None:
        raise NotImplementedError

    @abstractmethod
    async def insere_cotacoes_indices(
        self, indices_cotacoes: list[IndiceCotacaoSchema]
    ) -> Sequence[IndiceCotacao]:
        raise NotImplementedError


class IndicesRepositoryImpl(IndicesRepository):
    __base_repository: BaseRepository[Indice]

    def __init__(self, base_repository: BaseRepository[Indice]):
        self.__base_repository = base_repository

    async def lista(self) -> Sequence[Indice]:
        query = select(Indice)

        results = await self.__base_repository.get_db_session().execute(query)
        return results.unique().scalars().all()

    async def lista_indices_sem_cotacoes(self) -> Sequence[Indice]:
        query = (
            select(Indice)
            .join(Moeda, Indice.moeda_principal_id == Moeda.id)
            .outerjoin(IndiceCotacao, Indice.id == IndiceCotacao.indice_id)
            .where(IndiceCotacao.id == None)
        )

        results = await self.__base_repository.get_db_session().execute(query)
        return results.unique().scalars().all()

    async def lista_sinteticos(self) -> Sequence[Indice]:
        query = select(Indice).where(Indice.is_sintetico)

        results = await self.__base_repository.get_db_session().execute(query)
        return results.unique().scalars().all()

    async def lista_by_identificadores(
        self, identificadores: list[str]
    ) -> Sequence[Indice]:
        query = select(Indice).where(
            Indice.identificadores.any(IndiceIdentificador.codigo.in_(identificadores))
        )

        results = await self.__base_repository.get_db_session().execute(query)
        return results.scalars().all()

    async def lista_by_nomes(self, nomes: list[str]) -> Sequence[Indice]:
        query = select(Indice).where(Indice.nome.in_(nomes))

        results = await self.__base_repository.get_db_session().execute(query)
        return results.scalars().all()

    async def get_by_nome(self, nome: str) -> Indice | None:
        query = select(Indice).where(Indice.nome == nome)

        result = await self.__base_repository.get_db_session().execute(query)
        return result.unique().scalar_one_or_none()

    async def get_cotacao(
        self,
        indice_id: int,
        data_referente: date,
        codigo_moeda: str | None = None,
    ) -> IndiceCotacao | None:
        if codigo_moeda is None:
            codigo_moeda = "BRL"

        query = (
            select(IndiceCotacao)
            .join(Moeda)
            .where(IndiceCotacao.indice_id == indice_id)
            .where(IndiceCotacao.data_referente == data_referente)
            .where(Moeda.codigo == codigo_moeda)
        )

        result = await self.__base_repository.get_db_session().execute(query)
        return result.unique().scalar_one_or_none()

    async def insere_cotacoes_indices(
        self,
        indices_cotacoes: list[IndiceCotacaoSchema],
    ) -> Sequence[IndiceCotacao]:
        if len(indices_cotacoes) == 0:
            return []

        TAMANHO_LOTE: int = 1000
        cotacoes_dicts: list[dict] = []

        ids_cotacoes_inseridas: list[int] = []
        cotacoes_inseridas: list[IndiceCotacao] = []

        insert_query_template = (
            insert(IndiceCotacao)
            .on_conflict_do_update(
                index_elements=["indice_id", "moeda_id", "data_referente"],
                set_={
                    "indice_id": insert(IndiceCotacao).excluded.indice_id,
                    "fonte_dado_id": insert(IndiceCotacao).excluded.fonte_dado_id,
                    "moeda_id": insert(IndiceCotacao).excluded.moeda_id,
                    "data_referente": insert(IndiceCotacao).excluded.data_referente,
                    "cotacao": insert(IndiceCotacao).excluded.cotacao,
                },
            )
            .returning(IndiceCotacao.id)
        )

        for lote_cotacoes in self.__get_lotes(indices_cotacoes, TAMANHO_LOTE):
            cotacoes_dicts = [
                {
                    "indice_id": cotacao.indice_id,
                    "fonte_dado_id": cotacao.fonte_dado_id,
                    "moeda_id": cotacao.moeda_id,
                    "data_referente": cotacao.data_referente,
                    "cotacao": cotacao.cotacao,
                }
                for cotacao in lote_cotacoes
            ]

            if not cotacoes_dicts:
                continue

            ids_lote_results = await self.__base_repository.get_db_session().execute(
                insert_query_template, cotacoes_dicts
            )
            ids_lote = ids_lote_results.scalars().all()
            ids_cotacoes_inseridas.extend(ids_lote)

        if not ids_cotacoes_inseridas:
            return []

        select_query_template = select(IndiceCotacao).options(
            selectinload(IndiceCotacao.indice),
            selectinload(IndiceCotacao.fonte_dados),
            selectinload(IndiceCotacao.moeda),
        )

        for lote_ids in self.__get_lotes(ids_cotacoes_inseridas, TAMANHO_LOTE):
            if not lote_ids:
                continue

            query = select_query_template.where(IndiceCotacao.id.in_(lote_ids))
            cotacoes_inseridas_results = (
                await self.__base_repository.get_db_session().execute(query)
            )

            cotacoes_inseridas.extend(cotacoes_inseridas_results.scalars().all())

        return cotacoes_inseridas

    def __get_lotes(self, dados: list, tamanho_lote: int):
        for i in range(0, len(dados), tamanho_lote):
            yield dados[i : i + tamanho_lote]
