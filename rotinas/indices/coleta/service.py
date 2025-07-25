import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import date

from .schema import (
    ColetaIndiceSchema,
    AvisoSchema,
    ColetaIndiceCotacaoSchema,
    ResponseSchema,
)
from modules.integrations.enums import FontesDadosEnum
from modules.integrations.connectors_factories import (
    IntegrationsIndicesConnectorFactory,
)
from modules.integrations.connectors import IntegrationsIndicesConnector
from modules.indices.repository import IndicesRepository
from modules.indices.model import Indice, IndiceCollection
from modules.rotinas.indices.coleta.schema import ColetaIndiceCotacaoSchema
from modules.moedas.model import Moeda
from modules.moedas.repository import MoedasRepository


class RotinaIndiceColetaService(ABC):
    @abstractmethod
    async def coleta_cotacoes_indices(
        self,
        data_inicio: date,
        data_fim: date,
        dados_indices_a_serem_coletados: list[ColetaIndiceSchema],
    ) -> ResponseSchema:
        raise NotImplementedError

    @abstractmethod
    async def coleta_cotacoes_todos_indices(
        self,
        data_inicio: date,
        data_fim: date,
    ) -> ResponseSchema:
        raise NotImplementedError

    @abstractmethod
    async def coleta_ultimas_cotacoes_todos_indices(self) -> ResponseSchema:
        raise NotImplementedError


class RotinaIndiceColetaServiceImpl(RotinaIndiceColetaService):
    __indices_repository: IndicesRepository
    __moedas_repository: MoedasRepository
    __integrations_connector_factory: IntegrationsIndicesConnectorFactory

    def __init__(
        self,
        indices_repository: IndicesRepository,
        moedas_repository: MoedasRepository,
        integrations_connector_factory: IntegrationsIndicesConnectorFactory,
    ):
        self.__indices_repository = indices_repository
        self.__moedas_repository = moedas_repository
        self.__integrations_connector_factory = integrations_connector_factory

    async def coleta_cotacoes_indices(
        self,
        data_inicio: date,
        data_fim: date,
        dados_indices_a_serem_coletados: list[ColetaIndiceSchema],
    ) -> ResponseSchema:
        indices_cotacoes: list[ColetaIndiceCotacaoSchema] = []
        avisos: list[AvisoSchema] = []

        todos_indices: IndiceCollection = IndiceCollection(
            list(await self.__indices_repository.lista())
        )

        nomes_indices_nao_encontrados: list[str] = (
            self.__get_nomes_indices_nao_encontrados(
                dados_indices_a_serem_coletados, todos_indices
            )
        )
        if nomes_indices_nao_encontrados:
            logging.warning(
                "Índices não encontrados no Banco de Dados: ",
                nomes_indices_nao_encontrados,
            )
            avisos.append(
                AvisoSchema(
                    mensagem="Índices não encontrados no Banco de Dados",
                    indices_afetados=nomes_indices_nao_encontrados,
                )
            )

        dados_indices_a_serem_coletados_encontrados: list[ColetaIndiceSchema] = list(
            filter(
                lambda indice: indice.indice not in nomes_indices_nao_encontrados,
                dados_indices_a_serem_coletados,
            )
        )

        if not dados_indices_a_serem_coletados_encontrados:
            return ResponseSchema(cotacoes=[], avisos=avisos)

        indices_a_serem_coletados_encontrados: list[
            tuple[ColetaIndiceSchema, Indice]
        ] = self.__get_dados_e_indices_a_serem_coletados(
            dados_indices=dados_indices_a_serem_coletados_encontrados,
            indices=todos_indices,
        )

        dados_e_indices_a_serem_coletados_por_fonte_e_moeda: dict[
            FontesDadosEnum, dict[str, IndiceCollection]
        ] = self.__get_indices_por_fonte_e_moeda_from_dados_indices(
            dados_indices_a_serem_coletados=indices_a_serem_coletados_encontrados,
        )

        for fonte_dado in dados_e_indices_a_serem_coletados_por_fonte_e_moeda.keys():
            connector: IntegrationsIndicesConnector = (
                self.__integrations_connector_factory.create(fonte_dado)
            )
            for (
                codigo_moeda,
                indices,
            ) in dados_e_indices_a_serem_coletados_por_fonte_e_moeda[
                fonte_dado
            ].items():
                moeda: Moeda | None = await self.__moedas_repository.get_by_codigo(
                    codigo_moeda
                )
                if moeda is None:
                    avisos.append(
                        AvisoSchema(
                            mensagem=f"Moeda {moeda} não encontrada no Banco de Dados.",
                            indices_afetados=indices.get_nomes(),
                        )
                    )
                    continue

                _indices_cotacoes: list[ColetaIndiceCotacaoSchema] = (
                    await connector.fetch_indices_cotacoes_pontos(
                        indices_repository=self.__indices_repository,
                        indices=indices,
                        data_inicio=data_inicio,
                        data_fim=data_fim,
                        moeda=moeda,
                        fonte_dado=fonte_dado,
                    )
                )
                indices_cotacoes.extend(_indices_cotacoes)

        indices_sem_cotacao: IndiceCollection = self.__get_indices_sem_cotacao(
            indices=IndiceCollection(
                [indice[1] for indice in indices_a_serem_coletados_encontrados]
            ),
            cotacoes=indices_cotacoes,
        )
        if indices_sem_cotacao:
            avisos.append(
                AvisoSchema(
                    mensagem="Não foram encontradas cotações do(s) Índice(s).",
                    indices_afetados=indices_sem_cotacao.get_nomes(),
                )
            )

        return ResponseSchema(
            cotacoes=sorted(
                indices_cotacoes,
                key=lambda cotacao: cotacao.data_referente,
            ),
            avisos=avisos,
        )

    async def coleta_cotacoes_todos_indices(
        self,
        data_inicio: date,
        data_fim: date,
    ) -> ResponseSchema:
        indices: IndiceCollection = IndiceCollection(
            list(await self.__indices_repository.lista())
        )

        (indices_cotacoes, avisos) = await self.__get_cotacoes_indices_e_avisos(
            indices=indices,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )

        indices_sem_cotacao: IndiceCollection = self.__get_indices_sem_cotacao(
            indices=indices, cotacoes=indices_cotacoes
        )
        if indices_sem_cotacao:
            avisos.append(
                AvisoSchema(
                    mensagem="Não foram encontradas cotações do(s) Índice(s).",
                    indices_afetados=indices_sem_cotacao.get_nomes(),
                )
            )

        return ResponseSchema(
            cotacoes=sorted(
                indices_cotacoes,
                key=lambda cotacao: cotacao.data_referente,
            ),
            avisos=avisos,
        )

    async def coleta_ultimas_cotacoes_todos_indices(self) -> ResponseSchema:
        avisos: list[AvisoSchema] = []

        indices: IndiceCollection = IndiceCollection(
            list(await self.__indices_repository.lista())
        )
        (data_inicio, data_fim) = indices.get_menor_e_maior_data_ultima_cotacao()

        (indices_cotacoes, avisos) = await self.__get_cotacoes_indices_e_avisos(
            indices=indices,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )

        ultimas_cotacoes: list[ColetaIndiceCotacaoSchema] = (
            self.__get_ultimas_cotacoes_from_cotacoes(
                cotacoes=indices_cotacoes, indices=indices
            )
        )
        indices_sem_cotacao: IndiceCollection = self.__get_indices_sem_cotacao(
            indices=indices, cotacoes=ultimas_cotacoes
        )
        if indices_sem_cotacao:
            avisos.append(
                AvisoSchema(
                    mensagem="Não foram encontradas cotações do(s) Índice(s).",
                    indices_afetados=indices_sem_cotacao.get_nomes(),
                )
            )

        return ResponseSchema(
            cotacoes=sorted(
                ultimas_cotacoes,
                key=lambda cotacao: cotacao.data_referente,
            ),
            avisos=avisos,
        )

    async def __get_cotacoes_indices_e_avisos(
        self, indices: IndiceCollection, data_inicio: date, data_fim: date
    ) -> tuple[list[ColetaIndiceCotacaoSchema], list[AvisoSchema]]:
        indices_cotacoes: list[ColetaIndiceCotacaoSchema] = []
        avisos: list[AvisoSchema] = []

        indices_por_fonte_e_moedas: dict[
            FontesDadosEnum, dict[str, IndiceCollection]
        ] = self.__get_indices_por_fonte_e_moeda(indices)

        for fonte_dado in indices_por_fonte_e_moedas.keys():
            connector: IntegrationsIndicesConnector = (
                self.__integrations_connector_factory.create(fonte_dado)
            )

            for codigo_moeda, indices in indices_por_fonte_e_moedas[fonte_dado].items():
                moeda: Moeda | None = await self.__moedas_repository.get_by_codigo(
                    codigo_moeda
                )
                if moeda is None:
                    avisos.append(
                        AvisoSchema(
                            mensagem=f"Moeda {moeda} não encontrada no Banco de Dados.",
                            indices_afetados=indices.get_nomes(),
                        )
                    )
                    continue

                _indices_cotacoes: list[ColetaIndiceCotacaoSchema] = (
                    await connector.fetch_indices_cotacoes_pontos(
                        indices_repository=self.__indices_repository,
                        indices=indices,
                        data_inicio=data_inicio,
                        data_fim=data_fim,
                        moeda=moeda,
                        fonte_dado=fonte_dado,
                    )
                )
                indices_cotacoes.extend(_indices_cotacoes)

        return (indices_cotacoes, avisos)

    def __get_nomes_indices_nao_encontrados(
        self,
        dados_indices_a_serem_coletados: list[ColetaIndiceSchema],
        todos_indices: IndiceCollection,
    ) -> list[str]:
        nomes_todos_indices: list[str] = [indice.nome for indice in todos_indices]
        nomes_indices_nao_encontrados: list[str] = []

        for dado_indice in dados_indices_a_serem_coletados:
            if dado_indice.indice not in nomes_todos_indices:
                nomes_indices_nao_encontrados.append(dado_indice.indice)

        return nomes_indices_nao_encontrados

    def __get_dados_e_indices_a_serem_coletados(
        self,
        dados_indices: list[ColetaIndiceSchema],
        indices: IndiceCollection,
    ) -> list[tuple[ColetaIndiceSchema, Indice]]:
        dados_e_indices: list[tuple[ColetaIndiceSchema, Indice]] = []

        for dado_indice in dados_indices:
            for indice in indices:
                if dado_indice.indice == indice.nome:
                    dados_e_indices.append((dado_indice, indice))

        return dados_e_indices

    def __get_indices_por_fonte_e_moeda_from_dados_indices(
        self,
        dados_indices_a_serem_coletados: list[tuple[ColetaIndiceSchema, Indice]],
    ) -> dict[FontesDadosEnum, dict[str, IndiceCollection]]:
        dados_indices_por_fonte_e_moeda: dict[
            FontesDadosEnum, dict[str, IndiceCollection]
        ] = defaultdict(lambda: defaultdict(IndiceCollection))

        for dado_indice_e_indice in dados_indices_a_serem_coletados:
            dado_indice: ColetaIndiceSchema = dado_indice_e_indice[0]
            indice: Indice = dado_indice_e_indice[1]

            try:
                fonte: FontesDadosEnum = FontesDadosEnum(dado_indice.fonte)
            except KeyError:
                logging.warning(
                    f"Fonte de dados {dado_indice.fonte} não cadastrada no código (FonteDadosEnum) ou no banco de dados. Pulando índice {dado_indice.indice}."
                )
                continue

            moeda: str = dado_indice.moeda
            dados_indices_por_fonte_e_moeda[fonte][moeda].append(indice)

        return dados_indices_por_fonte_e_moeda

    def __get_indices_sem_cotacao(
        self, indices: IndiceCollection, cotacoes: list[ColetaIndiceCotacaoSchema]
    ) -> IndiceCollection:
        indices_sem_cotacao: IndiceCollection = IndiceCollection([])
        for indice in indices:
            cotacoes_indice: list[ColetaIndiceCotacaoSchema] = list(
                filter(lambda cotacao: cotacao.nome_indice == indice.nome, cotacoes)
            )

            if len(cotacoes_indice) == 0:
                indices_sem_cotacao.append(indice)

        return indices_sem_cotacao

    def __get_indices_por_fonte_e_moeda(
        self, indices: IndiceCollection
    ) -> dict[FontesDadosEnum, dict[str, IndiceCollection]]:
        indices_por_fonte_e_moeda: dict[
            FontesDadosEnum, dict[str, IndiceCollection]
        ] = defaultdict(lambda: defaultdict(IndiceCollection))

        for indice in indices:
            try:
                nome_fonte: FontesDadosEnum = FontesDadosEnum(
                    indice.get_nome_fonte_dados()
                )
            except KeyError:
                logging.warning(
                    f"Fonte de dados {nome_fonte} não cadastrada no código (FonteDadosEnum) ou no banco de dados. Pulando índice {indice.nome}"
                )
                continue

            moeda: str = indice.get_codigo_moeda()
            indices_por_fonte_e_moeda[nome_fonte][moeda].append(indice)

        return indices_por_fonte_e_moeda

    def __get_ultimas_cotacoes_from_cotacoes(
        self, cotacoes: list[ColetaIndiceCotacaoSchema], indices: IndiceCollection
    ) -> list[ColetaIndiceCotacaoSchema]:
        ultimas_cotacoes: list[ColetaIndiceCotacaoSchema] = []
        for indice in indices:
            indice_data_ultima_cotacao: date = indice.get_data_ultima_cotacao()
            cotacoes_filtradas = [
                cotacao
                for cotacao in cotacoes
                if cotacao.nome_indice == indice.nome
                and cotacao.data_referente == indice_data_ultima_cotacao
            ]
            try:
                ultima_cotacao_do_indice: ColetaIndiceCotacaoSchema = (
                    cotacoes_filtradas[0]
                )
            except Exception as e:
                continue
            ultimas_cotacoes.append(ultima_cotacao_do_indice)

        return ultimas_cotacoes
