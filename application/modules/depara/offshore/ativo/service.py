from pandas import read_excel, DataFrame
from typing import Literal

from modules.posicao.xml_anbima_401.enums import Tags
from .types import DeParaLinhaOffshoreAtivo


class DeParaOffshoreAtivoService:
    buffer_xlsm_depara_ativos_offshore: bytes

    def __init__(self, buffer_xlsm_depara_ativos_offshore: bytes):
        self.buffer_xlsm_depara_ativos_offshore = buffer_xlsm_depara_ativos_offshore

    def get_depara_linha_offshore_ativo(
        self,
        codigo_ativo_objeto: str,
        xml_tag: Literal[Tags.FUTUROS, Tags.OPCOESDERIV, Tags.OPCOESACOES],
    ) -> DeParaLinhaOffshoreAtivo | None:
        linhas_depara_ativos: list[DeParaLinhaOffshoreAtivo] = (
            self.__get_linhas_depara_ativos_offshore_from_xlsm()
        )
        linhas_depara_procuradas: list[DeParaLinhaOffshoreAtivo] = [
            depara_linha
            for depara_linha in linhas_depara_ativos
            if depara_linha.xml_tag == xml_tag.value
        ]

        for linha in linhas_depara_procuradas:
            if linha.xml_codigo_ativo_objeto == codigo_ativo_objeto:
                return linha

        return None

    def __get_linhas_depara_ativos_offshore_from_xlsm(
        self,
    ) -> list[DeParaLinhaOffshoreAtivo]:
        dataframe_depara_derivativos: DataFrame = (
            self.__get_dataframe_depara_ativos_offshore(
                self.buffer_xlsm_depara_ativos_offshore
            )
        )

        linhas_depara_derivativos: list[DeParaLinhaOffshoreAtivo] = []
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

            linha: DeParaLinhaOffshoreAtivo = DeParaLinhaOffshoreAtivo(
                xml_tag=xml_tag,
                xml_codigo_ativo_objeto=xml_codigo_ativo_objeto,
                bloomberg_codigo_ativo_objeto=bloomberg_codigo_ativo_objeto,
                tamanho_lote=tamanho_lote,
            )
            linhas_depara_derivativos.append(linha)

        return linhas_depara_derivativos

    def __get_dataframe_depara_ativos_offshore(
        self,
        buffer_xlsm_depara_ativos_offshore: bytes,
    ) -> DataFrame:
        NOME_SHEET: str = "De-Para"

        dataframe: DataFrame = read_excel(
            buffer_xlsm_depara_ativos_offshore, engine="openpyxl", sheet_name=NOME_SHEET
        )
        dataframe.columns = dataframe.columns.str.replace(" ", "_")

        return dataframe

    def get_mensagem_aviso_ativo_nao_encontrado(
        self, tipo_ativo: str, identificador_ativo: str
    ) -> str:
        return f'{tipo_ativo} "{identificador_ativo}" não encontrado na planiha de DE/PARA Offshore'

    def get_mensagem_aviso_ativo_sem_tamanho_lote(
        self, tipo_ativo: str, identificador_ativo: str
    ) -> str:
        return f'{tipo_ativo} "{identificador_ativo}" sem tamanho lote cadastrado na planilha de DE/PARA Offshore'

    def get_mensagem_aviso_ativo_encontrado(
        self, tipo_ativo: str, identificador_ativo: str
    ) -> str:
        return f'{tipo_ativo} "{identificador_ativo}" encontrado na planilha de DE/PARA Offshore'
