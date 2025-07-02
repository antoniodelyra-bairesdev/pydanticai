from abc import ABC, abstractmethod
from decimal import Decimal

from .model import IndiceCotacao
from .schema import (
    IndiceSchema,
    IndiceCotacaoSchema,
    PostCotacoesAvisoSchema,
    PostCotacoesResponseSchema,
    PostCotacoesSinteticosBaseAvisoSchema,
    PostCotacoesSinteticosBaseResponseSchema,
)
from .repository import IndicesRepository
from modules.moedas.repository import MoedasRepository
from modules.moedas.model import Moeda, MoedaCotacao, MoedaCollection
from modules.indices.model import Indice, IndiceCollection
from modules.fontes_dados.model import FonteDados, FonteDadosCollection
from modules.fontes_dados.repository import FontesDadosRepository
from modules.rotinas.indices.coleta.schema import ColetaIndiceCotacaoSchema


class IndiceService(ABC):
    @abstractmethod
    async def get_indices_sem_cotacoes(self) -> list[IndiceSchema]:
        raise NotImplementedError

    @abstractmethod
    async def insere_cotacoes(
        self,
        cotacoes_indices: list[ColetaIndiceCotacaoSchema],
    ) -> PostCotacoesResponseSchema:
        raise NotImplementedError

    @abstractmethod
    async def insere_cotacoes_base_indices_sinteticos(
        self,
    ) -> PostCotacoesSinteticosBaseResponseSchema:
        raise NotImplementedError


class IndiceServiceImpl(IndiceService):
    __indices_repository: IndicesRepository
    __moedas_repository: MoedasRepository
    __MSG_COTACAO_NAO_SALVA: str = "Essa cotação não foi salva no banco de dados."
    __COTACAO_BASE_INDICE_SINTETICO_BRL: Decimal = Decimal(100)

    def __init__(
        self,
        fontes_dados_repository: FontesDadosRepository,
        indices_repository: IndicesRepository,
        moedas_repository: MoedasRepository,
    ):
        self.__fontes_dados_repository = fontes_dados_repository
        self.__indices_repository = indices_repository
        self.__moedas_repository = moedas_repository

    async def get_indices_sem_cotacoes(self) -> list[IndiceSchema]:
        indices_sem_cotacoes: list[Indice] = list(
            await self.__indices_repository.lista_indices_sem_cotacoes()
        )
        indices_sem_cotacoes_schema: list[IndiceSchema] = [
            IndiceSchema.from_model(indice) for indice in indices_sem_cotacoes
        ]

        return indices_sem_cotacoes_schema

    async def insere_cotacoes(
        self, cotacoes_indices: list[ColetaIndiceCotacaoSchema]
    ) -> PostCotacoesResponseSchema:
        cotacoes_indices_tratados: list[IndiceCotacaoSchema] = []
        cotacoes_nao_inseridas: list[ColetaIndiceCotacaoSchema] = []

        indices: IndiceCollection = IndiceCollection(
            list(await self.__indices_repository.lista())
        )
        fontes_dados: FonteDadosCollection = FonteDadosCollection(
            list(await self.__fontes_dados_repository.lista())
        )
        moedas: MoedaCollection = MoedaCollection(
            list(await self.__moedas_repository.lista())
        )

        avisos: list[PostCotacoesAvisoSchema] = []

        for cotacao in cotacoes_indices:
            fonte_dado: FonteDados | None = fontes_dados.get_by_nome_completo(
                cotacao.fonte_dado
            )
            moeda: Moeda | None = moedas.get_by_codigo(cotacao.moeda)
            indice: Indice | None = indices.get_indice_by_nome(cotacao.nome_indice)

            if fonte_dado is None:
                avisos.append(
                    PostCotacoesAvisoSchema(
                        mensagem=f"Fonte dado {cotacao.fonte_dado} não encontrada. {self.__MSG_COTACAO_NAO_SALVA}",
                        indice_cotacao_afetada=cotacao,
                    )
                )
            if moeda is None:
                avisos.append(
                    PostCotacoesAvisoSchema(
                        mensagem=f"Moeda {cotacao.moeda} não encontrada. {self.__MSG_COTACAO_NAO_SALVA}",
                        indice_cotacao_afetada=cotacao,
                    )
                )
            if indice is None:
                avisos.append(
                    PostCotacoesAvisoSchema(
                        mensagem=f"Índice {cotacao.nome_indice} não encontrado. {self.__MSG_COTACAO_NAO_SALVA}",
                        indice_cotacao_afetada=cotacao,
                    )
                )

            if fonte_dado is None or moeda is None or indice is None:
                cotacoes_nao_inseridas.append(cotacao)
                continue

            cotacao_tratada: IndiceCotacaoSchema = IndiceCotacaoSchema(
                id=None,
                data_referente=cotacao.data_referente,
                cotacao=cotacao.cotacao,
                indice_id=indice.id,
                indice=indice.nome,
                fonte_dado_id=fonte_dado.id,
                fonte_dado=fonte_dado.get_nome_completo_fonte_dados(),
                moeda_id=moeda.id,
                moeda=moeda.codigo,
            )

            cotacoes_indices_tratados.append(cotacao_tratada)

        cotacoes_indices_inseridas: list[IndiceCotacao] = list(
            await self.__indices_repository.insere_cotacoes_indices(
                cotacoes_indices_tratados
            )
        )

        cotacoes_indices_inseridas_schema: list[IndiceCotacaoSchema] = [
            IndiceCotacaoSchema.from_model(cotacao_inserida)
            for cotacao_inserida in cotacoes_indices_inseridas
        ]

        return PostCotacoesResponseSchema(
            cotacoes_inseridas=sorted(
                cotacoes_indices_inseridas_schema,
                key=lambda cotacao: (cotacao.data_referente, cotacao.indice),
            ),
            cotacoes_nao_inseridas=sorted(
                cotacoes_nao_inseridas,
                key=lambda cotacao: (cotacao.data_referente, cotacao.nome_indice),
            ),
            avisos=avisos,
        )

    async def insere_cotacoes_base_indices_sinteticos(
        self,
    ) -> PostCotacoesSinteticosBaseResponseSchema:
        indices_sinteticos: IndiceCollection = IndiceCollection(
            list(await self.__indices_repository.lista_sinteticos())
        )
        if not indices_sinteticos:
            return PostCotacoesSinteticosBaseResponseSchema(
                avisos=[
                    PostCotacoesSinteticosBaseAvisoSchema(
                        mensagem="Não foi encontrado nenhum índice sintético no Banco de Dados.",
                        indice_afetado="",
                    )
                ],
                cotacoes_inseridas=[],
            )

        moedas: MoedaCollection = MoedaCollection(
            list(await self.__moedas_repository.lista())
        )
        fonte_dado_manual: FonteDados = (
            await self.__fontes_dados_repository.get_fonte_dado_icatuvanguarda_manual()
        )

        avisos: list[PostCotacoesSinteticosBaseAvisoSchema] = []

        indices_cotacoes: list[IndiceCotacaoSchema] = []
        for indice in indices_sinteticos:
            for moeda in moedas:
                cotacao_indice: IndiceCotacao | None = (
                    await self.__indices_repository.get_cotacao(
                        indice_id=indice.id,
                        data_referente=indice.data_inicio_coleta,
                        codigo_moeda=moeda.codigo,
                    )
                )
                if cotacao_indice:
                    avisos.append(
                        PostCotacoesSinteticosBaseAvisoSchema(
                            mensagem=f"Cotação base de {indice.nome} em {moeda.codigo} já existe. Nada foi feito.",
                            indice_afetado=indice.nome,
                        )
                    )
                    continue

                if moeda.codigo == "BRL":
                    cotacao_base: Decimal = Decimal(
                        self.__COTACAO_BASE_INDICE_SINTETICO_BRL
                    )
                else:
                    cotacao_moeda: MoedaCotacao | None = (
                        await self.__moedas_repository.get_cotacao(
                            moeda.codigo, indice.data_inicio_coleta
                        )
                    )
                    if cotacao_moeda is None:
                        avisos.append(
                            PostCotacoesSinteticosBaseAvisoSchema(
                                mensagem=f"""A cotação base em {moeda.codigo} do índice {indice.nome} não pode ser inserida no Banco de Dados, pois não foi encontrada a cotação de {indice.data_inicio_coleta} em {moeda.codigo}""",
                                indice_afetado=indice.nome,
                            )
                        )
                        continue

                    cotacao_base: Decimal = Decimal(
                        self.__COTACAO_BASE_INDICE_SINTETICO_BRL * cotacao_moeda.cotacao
                    )

                indice_cotacao: IndiceCotacaoSchema = IndiceCotacaoSchema(
                    id=None,
                    data_referente=indice.data_inicio_coleta,
                    cotacao=cotacao_base,
                    indice_id=indice.id,
                    indice=indice.nome,
                    fonte_dado_id=fonte_dado_manual.id,
                    fonte_dado=fonte_dado_manual.get_nome_completo_fonte_dados(),
                    moeda_id=moeda.id,
                    moeda=moeda.codigo,
                )
                indices_cotacoes.append(indice_cotacao)

        cotacoes_inseridas: list[IndiceCotacao] = list(
            (
                await self.__indices_repository.insere_cotacoes_indices(
                    indices_cotacoes=indices_cotacoes
                )
            )
        )
        cotacoes_inseridas_schemas: list[IndiceCotacaoSchema] = [
            IndiceCotacaoSchema.from_model(cotacao_inserida)
            for cotacao_inserida in cotacoes_inseridas
        ]

        return PostCotacoesSinteticosBaseResponseSchema(
            avisos=avisos,
            cotacoes_inseridas=sorted(
                cotacoes_inseridas_schemas, key=lambda cotacao: cotacao.indice
            ),
        )
