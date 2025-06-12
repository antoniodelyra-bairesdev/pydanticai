from datetime import date, datetime
from io import BytesIO
from json import dumps
from pandas import DataFrame
from typing import Literal
from xml.etree.ElementTree import fromstring, Element, ParseError
from zipfile import ZipFile

from modules.posicao.xml_anbima_401.enums import Tags
from modules.util.string import get_cnpj_com_formatacao
from modules.util.temp_file import TempFileHelper
from .types import (
    LinhaDEPARACreditoPrivado,
    LinhaDEPARARendaFixaMarcadaNaCurva,
    FundoPrecoTituloPrivado,
)
from .helper import RendaFixaHelper
from ..service import LiberacaoCotasService
from ..types import Log, LogMensagem, AtivoRendaFixa


class RendaFixaService(LiberacaoCotasService):
    def get_zip_buffer_ativos_renda_fixa_nao_precificados_anbima_fundos_bradesco(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        nome_arq_xls_caracteristicas_fundos: str,
        nome_arq_xlsx_depara_ativos_credito_privado: str,
        nome_arq_xlsx_depara_ativos_marcados_na_curva: str,
    ) -> tuple[BytesIO, str]:
        dataframe_ativos_renda_fixa_nao_precificados_anbima, avisos = (
            self.__get_ativos_renda_fixa_nao_precificados_anbima_fundos_bradesco_e_avisos(
                nomes_arqs_xmls_anbima_401=nomes_arqs_xmls_anbima_401,
                nome_arq_xls_caracteristicas_fundos=nome_arq_xls_caracteristicas_fundos,
                nome_arq_xlsx_depara_ativos_credito_privado=nome_arq_xlsx_depara_ativos_credito_privado,
                nome_arq_xlsx_depara_ativos_marcados_na_curva=nome_arq_xlsx_depara_ativos_marcados_na_curva,
            )
        )

        SHEET_NAME: str = "IMPORTACAO_COTACAO_SERIE_BRIT"
        buffer_excel_ativos_credito_privado_nao_precificados_anbima: BytesIO = (
            self._get_excel_buffer(
                dataframe=dataframe_ativos_renda_fixa_nao_precificados_anbima,
                sheet_name=SHEET_NAME,
            )
        )

        zip_buffer: BytesIO = BytesIO()
        nome_arq_xlsx_ativos_credito_privado_nao_precificados_anbima: str = (
            "ImportacaoCotacaoSerie.xlsx"
        )

        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr(
                nome_arq_xlsx_ativos_credito_privado_nao_precificados_anbima,
                buffer_excel_ativos_credito_privado_nao_precificados_anbima.read(),
            )

        avisos_dicts = [aviso.__dict__ for aviso in avisos]

        return (zip_buffer, dumps(avisos_dicts))

    def get_zip_buffer_marcacao_mercado_ativos_em_fundos_nao_bradesco(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        nome_arq_xls_caracteristicas_fundos: str,
        nome_arq_xlsx_depara_ativos_credito_privado: str,
    ) -> tuple[BytesIO, str]:
        (dataframe_precos_ativos, avisos) = (
            self.__get_precos_ativos_credito_privado_em_fundos_nao_bradesco_e_avisos(
                nomes_arqs_xmls_anbima_401=nomes_arqs_xmls_anbima_401,
                nome_arq_xls_caracteristicas_fundos=nome_arq_xls_caracteristicas_fundos,
                nome_arq_xlsx_depara_ativos_credito_privado=nome_arq_xlsx_depara_ativos_credito_privado,
            )
        )

        SHEET_NAME: str = "ImportacaoMTMManual"
        buffer_excel_precos_ativos_credito_privado_em_fundos_nao_bradesco: BytesIO = (
            self._get_excel_buffer(
                dataframe=dataframe_precos_ativos, sheet_name=SHEET_NAME
            )
        )

        zip_buffer: BytesIO = BytesIO()
        nome_arquivo: str = f"ImportacaoMTMManual.xlsx"

        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr(
                nome_arquivo,
                buffer_excel_precos_ativos_credito_privado_em_fundos_nao_bradesco.read(),
            )

        avisos_dicts = [aviso.__dict__ for aviso in avisos]

        return (zip_buffer, dumps(avisos_dicts))

    def __get_ativos_renda_fixa_nao_precificados_anbima_fundos_bradesco_e_avisos(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        nome_arq_xls_caracteristicas_fundos: str,
        nome_arq_xlsx_depara_ativos_credito_privado: str,
        nome_arq_xlsx_depara_ativos_marcados_na_curva: str,
    ) -> tuple[DataFrame, list[Log]]:
        dataframe_caracteristicas_fundos: DataFrame = (
            self._get_dataframe_caracteristicas_fundos(
                nome_arq_xls_caracteristicas_fundos=nome_arq_xls_caracteristicas_fundos
            )
        )
        linhas_depara_ativos_credito_privado: list[LinhaDEPARACreditoPrivado] = (
            RendaFixaHelper.get_linhas_depara_ativos_credito_privado(
                nome_arq_xlsx_depara_ativos_credito_privado
            )
        )
        linhas_depara_ativos_marcados_na_curva: list[
            LinhaDEPARARendaFixaMarcadaNaCurva
        ] = RendaFixaHelper.get_linhas_depara_ativos_marcados_na_curva(
            nome_arq_xlsx_depara_ativos_marcados_na_curva
        )

        ativos_renda_fixa, avisos = (
            self.__get_ativos_renda_fixa_nao_precificados_anbima_fundos_bradesco_e_avisos_from_xmls(
                nomes_arqs_xmls_anbima_401=nomes_arqs_xmls_anbima_401,
                dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
                linhas_depara_ativos_credito_privado=linhas_depara_ativos_credito_privado,
                linhas_depara_ativos_marcados_na_curva=linhas_depara_ativos_marcados_na_curva,
            )
        )

        linhas_ativos_renda_fixa_nao_precificados_anbima: list[dict] = []
        for ativo_renda_fixa in ativos_renda_fixa:
            assert ativo_renda_fixa.data_referente
            assert ativo_renda_fixa.id_serie_britech
            assert ativo_renda_fixa.preco_unitario

            data_referente: date = ativo_renda_fixa.data_referente
            id_serie_britech: int = int(ativo_renda_fixa.id_serie_britech)
            valor: float = float(ativo_renda_fixa.preco_unitario)

            linha_ativo_credito_privado_nao_precificado_anbima: dict = {
                "Data": data_referente.strftime("%d/%m/%Y"),
                "IdSerie": int(id_serie_britech),
                "Valor": valor,
            }
            linhas_ativos_renda_fixa_nao_precificados_anbima.append(
                linha_ativo_credito_privado_nao_precificado_anbima
            )

        dataframe_ativos_credito_privado_nao_precificados_anbima: DataFrame = DataFrame(
            linhas_ativos_renda_fixa_nao_precificados_anbima
        )
        return (dataframe_ativos_credito_privado_nao_precificados_anbima, avisos)

    def __get_precos_ativos_credito_privado_em_fundos_nao_bradesco_e_avisos(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        nome_arq_xls_caracteristicas_fundos: str,
        nome_arq_xlsx_depara_ativos_credito_privado: str,
    ) -> tuple[DataFrame, list[Log]]:
        dataframe_caracteristicas_fundos: DataFrame = (
            self._get_dataframe_caracteristicas_fundos(
                nome_arq_xls_caracteristicas_fundos=nome_arq_xls_caracteristicas_fundos
            )
        )
        linhas_depara_ativos_credito_privado: list[LinhaDEPARACreditoPrivado] = (
            RendaFixaHelper.get_linhas_depara_ativos_credito_privado(
                nome_arq_xlsx_depara_ativos_credito_privado=nome_arq_xlsx_depara_ativos_credito_privado
            )
        )

        fundos_precos_ativos_em_fundos_nao_bradesco, avisos = (
            self.__get_precos_ativos_em_fundos_nao_bradesco_e_avisos_from_xmls(
                nomes_arqs_xmls_anbima_401=nomes_arqs_xmls_anbima_401,
                dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
                linhas_depara_ativos_credito_privado=linhas_depara_ativos_credito_privado,
            )
        )

        linhas_fundos_precos_ativos_em_fundos_nao_bradesco: list[dict] = []
        for fundo_preco_ativo in fundos_precos_ativos_em_fundos_nao_bradesco:
            assert fundo_preco_ativo.fundo_codigo_britech
            assert fundo_preco_ativo.titulo_credito_privado.id_titulo_britech
            assert fundo_preco_ativo.titulo_credito_privado.data_referente

            linha_preco_ativo_em_fundo_nao_bradesco: dict = {
                "IdCliente": int(fundo_preco_ativo.fundo_codigo_britech),
                "IdTitulo": int(
                    fundo_preco_ativo.titulo_credito_privado.id_titulo_britech
                ),
                "IdOperacao": "",
                "DtVigencia": date.strftime(
                    fundo_preco_ativo.titulo_credito_privado.data_referente, "%d/%m/%Y"
                ),
                "Taxa252": 0,
                "PuMTM": fundo_preco_ativo.titulo_credito_privado.preco_unitario,
            }

            linhas_fundos_precos_ativos_em_fundos_nao_bradesco.append(
                linha_preco_ativo_em_fundo_nao_bradesco
            )

        dataframe_precos_ativos_em_fundos_nao_bradesco: DataFrame = DataFrame(
            linhas_fundos_precos_ativos_em_fundos_nao_bradesco
        )
        return (dataframe_precos_ativos_em_fundos_nao_bradesco, avisos)

    def __get_ativos_renda_fixa_nao_precificados_anbima_fundos_bradesco_e_avisos_from_xmls(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        dataframe_caracteristicas_fundos: DataFrame,
        linhas_depara_ativos_credito_privado: list[LinhaDEPARACreditoPrivado],
        linhas_depara_ativos_marcados_na_curva: list[
            LinhaDEPARARendaFixaMarcadaNaCurva
        ],
    ) -> tuple[list[AtivoRendaFixa], list[Log]]:
        avisos: list[Log] = []
        ativos_renda_fixa: list[AtivoRendaFixa] = []

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
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            if root is None:
                aviso.mensagens.append(LogMensagem.FUNDO_CORROMPIDO)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            node_header: Element | None = root.find(Tags.HEADER.value)
            if node_header is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_CORROMPIDO)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            node_cnpj: Element | None = node_header.find(Tags.CNPJ.value)
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
                        id_label="cnpj", id_value=get_cnpj_com_formatacao(cnpj)
                    )
                )
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            fundo_controlador: str | None = (
                self._get_fundo_controlador_by_codigo_britech(
                    codigo_britech=fundo_codigo_britech,
                    dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
                )
            )
            if fundo_controlador is None:
                LogMensagem.get_fundo_administrador_nao_encontrado_caracteristicas_by_codigo_britech(
                    fundo_codigo_britech
                )
                if aviso not in avisos:
                    avisos.append(aviso)
                continue
            if fundo_controlador == "":
                LogMensagem.get_fundo_administrador_vazio_caracteristicas_by_codigo_britech(
                    fundo_codigo_britech
                )
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            if fundo_controlador != "Bradesco":
                continue

            node_data_posicao: Element | None = root.find(
                f".//{Tags.HEADER.value}/{Tags.DTPOSICAO.value}"
            )
            if node_data_posicao is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_DATA_POSICAO_CORROMPIDA)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue
            data_posicao: date | None = (
                datetime.strptime(node_data_posicao.text, "%Y%m%d").date()
                if node_data_posicao.text is not None
                else None
            )
            if data_posicao is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_DATA_POSICAO_CORROMPIDA)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            nodes_titulos_privados: list[Element] = list(
                root.findall(Tags.TITPRIVADO.value)
            )
            for node in nodes_titulos_privados:
                titulo_privado: AtivoRendaFixa | None = (
                    self.__get_titulo_credito_privado_e_appenda_avisos(
                        node_ativo=node,
                        nome_node_codigo_ativo=Tags.CODATIVO.value,
                        data_posicao=data_posicao,
                        linhas_depara_ativos_credito_privado=linhas_depara_ativos_credito_privado,
                        aviso=aviso,
                        avisos=avisos,
                    )
                )

                if titulo_privado is None:
                    continue

                if titulo_privado not in ativos_renda_fixa:
                    ativos_renda_fixa.append(titulo_privado)

            nodes_debentures: list[Element] = root.findall(Tags.DEBENTURE.value)
            for node in nodes_debentures:
                debenture: AtivoRendaFixa | None = (
                    self.__get_titulo_credito_privado_e_appenda_avisos(
                        node_ativo=node,
                        nome_node_codigo_ativo=Tags.CODDEB.value,
                        data_posicao=data_posicao,
                        linhas_depara_ativos_credito_privado=linhas_depara_ativos_credito_privado,
                        aviso=aviso,
                        avisos=avisos,
                    )
                )

                if debenture is None:
                    continue

                if debenture not in ativos_renda_fixa:
                    ativos_renda_fixa.append(debenture)

            nodes_titulos_publicos: list[Element] = root.findall(Tags.TITPUBLICO.value)
            for node in nodes_titulos_publicos:
                titulo_publico: AtivoRendaFixa | None = (
                    self.__get_titulo_publico_e_appenda_avisos(
                        node_titulo_publico=node,
                        data_posicao=data_posicao,
                        linhas_depara_ativos_marcados_na_curva=linhas_depara_ativos_marcados_na_curva,
                        aviso=aviso,
                        avisos=avisos,
                    )
                )

                if titulo_publico is None:
                    continue

                if titulo_publico not in ativos_renda_fixa:
                    ativos_renda_fixa.append(titulo_publico)

        return (ativos_renda_fixa, avisos)

    def __get_precos_ativos_em_fundos_nao_bradesco_e_avisos_from_xmls(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        dataframe_caracteristicas_fundos: DataFrame,
        linhas_depara_ativos_credito_privado: list[LinhaDEPARACreditoPrivado],
    ) -> tuple[list[FundoPrecoTituloPrivado], list[Log]]:
        avisos: list[Log] = []
        fundos_precos_titulos_privados: list[FundoPrecoTituloPrivado] = []

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
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            if root is None:
                aviso.mensagens.append(LogMensagem.FUNDO_CORROMPIDO)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            node_header: Element | None = root.find(Tags.HEADER.value)
            if node_header is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_CORROMPIDO)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            node_cnpj: Element | None = node_header.find(Tags.CNPJ.value)
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
                        id_label="cnpj", id_value=get_cnpj_com_formatacao(cnpj)
                    )
                )
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            fundo_controlador: str | None = (
                self._get_fundo_controlador_by_codigo_britech(
                    codigo_britech=fundo_codigo_britech,
                    dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
                )
            )
            if fundo_controlador is None:
                LogMensagem.get_fundo_administrador_nao_encontrado_caracteristicas_by_codigo_britech(
                    fundo_codigo_britech
                )
                if aviso not in avisos:
                    avisos.append(aviso)
                continue
            if fundo_controlador == "":
                LogMensagem.get_fundo_administrador_vazio_caracteristicas_by_codigo_britech(
                    fundo_codigo_britech
                )
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            if fundo_controlador == "Bradesco":
                continue

            node_data_posicao: Element | None = root.find(
                f".//{Tags.HEADER.value}/{Tags.DTPOSICAO.value}"
            )
            if node_data_posicao is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_DATA_POSICAO_CORROMPIDA)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue
            data_posicao: date | None = (
                datetime.strptime(node_data_posicao.text, "%Y%m%d").date()
                if node_data_posicao.text is not None
                else None
            )
            if data_posicao is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_DATA_POSICAO_CORROMPIDA)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            node_titulos_privados: list[Element] | None = list(
                root.findall(Tags.TITPRIVADO.value)
            )
            if node_titulos_privados is None:
                aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PRIVADO_CORROMPIDO)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            for node in node_titulos_privados:
                titulo_privado: AtivoRendaFixa | None = (
                    self.__get_titulo_credito_privado_e_appenda_avisos(
                        node_ativo=node,
                        nome_node_codigo_ativo=Tags.CODATIVO.value,
                        data_posicao=data_posicao,
                        linhas_depara_ativos_credito_privado=linhas_depara_ativos_credito_privado,
                        aviso=aviso,
                        avisos=avisos,
                    )
                )

                if titulo_privado is None:
                    continue

                fundo_preco_titulo_privado: FundoPrecoTituloPrivado = (
                    FundoPrecoTituloPrivado(
                        fundo_codigo_britech=fundo_codigo_britech,
                        titulo_credito_privado=titulo_privado,
                    )
                )

                if fundo_preco_titulo_privado not in fundos_precos_titulos_privados:
                    fundos_precos_titulos_privados.append(fundo_preco_titulo_privado)

            node_debentures: list[Element] | None = root.findall(Tags.DEBENTURE.value)
            if node_debentures is None:
                aviso.mensagens.append(LogMensagem.FUNDO_DEBENTURE_CORROMPIDA)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            for node in node_debentures:
                debenture: AtivoRendaFixa | None = (
                    self.__get_titulo_credito_privado_e_appenda_avisos(
                        node_ativo=node,
                        nome_node_codigo_ativo=Tags.CODDEB.value,
                        data_posicao=data_posicao,
                        linhas_depara_ativos_credito_privado=linhas_depara_ativos_credito_privado,
                        aviso=aviso,
                        avisos=avisos,
                    )
                )

                if debenture is None:
                    continue

                fundo_preco_titulo_privado: FundoPrecoTituloPrivado = (
                    FundoPrecoTituloPrivado(
                        fundo_codigo_britech=fundo_codigo_britech,
                        titulo_credito_privado=debenture,
                    )
                )

                if fundo_preco_titulo_privado not in fundos_precos_titulos_privados:
                    fundos_precos_titulos_privados.append(fundo_preco_titulo_privado)

        return (fundos_precos_titulos_privados, avisos)

    def __get_titulo_credito_privado_e_appenda_avisos(
        self,
        node_ativo: Element,
        nome_node_codigo_ativo: Literal["codativo", "coddeb"],
        data_posicao: date,
        linhas_depara_ativos_credito_privado: list[LinhaDEPARACreditoPrivado],
        aviso: Log,
        avisos: list[Log],
    ) -> AtivoRendaFixa | None:
        node_codigo: Element | None = node_ativo.find(nome_node_codigo_ativo)
        if node_codigo is None:
            if nome_node_codigo_ativo == "codativo":
                aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PRIVADO_CORROMPIDO)
            else:
                aviso.mensagens.append(LogMensagem.FUNDO_DEBENTURE_CORROMPIDA)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        codigo: str | None = node_codigo.text
        if codigo is None:
            if nome_node_codigo_ativo == "codativo":
                aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PRIVADO_CORROMPIDO)
            else:
                aviso.mensagens.append(LogMensagem.FUNDO_DEBENTURE_CORROMPIDA)
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        id_serie_britech: str | None = (
            RendaFixaHelper.get_id_serie_britech_from_ativo_codigo_cetip(
                codigo_cetip=codigo,
                linhas_depara_ativos_credito_privado=linhas_depara_ativos_credito_privado,
            )
        )
        id_titulo_britech: str | None = (
            RendaFixaHelper.get_id_titulo_britech_from_ativo_codigo_cetip(
                codigo_cetip=codigo,
                linhas_depara_ativos_credito_privado=linhas_depara_ativos_credito_privado,
            )
        )
        if id_serie_britech is None:
            return None

        node_isin: Element | None = node_ativo.find(Tags.ISIN.value)
        if node_isin is None:
            if nome_node_codigo_ativo == "codativo":
                aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PRIVADO_CORROMPIDO)
            else:
                aviso.mensagens.append(LogMensagem.FUNDO_DEBENTURE_CORROMPIDA)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        isin: str | None = node_isin.text
        if isin is None:
            if nome_node_codigo_ativo == "codativo":
                aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PRIVADO_CORROMPIDO)
            else:
                aviso.mensagens.append(LogMensagem.FUNDO_DEBENTURE_CORROMPIDA)
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        node_pu_posicao: Element | None = node_ativo.find(Tags.PUPOSICAO.value)
        if node_pu_posicao is None:
            if nome_node_codigo_ativo == "codativo":
                aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PRIVADO_CORROMPIDO)
            else:
                aviso.mensagens.append(LogMensagem.FUNDO_DEBENTURE_CORROMPIDA)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        pu_posicao: float | None = (
            float(node_pu_posicao.text) if node_pu_posicao.text is not None else None
        )
        if pu_posicao is None:
            if nome_node_codigo_ativo == "codativo":
                aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PRIVADO_CORROMPIDO)
            else:
                aviso.mensagens.append(LogMensagem.FUNDO_DEBENTURE_CORROMPIDA)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        preco_unitario: float = pu_posicao

        titulo_privado: AtivoRendaFixa = AtivoRendaFixa(
            isin=isin,
            codigo=codigo,
            data_referente=data_posicao,
            preco_unitario=preco_unitario,
            id_titulo_britech=id_titulo_britech,
            id_serie_britech=id_serie_britech,
        )

        return titulo_privado

    def __get_titulo_publico_e_appenda_avisos(
        self,
        node_titulo_publico: Element,
        data_posicao: date,
        linhas_depara_ativos_marcados_na_curva: list[
            LinhaDEPARARendaFixaMarcadaNaCurva
        ],
        aviso: Log,
        avisos: list[Log],
    ) -> AtivoRendaFixa | None:
        node_codigo: Element | None = node_titulo_publico.find(Tags.CODATIVO.value)
        if node_codigo is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        codigo: str | None = node_codigo.text
        if codigo is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        node_isin: Element | None = node_titulo_publico.find(Tags.ISIN.value)
        if node_isin is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        isin: str | None = node_isin.text
        if isin is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        node_id_interno_ativo: Element | None = node_titulo_publico.find(
            Tags.IDINTERNOATIVO.value
        )
        if node_id_interno_ativo is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        id_interno_ativo: str | None = node_id_interno_ativo.text
        if id_interno_ativo is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        id_serie_britech: str | None = (
            RendaFixaHelper.get_id_serie_britech_from_ativo_id_interno(
                id_interno=id_interno_ativo,
                linhas_depara_ativos_precificados_na_curva=linhas_depara_ativos_marcados_na_curva,
            )
        )
        if id_serie_britech is None:
            return None

        node_pu_posicao: Element | None = node_titulo_publico.find(Tags.PUPOSICAO.value)
        if node_pu_posicao is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        pu_posicao: float | None = (
            float(node_pu_posicao.text) if node_pu_posicao.text is not None else None
        )
        if pu_posicao is None:
            aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PUBLICO_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        preco_unitario: float = pu_posicao

        titulo_publico: AtivoRendaFixa = AtivoRendaFixa(
            isin=isin,
            codigo=codigo,
            data_referente=data_posicao,
            preco_unitario=preco_unitario,
            id_titulo_britech=None,
            id_serie_britech=id_serie_britech,
        )

        return titulo_publico
