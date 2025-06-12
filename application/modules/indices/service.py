from abc import ABC, abstractmethod

from .model import IndiceCotacao
from .schema import IndiceCotacaoSchema, AvisoSchema, PostResponseSchma
from .repository import IndicesRepository
from modules.moedas.repository import MoedasRepository
from modules.moedas.model import Moeda, MoedaCollection
from modules.indices.model import Indice, IndiceCollection
from modules.fontes_dados.model import FonteDados, FonteDadosCollection
from modules.fontes_dados.repository import FontesDadosRepository
from modules.rotinas.indices.coleta.schema import ColetaIndiceCotacaoSchema


class IndiceService(ABC):
    @abstractmethod
    async def insere_cotacoes(
        self,
        cotacoes_indices: list[ColetaIndiceCotacaoSchema],
    ) -> list[IndiceCotacaoSchema]:
        raise NotImplementedError


class IndiceServiceImpl(IndiceService):
    __indices_repository: IndicesRepository
    __moedas_repository: MoedasRepository
    __MSG_COTACAO_NAO_SALVA: str = "Essa cotação não foi salva no banco de dados."

    def __init__(
        self,
        fontes_dados_repository: FontesDadosRepository,
        indices_repository: IndicesRepository,
        moedas_repository: MoedasRepository,
    ):
        self.__fontes_dados_repository = fontes_dados_repository
        self.__indices_repository = indices_repository
        self.__moedas_repository = moedas_repository

    async def insere_cotacoes(
        self, cotacoes_indices: list[ColetaIndiceCotacaoSchema]
    ) -> PostResponseSchma:
        cotacoes_indices_tratados: list[IndiceCotacaoSchema] = []
        cotacoes_nao_inseridas: list[ColetaIndiceCotacaoSchema] = []

        fontes_dados: FonteDadosCollection = FonteDadosCollection(
            list(await self.__fontes_dados_repository.lista())
        )
        moedas: MoedaCollection = MoedaCollection(
            list(await self.__moedas_repository.lista())
        )
        indices: IndiceCollection = IndiceCollection(
            list(await self.__indices_repository.lista())
        )

        avisos: list[AvisoSchema] = []

        for cotacao in cotacoes_indices:
            fonte_dado: FonteDados | None = fontes_dados.get_by_nome_completo(
                cotacao.fonte_dado
            )
            moeda: Moeda | None = moedas.get_by_codigo(cotacao.moeda)
            indice: Indice | None = indices.get_indice_by_nome(cotacao.nome_indice)

            if fonte_dado is None:
                avisos.append(
                    AvisoSchema(
                        mensagem=f"Fonte dado {cotacao.fonte_dado} não encontrada. {self.__MSG_COTACAO_NAO_SALVA}",
                        indice_cotacao_afetada=cotacao,
                    )
                )
            if moeda is None:
                avisos.append(
                    AvisoSchema(
                        mensagem=f"Moeda {cotacao.moeda} não encontrada. {self.__MSG_COTACAO_NAO_SALVA}",
                        indice_cotacao_afetada=cotacao,
                    )
                )
            if indice is None:
                avisos.append(
                    AvisoSchema(
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

        return PostResponseSchma(
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
