import logging
import urllib.parse
from datetime import date, datetime
from decimal import Decimal
from httpx import Response
from typing import Any, Literal

from modules.integrations.enums import FontesDadosEnum
from modules.integrations.connectors import IntegrationsIndicesConnector
from modules.integrations.api.client import IntegrationApiClient
from modules.integrations.api.client_factory import IntegrationApiClientFactory
from modules.indices.model import Indice, IndiceCollection, IndiceIdentificador
from modules.rotinas.indices.coleta.schema import (
    ColetaIndiceCotacaoSchema,
    ColetaIndiceCotacaoSchemaCollection,
)
from modules.moedas.model import Moeda
from modules.indices.repository import IndicesRepository
from modules.indices.model import IndiceCotacao
from modules.calculos.service import CalculosService
from modules.util.feriados_financeiros_numpy import feriados


class ComDinheiroApiConnector(IntegrationsIndicesConnector):
    __client: IntegrationApiClient

    def __init__(self):
        self.__client = IntegrationApiClientFactory.create(
            fonte_dados=FontesDadosEnum.COMDINHEIRO_API
        )

    async def fetch_indices_cotacoes_pontos(
        self,
        indices_repository: IndicesRepository,
        indices: IndiceCollection,
        data_inicio: date,
        data_fim: date,
        fonte_dado: FontesDadosEnum,
        moeda: Moeda,
    ) -> list[ColetaIndiceCotacaoSchema]:
        indices_cotacoes: list[ColetaIndiceCotacaoSchema] = []

        indices_nao_sinteticos: IndiceCollection = IndiceCollection(
            list(filter(lambda indice: indice.is_sintetico is False, indices))
        )
        indices_sinteticos: IndiceCollection = IndiceCollection(
            list(filter(lambda indice: indice.is_sintetico, indices))
        )

        if indices_sinteticos:
            indices_cotacoes.extend(
                await self.__fetch_indices_cotacoes(
                    indices=indices_sinteticos,
                    indices_repository=indices_repository,
                    moeda=moeda,
                    tipo_cotacao="retorno",
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    fonte_dado=fonte_dado,
                )
            )

        if indices_nao_sinteticos:
            indices_cotacoes.extend(
                await self.__fetch_indices_cotacoes(
                    indices=indices_nao_sinteticos,
                    indices_repository=indices_repository,
                    moeda=moeda,
                    tipo_cotacao="preco",
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    fonte_dado=fonte_dado,
                )
            )

        return indices_cotacoes

    async def __fetch_indices_cotacoes(
        self,
        indices_repository: IndicesRepository,
        indices: IndiceCollection,
        moeda: Moeda,
        tipo_cotacao: Literal["preco", "retorno"],
        data_inicio: date,
        data_fim: date,
        fonte_dado: FontesDadosEnum,
    ) -> ColetaIndiceCotacaoSchemaCollection:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        codigos_indices: list[str] = self.__get_enconded_codigos_tratados(
            self.__get_codigos_from_indices(indices)
        )
        body: dict[str, str] = self.__get_post_body(
            codigos_indices=codigos_indices,
            moeda=moeda.codigo,
            tipo_cotacao=tipo_cotacao,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )

        async with self.__client as client:
            response: Response = await client.post(
                endpoint="/v1/ep1/import-data",
                params=None,
                headers=headers,
                body=body,
            )
            response.raise_for_status()

        is_sintetico: bool = tipo_cotacao == "retorno"
        return await self.__get_indices_cotacoes_from_response(
            indices_repository=indices_repository,
            response=response,
            indices=indices,
            data_inicio=data_inicio,
            fonte_dado=fonte_dado,
            moeda=moeda,
            is_sintetico=is_sintetico,
        )

    def __get_post_body(
        self,
        codigos_indices: list[str],
        moeda: str,
        tipo_cotacao: Literal["preco", "retorno"],
        data_inicio: date,
        data_fim: date,
    ) -> dict[str, str]:
        body_endpoint: str = "HistoricoCotacao002.php"
        x_param: str = "+".join(codigos_indices)

        body_params: dict[str, str] = self.__get_post_body_params(
            moeda=moeda,
            data_inicio=data_inicio,
            data_fim=data_fim,
            info_desejada=tipo_cotacao,
        )
        body_url: str = (
            f"{body_endpoint}?&x={x_param}&{urllib.parse.urlencode(body_params)}"
        )

        body: dict[str, Any] = {"URL": body_url, "format": "json3"}
        return body

    def __get_post_body_params(
        self,
        moeda: str,
        data_inicio: date,
        data_fim: date,
        info_desejada: Literal["preco", "retorno", "numero_indice", "retorno_acum"],
    ) -> dict[str, str]:
        return {
            "data_ini": data_inicio.strftime("%d%m%Y"),
            "data_fim": data_fim.strftime("%d%m%Y"),
            "info_desejada": info_desejada,
            "pagina": "1",
            "d": moeda,
            "g": "0",
            "m": "0",
            "retorno": "discreto",
            "tipo_data": "du_br",
            "tipo_ajuste": "todosajustes",
            "num_casas": "2",
            "enviar_email": "0",
            "ordem_legenda": "1",
            "cabecalho_excel": "modo1",
            "classes_ativos": "z1ci99jj7473",
            "ordem_data": "0",
            "rent_acum": "rent_acum",
            "minY": "",
            "maxY": "",
            "deltaY": "",
            "preco_nd_ant": "0",
            "base_num_indice": "100",
            "flag_num_indice": "1",
            "eixo_x": "Data",
            "startX": "0",
            "max_list_size": "20",
            "line_width": "2",
            "titulo_grafico": "",
            "legenda_eixoy": "",
            "tipo_grafico": "line",
            "script": "",
            "tooltip": "unica",
        }

    def __get_codigos_from_indices(self, indices: IndiceCollection) -> list[str]:
        codigos_indices: list[str] = []

        for indice in indices:
            identificador: IndiceIdentificador | None = (
                indice.get_identificador_by_fonte_dado(FontesDadosEnum.COMDINHEIRO_API)
            )
            if identificador is None:
                logging.warning(
                    f"Identificador do índoce {indice.nome} não encontrado."
                )
                continue

            codigo: str = identificador.codigo
            codigos_indices.append(codigo)

        return codigos_indices

    def __get_enconded_codigos_tratados(self, codigos_indices: list[str]) -> list[str]:
        return list(map(lambda cod: cod.replace("+", "%BE"), codigos_indices))

    async def __get_indices_cotacoes_from_response(
        self,
        indices_repository: IndicesRepository,
        response: Response,
        indices: IndiceCollection,
        data_inicio: date,
        fonte_dado: FontesDadosEnum,
        moeda: Moeda,
        is_sintetico: bool,
    ) -> ColetaIndiceCotacaoSchemaCollection:
        response_json = response.json()
        tab1: dict = response_json["tables"]["tab1"]

        metadados_e_dados_cotacoes: list[dict] = []
        for linha in tab1.values():
            metadados_e_dados_cotacoes.append(linha)

        cotacoes_metadados: dict = metadados_e_dados_cotacoes[0]
        cotacoes_dados: list[dict] = metadados_e_dados_cotacoes[1:]
        cotacoes: ColetaIndiceCotacaoSchemaCollection = (
            ColetaIndiceCotacaoSchemaCollection([])
        )

        for i in range(len(cotacoes_dados)):
            linha_cotacoes = cotacoes_dados[i]
            data_referente: date = datetime.strptime(
                linha_cotacoes.pop("col0"), "%d/%m/%Y"
            ).date()
            for key in linha_cotacoes:
                identificador_indice: str = cotacoes_metadados[key]
                indice: Indice | None = indices.get_indice_by_fonte_dado_identificador(
                    nome_completo_fonte_dado=FontesDadosEnum.COMDINHEIRO_API.value,
                    codigo_identificador=identificador_indice,
                )
                if indice is None:
                    raise ValueError(
                        f'Índice de código identificador "{identificador_indice}" não encontrado. Nesse ponto do código, deveria ser garantido que o índice é encontrado.'
                    )
                valor_str: str = linha_cotacoes[key].replace(",", ".").replace(" ", "")

                data_ultima_cotacao: date = (
                    CalculosService.get_data_d_util_menos_x_dias(
                        x_dias=indice.atraso_coleta_dias,
                        data_input=datetime.today().date(),
                        feriados=feriados,
                    )
                )
                if (
                    valor_str == "nd"
                    or data_referente < indice.data_inicio_coleta
                    or data_referente > data_ultima_cotacao
                ):
                    continue

                if is_sintetico:
                    indice_data_inicio_coleta_d1: date = (
                        CalculosService.get_data_d_util_mais_x_dias(
                            x_dias=1,
                            data_input=indice.data_inicio_coleta,
                        )
                    )
                    if data_referente <= indice.data_inicio_coleta:
                        continue
                    elif (
                        data_referente == data_inicio
                        or data_referente == indice_data_inicio_coleta_d1
                    ):
                        indice_cotacao_base: IndiceCotacao | None = (
                            await indices_repository.get_cotacao(
                                indice_id=indice.id,
                                data_referente=CalculosService.get_data_d_util_menos_x_dias(
                                    x_dias=1,
                                    data_input=data_referente,
                                    feriados=feriados,
                                ),
                            )
                        )
                        if indice_cotacao_base is None:
                            raise ValueError(
                                f'Índice de código identificador "{identificador_indice}" possui pelo menos uma cotação em dia útil válido faltante. Insira no Banco de Dados todas as cotações referente ao período.'
                            )
                        preco_cotacao: Decimal = self.__get_cotacao_sintetica(
                            cotacao_base=indice_cotacao_base.cotacao,
                            retorno_str=valor_str,
                        )
                    else:
                        cotacao_base: ColetaIndiceCotacaoSchema | None = (
                            cotacoes.get_indice_ultima_cotacao(indice.nome)
                        )
                        if cotacao_base is None:
                            raise ValueError(
                                f'Índice de código identificador "{identificador_indice}" possui pelo menos uma cotação em dia útil válido faltante. Esse índice deveria ter sido enconrtado no array de cotações.'
                            )
                        preco_cotacao: Decimal = self.__get_cotacao_sintetica(
                            cotacao_base=cotacao_base.cotacao, retorno_str=valor_str
                        )
                else:
                    cotacao_str: str = (
                        linha_cotacoes[key].replace(",", ".").replace(" ", "")
                    )
                    preco_cotacao: Decimal = self.__get_cotacao(cotacao_str)

                cotacao: ColetaIndiceCotacaoSchema = ColetaIndiceCotacaoSchema(
                    data_referente=data_referente,
                    nome_indice=indice.nome,
                    cotacao=preco_cotacao,
                    moeda=moeda.codigo,
                    fonte_dado=fonte_dado.value,
                )
                cotacoes.append(cotacao)

        return cotacoes

    def __get_cotacao_sintetica(
        self, cotacao_base: Decimal, retorno_str: str
    ) -> Decimal:
        retorno_dia: Decimal = Decimal(retorno_str)

        # Rent = (ValorFinal - ValorInicial) / ValorInicial
        # Para obter o ValorFinal, basta isolá-lo:
        # ValorFinal = ValorInicial * (Rent + 1)
        cotacao: Decimal = cotacao_base * (retorno_dia + 1)
        return cotacao

    def __get_cotacao(self, cotacao_str: str) -> Decimal:
        cotacao: Decimal = Decimal(cotacao_str)
        return cotacao
