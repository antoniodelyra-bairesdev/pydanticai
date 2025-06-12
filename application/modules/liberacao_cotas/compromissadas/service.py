from datetime import date, datetime
from io import BytesIO
from json import dumps
from pandas import DataFrame
from xml.etree.ElementTree import fromstring, Element, ParseError
from zipfile import ZipFile

from modules.posicao.xml_anbima_401.enums import Tags
from modules.util.string import get_cnpj_com_formatacao
from modules.util.temp_file import TempFileHelper
from .types import Compromissada
from ..service import LiberacaoCotasService
from ..types import Log, LogMensagem


class CompromissadasService(LiberacaoCotasService):
    def get_zip_buffer_compromissadas(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        nome_arq_xls_caracteristicas_fundos: str,
    ) -> tuple[BytesIO, str]:
        dataframe_caracteristicas_fundos: DataFrame = (
            self._get_dataframe_caracteristicas_fundos(
                nome_arq_xls_caracteristicas_fundos=nome_arq_xls_caracteristicas_fundos
            )
        )

        dataframe_compromissadas, avisos = self.__get_compromissadas_e_avisos(
            nomes_arqs_xmls_anbima_401=nomes_arqs_xmls_anbima_401,
            dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
        )

        SHEET_NAME: str = "Compromissada_Britech"
        buffer_excel_compromissadas: BytesIO = self._get_excel_buffer(
            dataframe=dataframe_compromissadas, sheet_name=SHEET_NAME
        )

        zip_buffer: BytesIO = BytesIO()
        nome_arq_xlsx_compromissadas: str = "Compromissada_Britech.xlsx"

        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr(
                nome_arq_xlsx_compromissadas, buffer_excel_compromissadas.read()
            )

        avisos_dict = [aviso.__dict__ for aviso in avisos]

        return (zip_buffer, dumps(avisos_dict))

    def __get_compromissadas_e_avisos(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        dataframe_caracteristicas_fundos: DataFrame,
    ) -> tuple[DataFrame, list[Log]]:
        compromissadas, avisos = self.__get_compromissadas_e_avisos_from_xmls(
            nomes_arqs_xmls_anbima_401=nomes_arqs_xmls_anbima_401,
            dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
        )

        linhas_compromissadas: list[dict] = []
        for compromissada in compromissadas:
            linha_compromissada: dict = {
                "IdCliente": int(compromissada.fundo_codigo_brit),
                "IdTitulo": int(compromissada.id_titulo),
                "DataOperacao": date.strftime(compromissada.data_operacao, "%d/%m/%Y"),
                "TipoOperacao": compromissada.tipo_operacao,
                "Quantidade": compromissada.quantidade,
                "PuOperacao": compromissada.pu_operacao,
                "Valor": compromissada.valor,
                "TaxaOperacao": compromissada.taxa_operacao,
                "Categoria": "",
                "DataVolta": date.strftime(compromissada.data_retorno, "%d/%m/%Y"),
                "TaxaVolta": compromissada.taxa_retorno,
                "PuVolta": compromissada.pu_retorno,
                "ValorVolta": compromissada.valor_retorno,
                "IdIndiceVolta": "",
                "Custodia": "",
                "CodigoBovespa": "",
                "DataOperacaoOriginal": "",
                "IPO": compromissada.ipo,
                "LocalNegociacao": compromissada.local_negociacao,
                "AgenteCustodia": "",
                "Clearing": "",
                "Trader": "",
                "IdAgenteContraparte": "",
                "IdClienteContraparte": "",
                "DataLiquidacao": date.strftime(
                    compromissada.data_liquidacao, "%d/%m/%Y"
                ),
                "ValorCorretagem": "",
                "IdOperacaoResgatada": "",
                "IdCategoriaMovimentacao": "",
                "OperacaoTermo": compromissada.operacao_termo,
                "CodigoInterface_Cliente": "",
                "PercentualPuFace": "",
                "IdConta": "",
                "IdConta": "",
                "IdPosicao": "",
                "Observacao": "",
            }
            linhas_compromissadas.append(linha_compromissada)

        dataframe_compromissadas: DataFrame = DataFrame(linhas_compromissadas)
        return (dataframe_compromissadas, avisos)

    def __get_compromissadas_e_avisos_from_xmls(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        dataframe_caracteristicas_fundos: DataFrame,
    ) -> tuple[list[Compromissada], list[Log]]:
        avisos: list[Log] = []
        compromissadas: list[Compromissada] = []

        for i in range(0, len(nomes_arqs_xmls_anbima_401)):
            nome_arq = nomes_arqs_xmls_anbima_401[i][0]
            nome_arq_original = nomes_arqs_xmls_anbima_401[i][1]
            aviso: Log = Log(
                tipo_id="fundo_xml_nome", id=nome_arq_original, mensagens=[]
            )

            buffer_xml: bytes = TempFileHelper.get_conteudo_e_deleta(nome_arq)
            try:
                root: Element | None = fromstring(buffer_xml).find(Tags.FUNDO.value)
            except ParseError:
                aviso.mensagens.append(LogMensagem.ESTRUTURA_XML_CORROMPIDA)

            if root is None:
                aviso.mensagens.append(LogMensagem.FUNDO_CORROMPIDO)
                avisos.append(aviso)
                continue

            node_header: Element | None = root.find(Tags.HEADER.value)
            if node_header is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_CORROMPIDO)
                avisos.append(aviso)
                continue

            node_cnpj: Element | None = node_header.find(Tags.CNPJ.value)
            if node_cnpj is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_CNPJ_CORROMPIDO)
                avisos.append(aviso)
                continue
            cnpj: str | None = node_cnpj.text
            if cnpj is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_CNPJ_CORROMPIDO)
                avisos.append(aviso)
                continue

            node_titulos_publicos: list[Element] | None = list(
                root.findall(Tags.TITPUBLICO.value)
            )
            if node_titulos_publicos is None:
                aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
                avisos.append(aviso)
                continue

            for node in node_titulos_publicos:
                compromissada: Compromissada | None = (
                    self.__get_compromissada_e_appenda_avisos(
                        cnpj=cnpj,
                        node_titulo_publico=node,
                        dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
                        aviso=aviso,
                        avisos=avisos,
                    )
                )

                if compromissada is None:
                    continue

                compromissadas.append(compromissada)

        return (compromissadas, avisos)

    def __get_compromissada_e_appenda_avisos(
        self,
        cnpj: str,
        node_titulo_publico: Element,
        dataframe_caracteristicas_fundos: DataFrame,
        aviso: Log,
        avisos: list[Log],
    ) -> Compromissada | None:
        node_compromisso: Element | None = node_titulo_publico.find(
            Tags.COMPROMISSO.value
        )
        if node_compromisso is None:
            return None

        node_codigo_selic: Element | None = node_titulo_publico.find(
            Tags.CODATIVO.value
        )
        if node_codigo_selic is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            avisos.append(aviso)
            return None

        node_isin: Element | None = node_titulo_publico.find(Tags.ISIN.value)
        if node_isin is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            avisos.append(aviso)
            return None

        node_data_operacao: Element | None = node_titulo_publico.find(
            Tags.DTOPERACAO.value
        )
        if node_data_operacao is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            avisos.append(aviso)
            return None
        data_operacao: date | None = (
            datetime.strptime(node_data_operacao.text, "%Y%m%d").date()
            if node_data_operacao.text is not None
            else None
        )
        if data_operacao is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            avisos.append(aviso)
            return None

        node_principal: Element | None = node_titulo_publico.find(Tags.PRINCIPAL.value)
        if node_principal is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            avisos.append(aviso)
            return None
        principal: float | None = (
            float(node_principal.text) if node_principal.text is not None else None
        )
        if principal is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            avisos.append(aviso)
            return None

        node_preco_unitario: Element | None = node_titulo_publico.find(
            Tags.PUPOSICAO.value
        )
        if node_preco_unitario is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            avisos.append(aviso)
            return None
        preco_unitario: float | None = (
            float(node_preco_unitario.text)
            if node_preco_unitario.text is not None
            else None
        )
        if preco_unitario is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            avisos.append(aviso)
            return None

        node_data_retorno: Element | None = node_compromisso.find(Tags.DTRETORNO.value)
        if node_data_retorno is None:
            aviso.mensagens.append(
                LogMensagem.FUNDO_TITULO_PUBLICO_COMPROMISSO_CORROMPIDO
            )
            avisos.append(aviso)
            return None
        data_retorno: date | None = (
            datetime.strptime(node_data_retorno.text, "%Y%m%d").date()
            if node_data_retorno.text is not None
            else None
        )
        if data_retorno is None:
            aviso.mensagens.append(
                LogMensagem.FUNDO_TITULO_PUBLICO_COMPROMISSO_CORROMPIDO
            )
            avisos.append(aviso)
            return None

        node_taxa_retorno: Element | None = node_compromisso.find(Tags.TXOPERACAO.value)
        if node_taxa_retorno is None:
            aviso.mensagens.append(
                LogMensagem.FUNDO_TITULO_PUBLICO_COMPROMISSO_CORROMPIDO
            )
            avisos.append(aviso)
            return None
        taxa_retorno: float | None = (
            float(node_taxa_retorno.text)
            if node_taxa_retorno.text is not None
            else None
        )
        if taxa_retorno is None:
            aviso.mensagens.append(
                LogMensagem.FUNDO_TITULO_PUBLICO_COMPROMISSO_CORROMPIDO
            )
            avisos.append(aviso)
            return None

        node_preco_unitario_retorno: Element | None = node_compromisso.find(
            Tags.PURETORNO.value
        )
        if node_preco_unitario_retorno is None:
            aviso.mensagens.append(
                LogMensagem.FUNDO_TITULO_PUBLICO_COMPROMISSO_CORROMPIDO
            )
            avisos.append(aviso)
            return None
        preco_unitario_retorno: float | None = (
            float(node_preco_unitario_retorno.text)
            if node_preco_unitario_retorno.text is not None
            else None
        )
        if preco_unitario_retorno is None:
            aviso.mensagens.append(
                LogMensagem.FUNDO_TITULO_PUBLICO_COMPROMISSO_CORROMPIDO
            )
            avisos.append(aviso)
            return None

        fundo_codigo_britech: str | None = self._get_fundo_codigo_britech_by_cnpj(
            cnpj=cnpj, dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos
        )
        if fundo_codigo_britech is None:
            aviso.mensagens.append(
                LogMensagem.get_fundo_codigo_britech_nao_encontrado_caracteristicas(
                    id_label="cnpj", id_value=get_cnpj_com_formatacao(cnpj)
                )
            )
            avisos.append(aviso)
            return None

        quantidade: int = round(principal / preco_unitario)
        valor_retorno: float = preco_unitario_retorno * quantidade
        linha_compromissada: Compromissada = Compromissada(
            fundo_codigo_brit=fundo_codigo_britech,
            id_titulo=40,
            data_operacao=data_operacao,
            tipo_operacao="CompraRevenda",
            quantidade=quantidade,
            pu_operacao=preco_unitario,
            valor=principal,
            taxa_operacao=taxa_retorno,
            data_retorno=data_retorno,
            taxa_retorno=taxa_retorno,
            pu_retorno=preco_unitario_retorno,
            valor_retorno=valor_retorno,
            ipo="N",
            local_negociacao="SELIC",
            data_liquidacao=data_operacao,
            operacao_termo="N",
        )

        return linha_compromissada
