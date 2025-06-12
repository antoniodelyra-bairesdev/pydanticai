import logging
import math
from modules.calculos.service import CalculosService
from modules.rentabilidades.service import RentabilidadesService
import pandas as pd

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from http import HTTPStatus
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from scipy.interpolate import CubicSpline
from numpy import busday_offset

from ..util.datas import contar_du, is_dia_util
from ..util.planilhas import Aba, Planilha, Coluna, Fmt
from ..util.math import acumular, curva_di_interpolada

from .repository import IndicadoresRepository
from modules.rotinas.repository import RotinaRepository
from modules.rotinas.model import CURVA_DI, CURVA_NTNB, DAP
from modules.util.feriados_financeiros_numpy import feriados

from .schema import (
    AjusteDAPDetailsSchema,
    AjusteDAPSchema,
    AtualizacaoIGPMProjecaoSchema,
    AtualizacaoIPCAProjecaoSchema,
    AtualizarAjusteDAPSchema,
    AtualizarPontoCurvaDISchema,
    AtualizarPontoCurvaNTNBSchema,
    CurvaDIResponse,
    CurvaNTNBResponse,
    HistoricoCDISchema,
    HistoricoIGPMSchema,
    HistoricoIPCASchema,
    IGPMProjecaoSchema,
    IPCAProjecaoSchema,
    PontoCurvaNTNBSchema,
    SalvarIGPMRequest,
    SalvarIPCARequest,
    TaxasIndicativasDetailsSchema,
    TaxasIndicativasSchema,
)
from .types import CurvaDI, CurvaNTNB


@dataclass
class IndicadoresService:
    indicadores_repository: IndicadoresRepository
    rotinas_repository: RotinaRepository

    async def indicadores(self):
        indicadores = (
            await self.indicadores_repository.lista_indices_benchmark_ids_nomes()
        )
        return indicadores

    async def curva_di(self, data: date) -> CurvaDI:
        dias_conhecidos: list[int] = []
        valores_conhecidos: list[float] = []

        if not is_dia_util(data):
            raise HTTPException(
                HTTPStatus.NOT_FOUND, "A data informada não é um dia útil"
            )

        pontos = await self.indicadores_repository.curva_di(data)

        if len(pontos) < 2:
            raise HTTPException(HTTPStatus.NOT_FOUND)

        data_encontrada = pontos[0].data
        rotina = await self.rotinas_repository.ultima_atualizacao(
            CURVA_DI, data_encontrada
        )

        for ponto in pontos:
            dias_conhecidos.append(ponto.dias_corridos)
            valores_conhecidos.append(float(ponto.taxa))

        return CurvaDI(
            funcao=CubicSpline(dias_conhecidos, valores_conhecidos),
            dominio=set(dias_conhecidos),
            atualizacao=rotina.atualizacao if rotina else None,
            data=busday_offset(
                data_encontrada, offsets=-1, roll="backward", holidays=feriados
            ).astype(date),
        )

    async def curva_di_interpolada(self, data: date) -> CurvaDIResponse:
        curva = await self.curva_di(data)
        return curva_di_interpolada(curva)

    async def curva_di_interpolada_xlsx(self, data: date):
        dados = await self.curva_di_interpolada(data)
        now = datetime.today()

        return Planilha(
            nome=f"Curva DI {dados.dia.strftime('%Y-%m-%d')} - Gerado em {now}",
            abas=[
                Aba(
                    nome=f"Curva DI {dados.dia.strftime('%d-%m-%Y')}",
                    colunas=[
                        Coluna(
                            titulo="Data de Referência",
                            formatacao=[Fmt.CENTRALIZAR, Fmt.DATA],
                        ),
                        Coluna(
                            titulo="Dias Úteis",
                            formatacao=[Fmt.CENTRALIZAR, Fmt.INTEIRO],
                        ),
                        Coluna(
                            titulo="Dias Corridos",
                            formatacao=[Fmt.CENTRALIZAR, Fmt.INTEIRO],
                        ),
                        Coluna(
                            titulo="Taxa",
                            formatacao=[Fmt.CENTRALIZAR, Fmt.DECIMAL(2)],
                        ),
                        Coluna(
                            titulo="Interpolação",
                            formatacao=[Fmt.CENTRALIZAR],
                        ),
                    ],
                    dados=[
                        [
                            linha.data_referencia,
                            linha.dias_uteis,
                            linha.dias_corridos,
                            linha.taxa,
                            linha.interpolado,
                        ]
                        for linha in dados.curva
                    ],
                )
            ],
        )

    async def atualizar_curva_di(
        self, data: date, pontos: list[AtualizarPontoCurvaDISchema]
    ):
        await self.indicadores_repository.atualizar_curva_di(
            busday_offset(data, offsets=1, roll="forward", holidays=feriados).astype(
                date
            ),
            [
                {
                    "dias_corridos": ponto.dias_corridos,
                    "taxa": ponto.taxa,
                }
                for ponto in pontos
            ],
            commit=False,
        )
        # await self.rotinas_repository.atualizar_rotina(CURVA_DI, data, commit=True)

    async def curva_ntnb(self, data: date) -> CurvaNTNB:
        if not is_dia_util(data):
            raise HTTPException(
                HTTPStatus.NOT_FOUND, "A data informada não é um dia útil"
            )

        daps = list(await self.indicadores_repository.ajuste_dap(data))
        ntnbs = list(await self.indicadores_repository.curva_ntnb(data))

        if len(daps) < 2 or len(ntnbs) < 2:
            raise HTTPException(
                HTTPStatus.NOT_FOUND, "Não há pontos suficientes para a interpolação"
            )

        data_dap = daps[0].data_referencia
        data_ntnb = ntnbs[0].data_referencia
        rotina_dap = await self.rotinas_repository.ultima_atualizacao(DAP, data_dap)
        rotina_ntnb = await self.rotinas_repository.ultima_atualizacao(
            CURVA_NTNB, data_ntnb
        )

        return CurvaNTNB(
            atualizacao_dap=rotina_dap.atualizacao if rotina_dap else None,
            atualizacao_ntnb=rotina_ntnb.atualizacao if rotina_ntnb else None,
            data_dap=data_dap,
            data_ntnb=data_ntnb,
            ajustes_dap=daps,
            taxas_indicativas=ntnbs,
        )

    async def curva_ntnb_interpolada(self, data: date) -> CurvaNTNBResponse:
        curva = await self.curva_ntnb(data)

        menor_ntnb = curva.taxas_indicativas[0]

        daps = curva.ajustes_dap[:2]
        janeiros = [dap for dap in curva.ajustes_dap if dap.data_vencimento.month == 1]
        if len(janeiros) > 0 and janeiros[0] not in daps:
            daps.append(janeiros[0])

        pontos_conhecidos = daps + curva.taxas_indicativas
        pontos_conhecidos.sort(key=lambda tx: tx.duration)

        datas_vencimento_daps_utilizados = set([dap.data_vencimento for dap in daps])

        durations_conhecidas = [ponto.duration for ponto in pontos_conhecidos]
        taxas_conhecidas = [ponto.taxa for ponto in pontos_conhecidos]

        f_interpolar = CubicSpline(durations_conhecidas, taxas_conhecidas)

        ultima_duration = curva.taxas_indicativas[-1].duration

        durations = [dia for dia in range(1, int(ultima_duration) + 2)]
        taxas = f_interpolar(durations)

        pontos: list[PontoCurvaNTNBSchema] = []

        for i in range(len(durations)):
            duration = durations[i]
            taxa = taxas[i]
            pontos.append(PontoCurvaNTNBSchema(duration=duration, taxa=taxa))

        return CurvaNTNBResponse(
            data=data,
            ajustes_dap=AjusteDAPDetailsSchema(
                data_referencia=curva.data_dap,
                atualizacao=curva.atualizacao_dap,
                dados=[
                    AjusteDAPSchema(
                        duration=dap.duration,
                        taxa=float(dap.taxa),
                        data_vencimento=dap.data_vencimento,
                        utilizado=dap.data_vencimento
                        in datas_vencimento_daps_utilizados,
                    )
                    for dap in curva.ajustes_dap
                ],
            ),
            taxas_indicativas=TaxasIndicativasDetailsSchema(
                data_referencia=curva.data_ntnb,
                atualizacao=curva.atualizacao_ntnb,
                dados=[
                    TaxasIndicativasSchema(
                        duration=ntnb.duration,
                        taxa=float(ntnb.taxa),
                        data_vencimento=ntnb.data_vencimento,
                    )
                    for ntnb in curva.taxas_indicativas
                ],
            ),
            curva=pontos,
        )

    async def curva_ntnb_xlsx(self, data: date):
        data_ref = data.strftime("%Y-%m-%d")
        col_taxa = Coluna(
            titulo="Taxa", formatacao=[Fmt.CENTRALIZAR, Fmt.DECIMAL(2, 8)]
        )
        col_duration = Coluna(
            titulo="Duration", formatacao=[Fmt.CENTRALIZAR, Fmt.INTEIRO]
        )
        return Planilha(
            nome=f"Curva NTN-B {data_ref} - Gerado em {datetime.today()}",
            abas=[
                Aba(
                    nome="Taxas Indicativas",
                    colunas=[
                        Coluna(
                            titulo="Data de Vencimento",
                            formatacao=[Fmt.CENTRALIZAR, Fmt.DATA],
                        ),
                        col_taxa,
                        col_duration,
                    ],
                    dados=[],
                ),
                Aba(
                    nome="Ajustes DAP",
                    colunas=[
                        Coluna(titulo="Vencimento", formatacao=[Fmt.CENTRALIZAR]),
                        col_taxa,
                        col_duration,
                    ],
                    dados=[],
                ),
                Aba(nome="Curva NTN-B", colunas=[col_taxa, col_duration], dados=[]),
            ],
        )

    async def atualizar_taxas_indicativas_ntnb(
        self, data_referencia: date, ajustes: list[AtualizarPontoCurvaNTNBSchema]
    ):
        await self.indicadores_repository.atualizar_taxas_indicativas_ntnb(
            data_referencia, ajustes
        )
        # await self.rotinas_repository.atualizar_rotina(
        #     CURVA_NTNB, data_referencia, commit=True
        # )

    async def atualizar_ajustes_dap(
        self, data_referencia: date, ajustes: list[AtualizarAjusteDAPSchema]
    ):
        await self.indicadores_repository.atualizar_ajustes_dap(
            data_referencia, ajustes
        )
        # await self.rotinas_repository.atualizar_rotina(
        #     DAP, data_referencia, commit=True
        # )

    # Históricos e projeções

    # CDI

    async def cdi(self, intervalo: tuple[date, date] | None = None):
        historico = await self.indicadores_repository.cdi(intervalo)
        return [
            HistoricoCDISchema(
                data=atual.data,
                atualizacao=atual.atualizacao,
                indice=float((atual.taxa / 100 + 1) ** (1 / Decimal(252))),
                indice_acumulado=atual.indice_acumulado,
                taxa=atual.taxa,
            )
            for atual in historico
        ]

    async def inserir_cdi(self, data: date, taxa: Decimal):
        ultimo_cdi = await self.indicadores_repository.ultimo_cdi()
        if not ultimo_cdi:
            raise HTTPException(HTTPStatus.NOT_FOUND)
        if data <= ultimo_cdi.data:
            raise HTTPException(HTTPStatus.CONFLICT)
        indice_acumulado_anterior = ultimo_cdi.indice_acumulado
        indice_anterior = round((1 + float(ultimo_cdi.taxa) / 100) ** (1 / 252), 8)
        indice_acumulado = indice_acumulado_anterior * indice_anterior
        await self.indicadores_repository.inserir_cdi(data, taxa, indice_acumulado)

    async def cdi_acumulado(
        self,
        inicio_periodo: date,
        fim_periodo: date,
        valor: float,
        percentual: float,
        juros: float,
    ):
        periodo = await self.indicadores_repository.buscar_par_indices_acumulados(
            inicio_periodo, fim_periodo
        )
        if len(periodo) != 2:
            raise HTTPException(HTTPStatus.NOT_FOUND)
        inicio, fim = periodo
        fator = fim.indice_acumulado / inicio.indice_acumulado
        du = contar_du(inicio.data, fim.data)
        return acumular(fator, du, percentual, juros, du, valor)

    # IGPM

    async def igpm(
        self, intervalo: tuple[date, date] | None = None
    ) -> list[HistoricoIGPMSchema]:
        historico = await self.indicadores_repository.igpm(intervalo)
        if len(historico) < 2:
            raise HTTPException(HTTPStatus.NOT_FOUND)

        dados = []
        for i in range(1, len(historico)):
            anterior = historico[i - 1]
            atual = historico[i]

            acumulado = atual.indice_acumulado
            indice_mes = acumulado / anterior.indice_acumulado
            percentual = indice_mes - 1

            dados.append(
                HistoricoIGPMSchema(
                    data=atual.data,
                    atualizacao=atual.atualizacao,
                    indice_acumulado=acumulado,
                    indice_mes=indice_mes,
                    percentual=percentual,
                )
            )
        return dados

    async def igpm_projecao(self, intervalo: tuple[date, date] | None = None):
        projecoes = await self.indicadores_repository.igpm_projecao(intervalo)
        return [
            IGPMProjecaoSchema(
                data=projecao.data,
                projecao=projecao.taxa,
                indice=projecao.taxa + 1,
                projetado=projecao.projetado,
                atualizacao=projecao.atualizacao,
            )
            for projecao in projecoes
        ]

    async def atualizar_igpm_projecao(
        self, projecoes: list[AtualizacaoIGPMProjecaoSchema]
    ):
        await self.indicadores_repository.atualizar_igpm_projecao(projecoes)

    async def atualizar_igpm(self, indices_acumulados: list[SalvarIGPMRequest]):
        await self.indicadores_repository.salvar_igpm(indices_acumulados)

    # IPCA

    async def ipca(
        self, intervalo: tuple[date, date] | None = None
    ) -> list[HistoricoIPCASchema]:
        historico = await self.indicadores_repository.ipca(intervalo)
        if len(historico) < 2:
            raise HTTPException(HTTPStatus.NOT_FOUND)

        dados = []
        for i in range(1, len(historico)):
            anterior = historico[i - 1]
            atual = historico[i]

            acumulado = atual.indice_acumulado
            indice_mes = acumulado / anterior.indice_acumulado
            percentual = indice_mes - 1

            dados.append(
                HistoricoIPCASchema(
                    data=atual.data,
                    atualizacao=atual.atualizacao,
                    indice_acumulado=acumulado,
                    indice_mes=indice_mes,
                    percentual=percentual,
                )
            )
        return dados

    async def ipca_projecao(self, intervalo: tuple[date, date] | None = None):
        projecoes = await self.indicadores_repository.ipca_projecao(intervalo)
        return [
            IPCAProjecaoSchema(
                data=projecao.data,
                projecao=projecao.taxa,
                indice=projecao.taxa + 1,
                projetado=projecao.projetado,
                atualizacao=projecao.atualizacao,
            )
            for projecao in projecoes
        ]

    async def atualizar_ipca_projecao(
        self, projecoes: list[AtualizacaoIPCAProjecaoSchema]
    ):
        await self.indicadores_repository.atualizar_ipca_projecao(projecoes)

    async def atualizar_ipca(self, indices_acumulados: list[SalvarIPCARequest]):
        await self.indicadores_repository.salvar_ipca(indices_acumulados)

    async def indices_xlsx(self):
        ipca = await self.ipca()
        igpm = await self.igpm()
        ipca_proj = await self.ipca_projecao()
        igpm_proj = await self.igpm_projecao()

        cols_historico = [
            Coluna(titulo="Data", formatacao=[Fmt.CENTRALIZAR, Fmt.DATA]),
            Coluna(
                titulo="Índice acumulado",
                formatacao=[Fmt.CENTRALIZAR, Fmt.DECIMAL(2, 8)],
            ),
            Coluna(
                titulo="Índice mês",
                formatacao=[Fmt.CENTRALIZAR, Fmt.DECIMAL(2, 8)],
            ),
            Coluna(
                titulo="Percentual",
                formatacao=[Fmt.CENTRALIZAR, Fmt.DECIMAL(2, 8)],
            ),
        ]
        cols_projecao = [
            Coluna(
                titulo="Data",
                formatacao=[Fmt.CENTRALIZAR, Fmt.DATA],
            ),
            Coluna(
                titulo="Projeção",
                formatacao=[Fmt.CENTRALIZAR, Fmt.DECIMAL(2, 8)],
            ),
            Coluna(
                titulo="Índice",
                formatacao=[Fmt.CENTRALIZAR, Fmt.DECIMAL(2, 8)],
            ),
            Coluna(
                titulo="Tipo",
                formatacao=[Fmt.CENTRALIZAR],
            ),
        ]
        return Planilha(
            nome=f"Índices Inflação - Gerado em {datetime.today()}",
            abas=[
                Aba(
                    nome=f"IPCA",
                    colunas=cols_historico,
                    dados=[
                        [
                            linha.data,
                            linha.indice_acumulado,
                            linha.indice_mes,
                            linha.percentual,
                        ]
                        for linha in ipca
                    ],
                ),
                Aba(
                    nome=f"IGP-M",
                    colunas=cols_historico,
                    dados=[
                        [
                            linha.data,
                            linha.indice_acumulado,
                            linha.indice_mes,
                            linha.percentual,
                        ]
                        for linha in igpm
                    ],
                ),
                Aba(
                    nome=f"IPCA Projetado",
                    colunas=cols_projecao,
                    dados=[
                        [
                            linha.data,
                            linha.projecao,
                            linha.indice,
                            "Projeção" if linha.projetado else "Índice fechado",
                        ]
                        for linha in ipca_proj
                    ],
                ),
                Aba(
                    nome=f"IGP-M Projetado",
                    colunas=cols_projecao,
                    dados=[
                        [
                            linha.data,
                            linha.projecao,
                            linha.indice,
                            "Projeção" if linha.projetado else "Índice fechado",
                        ]
                        for linha in igpm_proj
                    ],
                ),
            ],
        )

    async def get_indicadores_benchmark_ids(self):
        indicadores_benchmark_ids = list(
            await self.indicadores_repository.lista_indices_benchmark_ids()
        )

        return indicadores_benchmark_ids

    async def get_indicadores_benchmark_rentabilidades(
        self,
        data_referencia: date | None,
        indices_benchmark_ids: list[int],
    ):
        if data_referencia is None:
            data_referencia = date.today()

        return await self.indicadores_repository.lista_indices_benchmark_rentabilidades_by_data_referencia(
            data_referencia=data_referencia, indices_benchmark_ids=indices_benchmark_ids
        )

    async def inserir_rentabilidades(
        self, arquivo_rentabilidades: UploadFile, *, persist=False
    ):
        ids_nomes_indices_benchmark = (
            await self.indicadores_repository.lista_indices_benchmark_ids_nomes()
        )
        dataframe = RentabilidadesService.get_dataframe(
            arquivo_rentabilidades=arquivo_rentabilidades.file,
            nome_sheet="Índices",
            skip_rows=4,
        )

        indices_benchmark_rentabilidades = []
        indices_benchmark_ids_inseridos: list[int] = []
        indices_benchmark_ids_nao_inseridos: list[int] = []

        for id_nome in ids_nomes_indices_benchmark:
            try:
                indice_benchmark_rentabilidade = (
                    self._get_indice_benchmark_rentabilidade(tuple(id_nome), dataframe)
                )

                indices_benchmark_rentabilidades.append(indice_benchmark_rentabilidade)
                indices_benchmark_ids_inseridos.append(id_nome[0])
            except Exception as e:
                if isinstance(e, KeyError):
                    logging.warn(
                        f"Índice {id_nome[0]} não encontrado na sheet de índices do arquivo enviado",
                        exc_info=True,
                    )
                else:
                    logging.error(
                        f"Houve um problema ao calcular as rentabilidades da cota do fundo {id_nome[0]}",
                        exc_info=True,
                    )

                indices_benchmark_ids_nao_inseridos.append(id_nome[0])
                continue

        if not persist:
            return indices_benchmark_rentabilidades

        await self.indicadores_repository.inserir_rentabilidades(
            indices_benchmark_rentabilidades
        )

        return {
            "indices_benchmark_id_rentabilidades_inseridos": indices_benchmark_ids_inseridos,
            "indices_benchmark_id_rentabilidades_nao_inseridos": indices_benchmark_ids_nao_inseridos,
        }

    def _get_indice_benchmark_rentabilidade(
        self,
        id_nome_indice: tuple[int, str],
        dataframe: pd.DataFrame,
    ) -> IndicadoresRepository.InserirIndiceBenchmarkRentabilidade:
        df = dataframe

        id_indice = id_nome_indice[0]
        nome_indice = self._get_nome_indice_dbfolder(id_nome_indice[1])

        QTD_DIAS_CORRIDOS = 365
        data_ultima_posicao: date = df[nome_indice].last_valid_index()  # type: ignore

        if id_nome_indice[1] == "CDI":
            data_ultima_posicao = CalculosService.get_data_d_util_menos_x_dias(
                x_dias=1, data_input=data_ultima_posicao, feriados=feriados
            )

        data_rentabilidade_dia = CalculosService.get_data_d_util_menos_x_dias(
            x_dias=1, data_input=data_ultima_posicao, feriados=feriados
        )

        data_rentabilidade_mes = CalculosService.get_ultimo_dia_util_mes_anterior(
            data_input=data_ultima_posicao,
        )

        data_rentabilidade_ano = CalculosService.get_ultimo_dia_util_ano_anterior(
            data_input=data_ultima_posicao,
        )

        data_rentabilidade_12m = CalculosService.get_data_d_util_menos_x_dias(
            x_dias=QTD_DIAS_CORRIDOS,
            data_input=data_ultima_posicao,
            feriados=feriados,
            roll="forward",
        )

        data_rentabilidade_24m = CalculosService.get_data_d_util_menos_x_dias(
            x_dias=QTD_DIAS_CORRIDOS * 2,
            data_input=data_ultima_posicao,
            feriados=feriados,
            roll="forward",
        )

        data_rentabilidade_36m = CalculosService.get_data_d_util_menos_x_dias(
            x_dias=QTD_DIAS_CORRIDOS * 3,
            data_input=data_ultima_posicao,
            feriados=feriados,
            roll="forward",
        )

        posicao_ultimo_indice = (
            None
            if math.isnan(df.loc[data_ultima_posicao, nome_indice]) == True  # type: ignore
            else df.loc[data_ultima_posicao, nome_indice]  # type: ignore
        )

        rentabilidade_dia = (
            posicao_ultimo_indice / df.loc[data_rentabilidade_dia, nome_indice]  # type: ignore
        )
        rentabilidade_mes = (
            posicao_ultimo_indice / df.loc[data_rentabilidade_mes, nome_indice]  # type: ignore
        )
        rentabilidade_ano = (
            posicao_ultimo_indice / df.loc[data_rentabilidade_ano, nome_indice]  # type: ignore
        )
        rentabilidade_12m = (
            posicao_ultimo_indice / df.loc[data_rentabilidade_12m, nome_indice]  # type: ignore
        )
        rentabilidade_24m = (
            posicao_ultimo_indice / df.loc[data_rentabilidade_24m, nome_indice]  # type: ignore
        )
        rentabilidade_36m = (
            posicao_ultimo_indice / df.loc[data_rentabilidade_36m, nome_indice]  # type: ignore
        )

        rentabilidade_dia = (
            None if math.isnan(rentabilidade_dia) == True else rentabilidade_dia
        )
        rentabilidade_mes = (
            None if math.isnan(rentabilidade_mes) == True else rentabilidade_mes
        )
        rentabilidade_ano = (
            None if math.isnan(rentabilidade_ano) == True else rentabilidade_ano
        )
        rentabilidade_12m = (
            None if math.isnan(rentabilidade_12m) == True else rentabilidade_12m
        )
        rentabilidade_24m = (
            None if math.isnan(rentabilidade_24m) == True else rentabilidade_24m
        )
        rentabilidade_36m = (
            None if math.isnan(rentabilidade_36m) == True else rentabilidade_36m
        )

        indice_benchmark_rentabilidade: (
            IndicadoresRepository.InserirIndiceBenchmarkRentabilidade
        ) = {
            "indice_benchmark_id": id_indice,
            "data_posicao": data_ultima_posicao,
            "rentabilidade_dia": rentabilidade_dia,
            "rentabilidade_mes": rentabilidade_mes,
            "rentabilidade_ano": rentabilidade_ano,
            "rentabilidade_12meses": rentabilidade_12m,
            "rentabilidade_24meses": rentabilidade_24m,
            "rentabilidade_36meses": rentabilidade_36m,
        }

        return indice_benchmark_rentabilidade

    def _get_nome_indice_dbfolder(self, nome_indice: str) -> str:
        if nome_indice == "CDI":
            return "CDI diário"
        if nome_indice == "Selic":
            return "Selic diário"
        if nome_indice == "IPCA":
            return "IPCA diário"
        if nome_indice == "IRFM1+":
            return "IRF-M 1+"
        if nome_indice == "Dólar":
            return "DOL CLEAN"
        if nome_indice == "IBX":
            return "IBrX"
        if nome_indice == "Ibovespa":
            return "IBOVESPA"

        return nome_indice
