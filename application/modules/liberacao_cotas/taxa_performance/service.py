from io import BytesIO
from json import dumps
from pandas import DataFrame, read_excel
from xml.etree.ElementTree import fromstring, Element, ParseError
from zipfile import ZipFile

from modules.posicao.xml_anbima_401.enums import Tags
from modules.util.string import get_cnpj_com_formatacao, get_cnpj_sem_formatacao
from modules.util.temp_file import TempFileHelper
from .types import PefeeDespesaBritech, PefeeTaxaPerformance
from ..service import LiberacaoCotasService
from ..types import Log, LogMensagem


class TaxaPerformanceService(LiberacaoCotasService):
    def get_zip_buffer_taxas_performance(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        nome_arq_xlsx_relatorio_despesas_britech: str,
        nome_arq_xls_caracteristicas_fundos: str,
    ) -> tuple[BytesIO, str]:
        (dataframe_taxas_performance, avisos) = self.__get_taxas_performance_e_avisos(
            nomes_arqs_xmls_anbima_401=nomes_arqs_xmls_anbima_401,
            nome_arq_xlsx_relatorio_despesas_britech=nome_arq_xlsx_relatorio_despesas_britech,
            nome_arq_xls_caracteristicas_fundos=nome_arq_xls_caracteristicas_fundos,
        )

        SHEET_NAME: str = "PFEE_BRIT"
        buffer_excel_taxas_performance: BytesIO = self._get_excel_buffer(
            dataframe=dataframe_taxas_performance, sheet_name=SHEET_NAME
        )

        zip_buffer: BytesIO = BytesIO()
        nome_arquivo_xlsx: str = "Cal.Prov.Brit2.xlsx"

        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr(nome_arquivo_xlsx, buffer_excel_taxas_performance.read())

        avisos_dicts = [aviso.__dict__ for aviso in avisos]

        return (zip_buffer, dumps(avisos_dicts))

    def __get_taxas_performance_e_avisos(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        nome_arq_xlsx_relatorio_despesas_britech: str,
        nome_arq_xls_caracteristicas_fundos: str,
    ) -> tuple[DataFrame, list[Log]]:
        linhas_despesas_britech: list[PefeeDespesaBritech] = (
            self.__get_linhas_despesas_britech(nome_arq_xlsx_relatorio_despesas_britech)
        )
        dataframe_caracteristicas_fundos: DataFrame = (
            self._get_dataframe_caracteristicas_fundos(
                nome_arq_xls_caracteristicas_fundos=nome_arq_xls_caracteristicas_fundos
            )
        )

        taxas_performance, avisos = self.__get_taxas_performance_e_avisos_from_xmls(
            nomes_arqs_xmls_anbima_401=nomes_arqs_xmls_anbima_401,
            despesas_britech=linhas_despesas_britech,
            dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
        )

        linhas_taxas_performance: list[dict] = []
        for taxa_perfomance in taxas_performance:
            assert taxa_perfomance.id_tabela

            linha: dict = {
                "IdTabela": taxa_perfomance.id_tabela,
                "IdCarteira": taxa_perfomance.id_carteira,
                "ValorDia": taxa_perfomance.valor_dia,
                "ValorAcumulado": taxa_perfomance.valor_acumulado,
                "DataFimApropriacao": taxa_perfomance.data_fim_apropriacao,
                "DataPagamento": taxa_perfomance.data_pagamento,
            }
            linhas_taxas_performance.append(linha)

        dataframe_taxas_performance: DataFrame = DataFrame(linhas_taxas_performance)

        return (dataframe_taxas_performance, avisos)

    def __get_taxas_performance_e_avisos_from_xmls(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        despesas_britech: list[PefeeDespesaBritech],
        dataframe_caracteristicas_fundos: DataFrame,
    ) -> tuple[list[PefeeTaxaPerformance], list[Log]]:
        avisos: list[Log] = []
        taxas_performance: list[PefeeTaxaPerformance] = []

        for i in range(0, len(nomes_arqs_xmls_anbima_401)):
            nome_arq = nomes_arqs_xmls_anbima_401[i][0]
            nome_arq_original = nomes_arqs_xmls_anbima_401[i][1]
            cnpj_arq_original = nome_arq_original.split("_")[0][2:]

            if (
                self.__has_taxa_administracao_fundo(
                    cnpj_arq_original, dataframe_caracteristicas_fundos
                )
                is False
            ):
                TempFileHelper.deleta_arquivo(nome_arq)
                continue

            aviso: Log = Log(
                tipo_id="fundo_xml_nome", id=nome_arq_original, mensagens=[]
            )

            buffer_xml: bytes = TempFileHelper.get_conteudo_e_deleta(nome_arq)
            try:
                root: Element | None = fromstring(buffer_xml).find(Tags.FUNDO.value)
            except ParseError:
                aviso.mensagens.append(LogMensagem.ESTRUTURA_XML_CORROMPIDA)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            if root is None:
                aviso.mensagens.append(LogMensagem.FUNDO_CORROMPIDO)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            node_cnpj: Element | None = root.find("header/cnpj")
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

            fundo_codigo_britech: str | None = self._get_fundo_codigo_britech_by_cnpj(
                cnpj=cnpj,
                dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
            )
            if fundo_codigo_britech is None:
                aviso.mensagens.append(
                    LogMensagem.get_fundo_codigo_britech_nao_encontrado_caracteristicas(
                        id_label="cnpj",
                        id_value=get_cnpj_com_formatacao(cnpj),
                    )
                )
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            taxa_performance_codigo_britech: str | None = (
                self.__get_pefee_codigo_britech_from_fundo_codigo_britech(
                    fundo_codigo_britech=fundo_codigo_britech,
                    despesas_britech=despesas_britech,
                )
            )
            if taxa_performance_codigo_britech is None:
                aviso.mensagens.append(
                    LogMensagem.get_fundo_nao_encontrado_planilha_despesas_britech(
                        fundo_codigo_britech
                    )
                )
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            node_provisoes: list[Element] | None = list(root.findall("provisao"))
            valor_acumulado: float = 0
            if node_provisoes is None:
                aviso.mensagens.append(LogMensagem.FUNDO_PROVISAO_CORROMPIDA)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            for node in node_provisoes:
                if self.__is_pefee(node) == False:
                    continue

                node_valor: Element | None = node.find("valor")
                if node_valor is None:
                    aviso.mensagens.append(LogMensagem.FUNDO_PROVISAO_VALOR_CORROMPIDO)
                    if aviso not in avisos:
                        avisos.append(aviso)
                    continue
                valor: float | None = (
                    float(node_valor.text) if node_valor.text is not None else None
                )
                if valor is None:
                    aviso.mensagens.append(LogMensagem.FUNDO_PROVISAO_VALOR_CORROMPIDO)
                    if aviso not in avisos:
                        avisos.append(aviso)
                    continue

                valor_acumulado = valor_acumulado + valor

            taxa_performance: PefeeTaxaPerformance = PefeeTaxaPerformance(
                id_tabela=int(taxa_performance_codigo_britech),
                id_carteira=int(fundo_codigo_britech),
                valor_dia=0,  # ignorado
                valor_acumulado=valor_acumulado,
                data_fim_apropriacao="02/01/2027",  # ignorado
                data_pagamento="02/01/2023",  # ignorado
            )

            taxas_performance.append(taxa_performance)

        return (taxas_performance, avisos)

    def __get_linhas_despesas_britech(
        self,
        nome_arq_xlsx_relatorio_despesas_britech,
    ) -> list[PefeeDespesaBritech]:
        buffer_arq_xlsx_relatorio_despesas_britech: bytes = (
            TempFileHelper.get_conteudo_e_deleta(
                nome_arq_xlsx_relatorio_despesas_britech
            )
        )
        dataframe_despesas_britech: DataFrame = self.__get_dataframe_despesas_britech(
            buffer_arq_xlsx_relatorio_despesas_britech
        )
        despesas_britech: list[PefeeDespesaBritech] = self.__get_despesas_britech(
            dataframe_despesas_britech
        )

        return despesas_britech

    def __get_dataframe_despesas_britech(
        self,
        buffer_arq_xlsx_relatorio_despesas_britech: bytes,
    ) -> DataFrame:
        dataframe: DataFrame = read_excel(buffer_arq_xlsx_relatorio_despesas_britech)

        return dataframe

    @staticmethod
    def __get_despesas_britech(
        dataframe_despesas_britech: DataFrame,
    ) -> list[PefeeDespesaBritech]:
        records: list[dict] = dataframe_despesas_britech.to_dict("records")

        despesas_britech: list[PefeeDespesaBritech] = []
        for record in records:
            codigo: str = str(record["Id"]).strip()
            fundo_codigo_britech: str = str(record["Id Carteira"]).strip()
            descricao: str = str(record["Descrição"]).strip()

            despesa_britech: PefeeDespesaBritech = PefeeDespesaBritech(
                codigo=codigo, fundo_codigo=fundo_codigo_britech, descricao=descricao
            )

            despesas_britech.append(despesa_britech)

        return despesas_britech

    def __has_taxa_administracao_fundo(
        self,
        cnpj: str,
        dataframe_caracteristicas_fundos: DataFrame,
    ) -> bool:

        for _, row in dataframe_caracteristicas_fundos.iterrows():
            row_cnpj: str = get_cnpj_sem_formatacao(row["CNPJ"])

            if cnpj == row_cnpj:
                row_taxa_administracao: str = row["Taxa de Performance"]

                if (
                    row_taxa_administracao != None
                    and row_taxa_administracao != ""
                    and row_taxa_administracao != "-"
                ):
                    return True

        return False

    def __get_pefee_codigo_britech_from_fundo_codigo_britech(
        self,
        fundo_codigo_britech: str,
        despesas_britech: list[PefeeDespesaBritech],
    ) -> str | None:
        for despesa in despesas_britech:
            descricao_tratada: str = despesa.descricao.strip().lower()
            if not descricao_tratada.startswith("performance"):
                continue

            if fundo_codigo_britech == despesa.fundo_codigo:
                return despesa.codigo

        return None

    def __is_pefee(self, node_provisao: Element) -> bool:
        node_codigo: Element | None = node_provisao.find("codprov")
        if node_codigo is None:
            return False
        codigo: str | None = node_codigo.text

        return codigo == "35"
