from datetime import date, datetime
from io import BytesIO
from json import dumps
from pandas import DataFrame, read_excel
from typing import Literal
from xml.etree.ElementTree import fromstring, Element, ParseError
from zipfile import ZipFile

from modules.posicao.xml_anbima_401.enums import Tags
from modules.util.temp_file import TempFileHelper
from .types import OffshoreLinhaDEPARABond
from ..service import LiberacaoCotasService
from ..types import Log, LogMensagem, AtivoRendaFixa


class BondsOffshoreService(LiberacaoCotasService):
    def get_zip_buffer_offshore_bonds_offshore(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        nome_arq_xlsx_depara_bonds_offshore: str,
        usdbrl: float,
    ) -> tuple[BytesIO, str]:
        dataframe_bonds, avisos = self.__get_bonds_offshore_e_avisos(
            usdbrl=usdbrl,
            nomes_arqs_xmls_anbima_401=nomes_arqs_xmls_anbima_401,
            nome_arq_xlsx_depara_bonds_offshore=nome_arq_xlsx_depara_bonds_offshore,
        )

        SHEET_NAME: str = "IMPORTACAO_COTACAO_SERIE_BRIT"
        buffer_excel_bonds_offshore: BytesIO = self._get_excel_buffer(
            dataframe=dataframe_bonds, sheet_name=SHEET_NAME
        )

        zip_buffer: BytesIO = BytesIO()
        nome_arquivo_xlsx_bonds: str = "ImportacaoCotacaoSerie_Offshore.xlsx"

        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr(
                nome_arquivo_xlsx_bonds, buffer_excel_bonds_offshore.read()
            )

        avisos_dicts = [aviso.__dict__ for aviso in avisos]

        return (zip_buffer, dumps(avisos_dicts))

    def __get_bonds_offshore_e_avisos(
        self,
        usdbrl: float,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        nome_arq_xlsx_depara_bonds_offshore: str,
    ) -> tuple[DataFrame, list[Log]]:
        linhas_depara_bonds: list[OffshoreLinhaDEPARABond] = (
            self.__get_linhas_depara_bonds_offshore(nome_arq_xlsx_depara_bonds_offshore)
        )

        bonds, avisos = self.__get_bonds_e_avisos_from_xmls(
            usdbrl=usdbrl,
            nomes_arqs_xmls_anbima_401=nomes_arqs_xmls_anbima_401,
            linhas_depara_bonds=linhas_depara_bonds,
        )

        linhas_bonds: list[dict] = []
        for bond in bonds:
            assert bond.data_referente
            assert bond.id_serie_britech
            assert bond.preco_unitario

            data_referente: date = bond.data_referente
            id_serie_britech: int = int(bond.id_serie_britech)
            valor: float = bond.preco_unitario

            linha_bond: dict = {
                "Data": data_referente.strftime("%d/%m/%Y"),
                "IdSerie": id_serie_britech,
                "Valor": valor,
            }
            linhas_bonds.append(linha_bond)

        dataframe_bonds: DataFrame = DataFrame(linhas_bonds)
        return (dataframe_bonds, avisos)

    def __get_linhas_depara_bonds_offshore(
        self,
        nome_arq_xlsx_depara_bonds: str,
    ) -> list[OffshoreLinhaDEPARABond]:
        buffer_arq_xlsx_depara_bonds: bytes = TempFileHelper.get_conteudo_e_deleta(
            nome_arq_xlsx_depara_bonds
        )
        dataframe_depara_bonds: DataFrame = self.__get_dataframe_depara_bonds(
            buffer_arq_xlsx_depara_bonds
        )

        linhas_depara_bonds: list[OffshoreLinhaDEPARABond] = []

        for _, row in dataframe_depara_bonds.iterrows():
            id_serie_britech: str = str(row["ID_SERIE_BRITECH"])
            isin: str = str(row["ISIN"])
            nome_ativo: str = str(row["ATIVO"])

            linha: OffshoreLinhaDEPARABond = OffshoreLinhaDEPARABond(
                id_serie_britech=id_serie_britech, isin=isin, nome_ativo=nome_ativo
            )
            linhas_depara_bonds.append(linha)

        return linhas_depara_bonds

    def __get_bonds_e_avisos_from_xmls(
        self,
        usdbrl: float,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        linhas_depara_bonds: list[OffshoreLinhaDEPARABond],
    ) -> tuple[list[AtivoRendaFixa], list[Log]]:
        avisos: list[Log] = []
        titulos_privados: list[AtivoRendaFixa] = []

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
                if self.__is_node_ativo_offshore(node) == False:
                    continue

                titulo_privado: AtivoRendaFixa | None | Literal[-1] = (
                    self.__get_bond_offshore(
                        node_titulo_privado=node,
                        usdbrl=usdbrl,
                        data_posicao=data_posicao,
                        linhas_depara_bonds=linhas_depara_bonds,
                        aviso=aviso,
                    )
                )

                if titulo_privado is None:
                    aviso.mensagens.append(LogMensagem.FUNDO_TITULO_PRIVADO_CORROMPIDO)
                    if aviso not in avisos:
                        avisos.append(aviso)
                    continue

                if type(titulo_privado) == int:
                    if aviso not in avisos:
                        avisos.append(aviso)
                    continue

                if titulo_privado not in titulos_privados:
                    assert type(titulo_privado) == AtivoRendaFixa
                    titulos_privados.append(titulo_privado)

        return (titulos_privados, avisos)

    def __get_dataframe_depara_bonds(
        self,
        buffer_arq_xlsx_depara_bonds: bytes,
    ) -> DataFrame:
        dataframe: DataFrame = read_excel(
            buffer_arq_xlsx_depara_bonds, engine="openpyxl"
        )
        dataframe.columns = dataframe.columns.str.replace(" ", "_")

        return dataframe

    def __is_node_ativo_offshore(
        self,
        xml_node: Element,
    ):
        isin_node: Element | None = xml_node.find(f".//{Tags.ISIN.value}")

        if isin_node is None:
            return False

        isin: str | None = isin_node.text

        if isin is None or isin.startswith("BR"):
            return False

        return True

    def __get_bond_offshore(
        self,
        node_titulo_privado: Element,
        usdbrl: float,
        data_posicao: date,
        linhas_depara_bonds: list[OffshoreLinhaDEPARABond],
        aviso: Log,
    ) -> AtivoRendaFixa | None | Literal[-1]:
        node_codigo: Element | None = node_titulo_privado.find(Tags.CODATIVO.value)
        if node_codigo is None:
            return None
        codigo: str | None = node_codigo.text
        if codigo is None:
            return None

        node_isin: Element | None = node_titulo_privado.find(Tags.ISIN.value)
        if node_isin is None:
            return None
        isin: str | None = node_isin.text
        if isin is None:
            return None

        node_pu_posicao: Element | None = node_titulo_privado.find(Tags.PUPOSICAO.value)
        if node_pu_posicao is None:
            return None
        pu_posicao: float | None = (
            float(node_pu_posicao.text) if node_pu_posicao.text is not None else None
        )
        if pu_posicao is None:
            return None
        preco_unitario: float = pu_posicao / usdbrl

        linha_depara_bonds: OffshoreLinhaDEPARABond | None = (
            self.__get_linha_depara_bonds_by_isin(
                isin=isin, linhas_depara_bonds=linhas_depara_bonds
            )
        )

        if linha_depara_bonds is None:
            aviso.mensagens.append(
                LogMensagem.get_fundo_titulo_privado_nao_encontrado_depara_bonds(
                    codigo_xml=codigo,
                    isin=isin,
                )
            )
            return -1

        id_serie_britech: str = linha_depara_bonds.id_serie_britech
        titulo_privado: AtivoRendaFixa = AtivoRendaFixa(
            isin=isin,
            codigo=codigo,
            data_referente=data_posicao,
            preco_unitario=preco_unitario,
            id_serie_britech=id_serie_britech,
            id_titulo_britech=None,
        )

        return titulo_privado

    def __get_linha_depara_bonds_by_isin(
        self,
        isin: str,
        linhas_depara_bonds: list[OffshoreLinhaDEPARABond],
    ) -> OffshoreLinhaDEPARABond | None:
        for linha in linhas_depara_bonds:
            if isin == linha.isin:
                return linha

        return None
