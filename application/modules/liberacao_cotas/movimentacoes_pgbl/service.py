from io import BytesIO
from datetime import date, datetime
from zipfile import ZipFile
from pandas import DataFrame, read_excel, concat
from json import dumps
from xml.etree.ElementTree import fromstring, Element, ParseError

from modules.posicao.xml_anbima_401.enums import Tags
from modules.util.temp_file import TempFileHelper
from modules.util.string import get_cnpj_com_formatacao, get_cnpj_sem_formatacao
from .types import MovimentacaoPGBLFundoCota, MovimentacaoPGBLLinhaRelatorio
from ..types import Log, LogMensagem
from ..service import LiberacaoCotasService


class MovimentacoesPGBLService(LiberacaoCotasService):
    def get_zip_buffer_movimentacoes_pgbl(
        self,
        data_referente: date,
        nomes_arqs_xml_anbima_401: list[tuple[str, str]],
        nome_arq_xls_caracteristicas_fundos: str,
        nomes_arqs_xlsxs_relatorios_movimentacoes_pgbl: list[str],
    ) -> tuple[BytesIO, str]:
        (
            dataframe_movimentacoes_pgbl,
            avisos,
        ) = self.__get_movimentacoes_pgbl_e_avisos(
            nomes_arqs_xml_anbima_401=nomes_arqs_xml_anbima_401,
            nome_arq_xls_caracteristicas_fundos=nome_arq_xls_caracteristicas_fundos,
            nomes_arqs_xlsxs_relatorios_movimentacoes_pgbl=nomes_arqs_xlsxs_relatorios_movimentacoes_pgbl,
        )

        SHEET_NAME: str = "Oper.Cotista.BRIT"
        buffer_excel_movimentacoes_pgbl: BytesIO = self._get_excel_buffer(
            dataframe=dataframe_movimentacoes_pgbl, sheet_name=SHEET_NAME
        )

        zip_buffer: BytesIO = BytesIO()
        nome_arquivo: str = (
            f"Arquivo_Importação_Oper.Cot_BRIT_{data_referente.strftime('%Y%m%d')}.xlsx"
        )

        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr(nome_arquivo, buffer_excel_movimentacoes_pgbl.read())

        avisos_dicts = [aviso.__dict__ for aviso in avisos]

        return (zip_buffer, dumps(avisos_dicts))

    def __get_movimentacoes_pgbl_e_avisos(
        self,
        nomes_arqs_xml_anbima_401: list[tuple[str, str]],
        nome_arq_xls_caracteristicas_fundos: str,
        nomes_arqs_xlsxs_relatorios_movimentacoes_pgbl: list[str],
    ) -> tuple[DataFrame, list[Log]]:
        linhas_relatorio_movimentacoes_pgbl: list[MovimentacaoPGBLLinhaRelatorio] = (
            self.__get_linhas_relatorio_movimentacoes_pgbl(
                nomes_arqs_xlsxs_relatorios_movimentacoes_pgbl=nomes_arqs_xlsxs_relatorios_movimentacoes_pgbl
            )
        )
        dataframe_caracteristias_fundos: DataFrame = (
            self._get_dataframe_caracteristicas_fundos(
                nome_arq_xls_caracteristicas_fundos=nome_arq_xls_caracteristicas_fundos
            )
        )
        fundos_cotas, avisos = self.__get_fundos_cotas_e_avisos(
            nomes_arqs_xml_anbima_401=nomes_arqs_xml_anbima_401,
            dataframe_caracteristicas_fundos=dataframe_caracteristias_fundos,
        )

        linhas_dataframe_movimentacoes_pgbl: list[dict] = []
        for linha in linhas_relatorio_movimentacoes_pgbl:
            fundo_cota: MovimentacaoPGBLFundoCota | None = (
                (
                    self.__get_fundo_cota_by_codigo_brit(
                        codigo_brit=linha.codigo_brit, fundos_cotas=fundos_cotas
                    )
                )
                if linha.codigo_brit is not None
                else None
            )

            id_cotista: int = int(linha.id_cotista)
            id_carteira: int = int(linha.codigo_brit)
            data_operacao: date = linha.data_operacao
            data_conversao: date = linha.data_conversao
            data_liquidacao: date = linha.data_liquidacao
            tipo_operacao: int = linha.tipo_operacao
            tipo_resgate: str = ""
            quantidade: int = 0
            cota_operacao: int = 0
            valor_bruto: float | None = (
                fundo_cota.valor_cota * linha.quantidade_cotas
                if fundo_cota is not None
                else None
            )
            valor_liquido: float | None = (
                fundo_cota.valor_cota * linha.quantidade_cotas
                if fundo_cota is not None
                else None
            )
            valor_ir: float = 0
            valor_iof: float = 0
            valor_performance: float = 0
            rendimento_resgate: float = 0
            local_negociacao: str = "CETIP"
            fie_modalidade: str = ""
            fie_tabela_ir: str = ""
            data_aplic_cautela_resgatada: str = ""
            cota_informada: str = ""
            trader: str = ""
            tipo_cotista_movimentacao: str = ""
            codigo_interface_cliente: str = ""
            codigo_interface_cotista: str = ""
            data_registro: str = ""
            dados_bancarios: str = ""
            observacao: str = ""
            id_forma_liquidacao: str = ""

            linha_output: dict = {
                "IdCotista": id_cotista,
                "IdCarteira": id_carteira,
                "DataOperacao": data_operacao.strftime("%d/%m/%Y"),
                "DataConversao": data_conversao.strftime("%d/%m/%Y"),
                "DataLiquidacao": data_liquidacao.strftime("%d/%m/%Y"),
                "TipoOperacao": tipo_operacao,
                "TipoResgate": tipo_resgate,
                "Quantidade": quantidade,
                "CotaOperacao": cota_operacao,
                "ValorBruto": valor_bruto,
                "ValorLiquido": valor_liquido,
                "ValorIR": valor_ir,
                "ValorIOF": valor_iof,
                "ValorPerformance": valor_performance,
                "RendimentoResgate": rendimento_resgate,
                "LocalNegociacao": local_negociacao,
                "FieModalidade": fie_modalidade,
                "FieTabelaIr": fie_tabela_ir,
                "DataAplicCautelaResgatada": data_aplic_cautela_resgatada,
                "CotaInformada": cota_informada,
                "Trader": trader,
                "Tipo_CotistaMovimentacao": tipo_cotista_movimentacao,
                "CodigoInterface_Cliente": codigo_interface_cliente,
                "CodigoInterface_Cotista": codigo_interface_cotista,
                "DataRegistro": data_registro,
                "DadosBancarios": dados_bancarios,
                "Observacao": observacao,
                "IdFormaLiquidacao": id_forma_liquidacao,
            }
            linhas_dataframe_movimentacoes_pgbl.append(linha_output)

        dataframe_movimentacoes_pgbl: DataFrame = DataFrame(
            linhas_dataframe_movimentacoes_pgbl
        )

        return (
            dataframe_movimentacoes_pgbl,
            avisos,
        )

    def __get_linhas_relatorio_movimentacoes_pgbl(
        self,
        nomes_arqs_xlsxs_relatorios_movimentacoes_pgbl: list[str],
    ) -> list[MovimentacaoPGBLLinhaRelatorio]:
        buffers_arqs_xlsxs_relatorios_movimentacoes_pgbl: list[bytes] = []
        for nome_arq in nomes_arqs_xlsxs_relatorios_movimentacoes_pgbl:
            buffer_arq: bytes = TempFileHelper.get_conteudo_e_deleta(nome_arq)
            buffers_arqs_xlsxs_relatorios_movimentacoes_pgbl.append(buffer_arq)

        dataframe_relatorios_movimentacoes_pgbl: DataFrame = (
            self.__get_dataframe_movimentacoes_pgbl(
                buffers_arqs_xlsxs_relatorios_movimentacoes_pgbl=buffers_arqs_xlsxs_relatorios_movimentacoes_pgbl
            )
        )

        linhas_relatorio_movimentacoes_pbgl: list[MovimentacaoPGBLLinhaRelatorio] = []

        for _, row in dataframe_relatorios_movimentacoes_pgbl.iterrows():
            id_cotista: str = str(row.IdCotista)
            codigo_brit: str = str(row.IdCarteira)
            data_operacao: date = datetime.strptime(
                str(row.DataOperacao), "%Y-%m-%d %H:%M:%S"
            )
            data_conversao: date = datetime.strptime(
                str(row.DataConversao), "%Y-%m-%d %H:%M:%S"
            )
            data_liquidacao: date = datetime.strptime(
                str(row.DataLiquidacao), "%Y-%m-%d %H:%M:%S"
            )
            tipo_operacao: int = int(row.TipoOperacao)
            quantidade_cotas: float = float(row.qtd_cotas)

            linha: MovimentacaoPGBLLinhaRelatorio = MovimentacaoPGBLLinhaRelatorio(
                id_cotista=id_cotista,
                codigo_brit=codigo_brit,
                data_operacao=data_operacao,
                data_conversao=data_conversao,
                data_liquidacao=data_liquidacao,
                tipo_operacao=tipo_operacao,
                quantidade_cotas=quantidade_cotas,
            )

            linhas_relatorio_movimentacoes_pbgl.append(linha)

        return linhas_relatorio_movimentacoes_pbgl

    def __get_dataframe_movimentacoes_pgbl(
        self,
        buffers_arqs_xlsxs_relatorios_movimentacoes_pgbl: list[bytes],
    ) -> DataFrame:
        dataframe_relatorios: DataFrame = DataFrame()

        for buffer in buffers_arqs_xlsxs_relatorios_movimentacoes_pgbl:
            dataframe_relatorio: DataFrame = read_excel(buffer)
            dataframe_relatorios = concat([dataframe_relatorio, dataframe_relatorios])

        return dataframe_relatorios

    def __get_fundos_cotas_e_avisos(
        self,
        nomes_arqs_xml_anbima_401: list[tuple[str, str]],
        dataframe_caracteristicas_fundos: DataFrame,
    ) -> tuple[list[MovimentacaoPGBLFundoCota], list[Log]]:
        avisos: list[Log] = []
        fundos_cotas: list[MovimentacaoPGBLFundoCota] = []

        for i in range(0, len(nomes_arqs_xml_anbima_401)):
            nome_arq = nomes_arqs_xml_anbima_401[i][0]
            nome_arq_original = nomes_arqs_xml_anbima_401[i][1]
            aviso: Log = Log(
                tipo_id="fundo_xml_nome", id=nome_arq_original, mensagens=[]
            )

            buffer_xml: bytes = TempFileHelper.get_conteudo_e_deleta(nome_arq)
            try:
                root: Element | None = fromstring(buffer_xml).find(Tags.FUNDO.value)
            except ParseError:
                aviso.mensagens.append(LogMensagem.ESTRUTURA_XML_CORROMPIDA)
                continue
            if root is None:
                aviso.mensagens.append(LogMensagem.FUNDO_CORROMPIDO)
                continue

            node_header = root.find("header")
            if node_header is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_CORROMPIDO)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            node_cnpj: Element | None = node_header.find("cnpj")
            if node_cnpj is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_CNPJ_CORROMPIDO)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue
            cnpj: str | None = node_cnpj.text
            if cnpj is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_CNPJ_CORROMPIDO)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue
            if (
                self.__is_fundo_pgbl(
                    cnpj=cnpj,
                    dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
                )
                != True
            ):
                continue

            node_valor_cota: Element | None = node_header.find("valorcota")
            if node_valor_cota is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_VALOR_COTA_CORROMPIDA)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue
            valor_cota_text: str | None = node_valor_cota.text
            if valor_cota_text is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_VALOR_COTA_CORROMPIDA)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue
            valor_cota: float = float(valor_cota_text)

            codigo_brit: str | None = self._get_fundo_codigo_britech_by_cnpj(
                cnpj=cnpj,
                dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
            )
            if codigo_brit is None:
                aviso.mensagens.append(
                    LogMensagem.get_fundo_codigo_britech_nao_encontrado_caracteristicas(
                        id_label="cnpj",
                        id_value=get_cnpj_com_formatacao(cnpj),
                    )
                )
                continue
            fundo_cota: MovimentacaoPGBLFundoCota = MovimentacaoPGBLFundoCota(
                cnpj=cnpj, codigo_brit=codigo_brit, valor_cota=valor_cota
            )

            fundos_cotas.append(fundo_cota)

        return (fundos_cotas, avisos)

    def __get_fundo_cota_by_codigo_brit(
        self, codigo_brit: str, fundos_cotas: list[MovimentacaoPGBLFundoCota]
    ) -> MovimentacaoPGBLFundoCota | None:
        for fundo_cota in fundos_cotas:
            if codigo_brit == fundo_cota.codigo_brit:
                return fundo_cota

        return None

    def __is_fundo_pgbl(
        self, cnpj: str, dataframe_caracteristicas_fundos: DataFrame
    ) -> bool | None:
        for _, row in dataframe_caracteristicas_fundos.iterrows():
            cnpj_procurado: str = get_cnpj_sem_formatacao(str(row["CNPJ"]))

            if cnpj == cnpj_procurado:
                tipo_fundo: str = str(row["Tipo Fundo"])
                return (
                    tipo_fundo == "FIE I"
                    or tipo_fundo == "FIE II"
                    or tipo_fundo == "FIFE"
                )

        return None
