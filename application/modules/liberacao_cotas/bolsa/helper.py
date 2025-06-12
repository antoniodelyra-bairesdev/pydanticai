from typing import Literal
from pandas import DataFrame, read_excel
from xml.etree.ElementTree import Element

from modules.posicao.xml_anbima_401.enums import Tags
from modules.util.temp_file import TempFileHelper
from .types import (
    CodigosOpcao,
    OffshoreLinhaDEPARADerivativo,
    CodigosFuturo,
)


class BolsaHelper:
    @staticmethod
    def get_linha_depara_derivativos_by_xml_codigo_ativo_objeto(
        xml_tag: Literal[
            Tags.FUTUROS,
            Tags.OPCOESDERIV,
            Tags.OPCOESACOES,
        ],
        xml_codigo_ativo_objeto: str,
        linhas_depara_derivativos: list[OffshoreLinhaDEPARADerivativo],
    ) -> OffshoreLinhaDEPARADerivativo | None:
        depara_linhas_procuradas: list[OffshoreLinhaDEPARADerivativo] = [
            depara_linha
            for depara_linha in linhas_depara_derivativos
            if depara_linha.xml_tag == xml_tag.value
        ]

        for linha in depara_linhas_procuradas:
            if linha.xml_codigo_ativo_objeto == xml_codigo_ativo_objeto:
                return linha

        return None

    @staticmethod
    def get_tipo_opcao_acao_b3(codigo_opcao: str) -> Literal["C", "P"] | None:
        for char in reversed(codigo_opcao):
            if "A" <= char <= "L":
                return "C"
            if "M" <= char <= "X":
                return "P"

        return None

    @staticmethod
    def get_tipo_opcao_acao_offshore(codigo_opcao: str) -> Literal["C", "P"] | None:
        for char in reversed(codigo_opcao):
            if char == "C":
                return "C"
            if char == "P":
                return "P"

        return None

    @staticmethod
    def get_codigos_opcao_acao_offshore(xml_codigo: str) -> CodigosOpcao:
        indice_digito_call_ou_put: int
        if xml_codigo.rfind("C") != -1:
            indice_digito_call_ou_put = xml_codigo.rfind("C")
        elif xml_codigo.rfind("P") != -1:
            indice_digito_call_ou_put = xml_codigo.rfind("P")
        else:
            indice_digito_call_ou_put = -1

        LENGTH_CODIGO_VENCIMENTO = 6
        assert LENGTH_CODIGO_VENCIMENTO < indice_digito_call_ou_put

        indice_comeco_codigo_vencimento: int = (
            indice_digito_call_ou_put - LENGTH_CODIGO_VENCIMENTO
        )
        codigo_ativo_objeto: str = xml_codigo[:indice_comeco_codigo_vencimento]
        codigo_serie: str = xml_codigo[indice_comeco_codigo_vencimento:]

        return CodigosOpcao(
            codigo_ativo_objeto=codigo_ativo_objeto, codigo_serie=codigo_serie
        )

    @staticmethod
    def get_codigos_opcao_acao_b3(xml_codigo: str) -> CodigosOpcao:
        indice_digito_call_ou_put: int | None = None
        for i in range(len(xml_codigo) - 1, 0, -1):
            char = xml_codigo[i]

            if "A" <= char <= "X":
                indice_digito_call_ou_put = i

        assert indice_digito_call_ou_put
        codigo_ativo_objeto: str = xml_codigo[:indice_digito_call_ou_put]
        codigo_serie: str = xml_codigo[indice_digito_call_ou_put:]

        return CodigosOpcao(
            codigo_ativo_objeto=codigo_ativo_objeto, codigo_serie=codigo_serie
        )

    @staticmethod
    def get_codigos_futuros(xml_codigo: str) -> CodigosFuturo:
        codigo_ativo_objeto: str = xml_codigo[:-2]
        codigo_vencimento: str = xml_codigo[-2:]

        return CodigosFuturo(
            codigo_ativo_objeto=codigo_ativo_objeto, codigo_vencimento=codigo_vencimento
        )

    @staticmethod
    def get_codigo_serie_opcao(xml_codigo_serie: str, preco_exercicio: float) -> str:
        return xml_codigo_serie[0] + str(preco_exercicio).replace(".", "")

    @staticmethod
    def get_linhas_depara_derivativos(
        nome_arq_xlsm_depara_derivativos: str,
    ) -> list[OffshoreLinhaDEPARADerivativo]:
        buffer_arq_xlsm_depara_derivativos: bytes = (
            TempFileHelper.get_conteudo_e_deleta(nome_arq_xlsm_depara_derivativos)
        )
        dataframe_depara_derivativos: DataFrame = (
            BolsaHelper.__get_dataframe_depara_derivativos(
                buffer_arq_xlsm_depara_derivativos
            )
        )

        linhas_depara_derivativos: list[OffshoreLinhaDEPARADerivativo] = []

        for _, row in dataframe_depara_derivativos.iterrows():
            xml_tag: Literal[
                Tags.FUTUROS,
                Tags.OPCOESDERIV,
                Tags.OPCOESACOES,
            ] = row.classe
            xml_codigo_ativo_objeto: str = row["xml"]
            bloomberg_codigo_ativo_objeto: str = row["bbg_cod"]
            tamanho_lote: int | None = None

            if isinstance(row["lote"], int):
                tamanho_lote = abs(int(row["lote"]))

            linha: OffshoreLinhaDEPARADerivativo = OffshoreLinhaDEPARADerivativo(
                xml_tag=xml_tag,
                xml_codigo_ativo_objeto=xml_codigo_ativo_objeto,
                bloomberg_codigo_ativo_objeto=bloomberg_codigo_ativo_objeto,
                tamanho_lote=tamanho_lote,
            )
            linhas_depara_derivativos.append(linha)

        return linhas_depara_derivativos

    @staticmethod
    def is_node_ativo_offshore(xml_node: Element):
        isin_node: Element | None = xml_node.find(f".//{Tags.ISIN.value}")

        if isin_node is None:
            return False

        isin: str | None = isin_node.text

        if isin is None or isin.startswith("BR"):
            return False

        return True

    @staticmethod
    def __get_dataframe_depara_derivativos(
        buffer_arq_xlsm_derivativos: bytes,
    ) -> DataFrame:
        NOME_SHEET: str = "De-Para"

        dataframe: DataFrame = read_excel(
            buffer_arq_xlsm_derivativos, engine="openpyxl", sheet_name=NOME_SHEET
        )
        dataframe.columns = dataframe.columns.str.replace(" ", "_")

        return dataframe
