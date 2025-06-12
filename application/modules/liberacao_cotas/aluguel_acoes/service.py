from datetime import date
from io import BytesIO
from json import dumps
from pandas import DataFrame
from zipfile import ZipFile

from ..types import Log, LogMensagem
from ..service import LiberacaoCotasService
from .helper import AluguelAcoesHelper
from .types import (
    AluguelLinhaRelatorioAntecipacao,
    AluguelLinhaRelatorioBIP,
    AluguelTipoContrato,
)


class AluguelAcoesService(LiberacaoCotasService):
    __CODIGO_AGENTE_BRADESCO: int = 72
    __PONTA_EMPRESTIMO_DOADOR: int = 1

    def __get_codigo_agente_bradesco(self) -> int:
        return self.__CODIGO_AGENTE_BRADESCO

    def __get_ponta_emprestimo_doador(self) -> int:
        return self.__PONTA_EMPRESTIMO_DOADOR

    def __get_codigo_contrato_tratado(self, numero_contrato: str) -> str:
        return numero_contrato[8:-2]

    def get_zip_buffer_renovacoes(
        self,
        data_referente: date,
        nome_arq_xls_caracteristicas_fundos: str,
        nome_arq_csv_relatorio_bip: str,
    ) -> tuple[BytesIO, str]:
        dataframe_liquidacao, avisos = self.__get_liquidacoes_e_avisos(
            data_referente=data_referente,
            nome_arq_xls_caracteristicas_fundos=nome_arq_xls_caracteristicas_fundos,
            nome_arq_csv_relatorio_bip=nome_arq_csv_relatorio_bip,
        )

        SHEET_NAME: str = "Aluguel_Liquidação"
        buffer_excel_liquidacao_buffer: BytesIO = self._get_excel_buffer(
            dataframe=dataframe_liquidacao, sheet_name=SHEET_NAME
        )

        zip_buffer: BytesIO = BytesIO()
        nome_arquivo: str = (
            f"Liquida_Emprest.bolsa(Renovação)_{data_referente.strftime('%Y%m%d')} - Gerar Liquidação.xlsx"
        )
        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr(
                nome_arquivo,
                buffer_excel_liquidacao_buffer.read(),
            )

        avisos_dicts = [aviso.__dict__ for aviso in avisos]

        return (zip_buffer, dumps(avisos_dicts))

    def get_zip_buffer_novos_contratos(
        self,
        data_referente: date,
        nome_arq_xls_caracteristicas_fundos: str,
        nome_arq_csv_relatorio_bip: str,
    ) -> tuple[BytesIO, str]:
        dataframe_novos_contratos, avisos = self.__get_novos_contratos_e_avisos(
            data_referente=data_referente,
            nome_arq_xls_caracteristicas_fundos=nome_arq_xls_caracteristicas_fundos,
            nome_arq_csv_relatorio_bip=nome_arq_csv_relatorio_bip,
        )

        SHEET_NAME: str = "Aluguel_Novo"
        buffer_excel_novos_contratos: BytesIO = self._get_excel_buffer(
            dataframe=dataframe_novos_contratos, sheet_name=SHEET_NAME
        )

        zip_buffer: BytesIO = BytesIO()
        nome_arquivo: str = (
            f"Oper.Emprest.bolsa.BRIT_{data_referente.strftime('%Y%m%d')} - Gerar Novo Contrato.xlsx"
        )
        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr(
                nome_arquivo,
                buffer_excel_novos_contratos.read(),
            )

        avisos_dicts = [aviso.__dict__ for aviso in avisos]

        return (zip_buffer, dumps(avisos_dicts))

    def get_zip_buffer_antecipacoes(
        self,
        data_referente: date,
        nome_arq_xls_caracteristicas_fundos: str,
        nome_arq_xlsx_relatorio_antecipacoes: str,
    ) -> tuple[BytesIO, str]:
        dataframe_antecipacoes, avisos = self.__get_antecipacoes_e_avisos(
            data_referente=data_referente,
            nome_arq_xls_caracteristicas_fundos=nome_arq_xls_caracteristicas_fundos,
            nome_arq_xlsx_relatorio_antecipacoes=nome_arq_xlsx_relatorio_antecipacoes,
        )

        SHEET_NAME: str = "Aluguel_Liquidação"
        buffer_excel_antecipacoes: BytesIO = self._get_excel_buffer(
            dataframe=dataframe_antecipacoes, sheet_name=SHEET_NAME
        )

        zip_buffer: BytesIO = BytesIO()
        nome_arquivo: str = (
            f"Liquida_Emprest.bolsa(Antecipação)_{data_referente.strftime('%Y%m%d')} - Gerar Antecipação.xlsx"
        )

        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr(nome_arquivo, buffer_excel_antecipacoes.read())

        avisos_dicts = [aviso.__dict__ for aviso in avisos]

        return (zip_buffer, dumps(avisos_dicts))

    def __get_liquidacoes_e_avisos(
        self,
        data_referente: date,
        nome_arq_xls_caracteristicas_fundos: str,
        nome_arq_csv_relatorio_bip: str,
    ) -> tuple[DataFrame, list[Log]]:
        dataframe_caracteristicas_fundos: DataFrame = (
            self._get_dataframe_caracteristicas_fundos(
                nome_arq_xls_caracteristicas_fundos=nome_arq_xls_caracteristicas_fundos
            )
        )
        linhas_relatorio_bip: list[AluguelLinhaRelatorioBIP] = (
            AluguelAcoesHelper.get_linhas_relatorio_bip(
                nome_arq_csv_relatorio_bip=nome_arq_csv_relatorio_bip
            )
        )

        dmenos1: date = self._get_d_util_menos_1(data_referente)

        avisos: list[Log] = []
        linhas_dataframe_liquidacao: list[dict] = []
        for linha in linhas_relatorio_bip:
            aviso: Log = Log(
                tipo_id="fundo_codigo_administrador",
                id=linha.codigo_administrador,
                mensagens=[],
            )
            if (
                linha.tipo_contrato != AluguelTipoContrato.RENOVACAO.value
                or linha.quantidade == 0
            ):
                continue

            codigo_britech: int | None = (
                self._get_fundo_codigo_britech_by_fundo_codigo_administrador(
                    fundo_codigo_administrador=linha.codigo_administrador,
                    dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
                )
            )
            if codigo_britech is None:
                aviso.mensagens.append(
                    LogMensagem.get_fundo_codigo_britech_nao_encontrado_caracteristicas(
                        id_label="código administrador",
                        id_value=str(linha.codigo_administrador),
                    )
                )
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            codigo_contrato: str = self.__get_codigo_contrato_tratado(
                linha.numero_contrato
            )

            linha_dataframe_liquidacao: dict = {
                "IdCliente": codigo_britech,
                "CdAtivoBolsa": linha.papel,
                "CdAgente": self.__get_codigo_agente_bradesco(),
                "PontaEmprestimo": self.__get_ponta_emprestimo_doador(),
                "DataRegistro": dmenos1.strftime("%d/%m/%Y"),
                "DataVencimento": data_referente.strftime("%d/%m/%Y"),
                "NumeroContrato": codigo_contrato,
                "DataLiquidacaoAntecipada": dmenos1.strftime("%d/%m/%Y"),
                "QuantidadeLiquidar": linha.quantidade,
                "DataLiquidacao": "",
            }
            linhas_dataframe_liquidacao.append(linha_dataframe_liquidacao)

        dataframe_liquidacoes: DataFrame = DataFrame(linhas_dataframe_liquidacao)

        return (dataframe_liquidacoes, avisos)

    def __get_novos_contratos_e_avisos(
        self,
        data_referente: date,
        nome_arq_xls_caracteristicas_fundos: str,
        nome_arq_csv_relatorio_bip: str,
    ) -> tuple[DataFrame, list[Log]]:
        dataframe_caracteristicas_fundos: DataFrame = (
            self._get_dataframe_caracteristicas_fundos(
                nome_arq_xls_caracteristicas_fundos=nome_arq_xls_caracteristicas_fundos
            )
        )
        linhas_relatorio_bip: list[AluguelLinhaRelatorioBIP] = (
            AluguelAcoesHelper.get_linhas_relatorio_bip(
                nome_arq_csv_relatorio_bip=nome_arq_csv_relatorio_bip
            )
        )

        dmenos1: date = self._get_d_util_menos_1(data_referente)

        avisos: list[Log] = []
        linhas_dataframe_novos_contratos: list[dict] = []
        for linha in linhas_relatorio_bip:
            aviso: Log = Log(
                tipo_id="fundo_xml_nome",
                id=linha.codigo_administrador,
                mensagens=[],
            )

            if linha.quantidade == 0:
                continue

            codigo_britech: int | None = (
                self._get_fundo_codigo_britech_by_fundo_codigo_administrador(
                    fundo_codigo_administrador=linha.codigo_administrador,
                    dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
                )
            )
            if codigo_britech is None:
                aviso.mensagens.append(
                    LogMensagem.get_fundo_codigo_britech_nao_encontrado_caracteristicas(
                        id_label="código administrador",
                        id_value=linha.codigo_administrador,
                    )
                )
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            codigo_contrato: str = self.__get_codigo_contrato_tratado(
                linha.numero_contrato
            )

            linha_dataframe_novo_contrato: dict = {
                "IdCliente": codigo_britech,
                "CdAtivoBolsa": linha.papel,
                "CodigoBovespa": self.__get_codigo_agente_bradesco(),
                "PontaEmprestimo": self.__get_ponta_emprestimo_doador(),
                "DataRegistro": dmenos1.strftime("%d/%m/%Y"),
                "DataVencimento": linha.data_vencimento.strftime("%d/%m/%Y"),
                "TaxaOperacao": linha.taxa_cliente,
                "Quantidade": linha.quantidade,
                "PU": 0,
                "NumeroContrato": codigo_contrato,
                "TipoEmprestimo": self.__get_ponta_emprestimo_doador(),
                "Trader": "",
                "TaxaComissao": round(linha.taxa_derivada, 2),
                "PermiteDevolucaoAntecipada": "S",
                "DataInicialDevolucaoAntecipada": data_referente.strftime("%d/%m/%Y"),
                "DataLiquidacao": dmenos1.strftime("%d/%m/%Y"),
                "UserTimeStamp": "",
            }

            linhas_dataframe_novos_contratos.append(linha_dataframe_novo_contrato)

        dataframe_novos_contratos: DataFrame = DataFrame(
            linhas_dataframe_novos_contratos
        )

        return (dataframe_novos_contratos, avisos)

    def __get_antecipacoes_e_avisos(
        self,
        data_referente: date,
        nome_arq_xls_caracteristicas_fundos: str,
        nome_arq_xlsx_relatorio_antecipacoes: str,
    ) -> tuple[DataFrame, list[Log]]:
        dataframe_caracteristicas_fundos: DataFrame = (
            self._get_dataframe_caracteristicas_fundos(
                nome_arq_xls_caracteristicas_fundos=nome_arq_xls_caracteristicas_fundos
            )
        )
        linhas_relatorio_antecipacoes: list[AluguelLinhaRelatorioAntecipacao] = (
            AluguelAcoesHelper.get_linhas_relatorio_antecipacoes(
                nome_arq_xlsx_relatorio_antecipacoes=nome_arq_xlsx_relatorio_antecipacoes
            )
        )

        avisos: list[Log] = []
        linhas_dataframe_antecipacoes: list[dict] = []
        for linha in linhas_relatorio_antecipacoes:
            aviso: Log = Log(
                tipo_id="fundo_codigo_corretora",
                id=linha.numero_conta,
                mensagens=[],
            )
            if linha.quantidade_liquidacao == 0:
                continue

            codigo_britech: str | None = (
                self._get_fundo_codigo_britech_by_fundo_codigo_corretora(
                    fundo_codigo_corretora=linha.numero_conta,
                    dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
                )
            )
            if codigo_britech is None:
                aviso_mensagem: str = (
                    LogMensagem.get_fundo_codigo_britech_nao_encontrado_caracteristicas(
                        id_label="código corretora",
                        id_value=linha.numero_conta,
                    )
                )
                aviso.mensagens.append(aviso_mensagem)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            codigo_contrato: str = self.__get_codigo_contrato_tratado(
                linha.numero_contrato
            )

            dmenos1: date = self._get_d_util_menos_1(data_referente)
            linha_dataframe_antecipacoes: dict = {
                "IdCliente": codigo_britech,
                "CdAtivoBolsa": linha.papel,
                "CdAgente": self.__get_codigo_agente_bradesco(),
                "PontaEmprestimo": self.__get_ponta_emprestimo_doador(),
                "DataRegistro": dmenos1.strftime("%d/%m/%Y"),
                "DataVencimento": linha.data_vencimento.strftime("%d/%m/%Y"),
                "NumeroContrato": codigo_contrato,
                "DataLiquidacaoAntecipada": dmenos1.strftime("%d/%m/%Y"),
                "QuantidadeLiquidar": linha.quantidade_liquidacao,
                "DataLiquidacao": "",
            }

            linhas_dataframe_antecipacoes.append(linha_dataframe_antecipacoes)

        dataframe_antecipacoes: DataFrame = DataFrame(linhas_dataframe_antecipacoes)

        return (dataframe_antecipacoes, avisos)
