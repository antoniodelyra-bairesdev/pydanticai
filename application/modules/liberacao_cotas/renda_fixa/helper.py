from datetime import date, datetime
from pandas import DataFrame, read_excel

from modules.util.temp_file import TempFileHelper
from .types import LinhaDEPARACreditoPrivado, LinhaDEPARARendaFixaMarcadaNaCurva


class RendaFixaHelper:
    @staticmethod
    def get_linhas_depara_ativos_credito_privado(
        nome_arq_xlsx_depara_ativos_credito_privado: str,
    ) -> list[LinhaDEPARACreditoPrivado]:
        buffer_arq_xlsx_depara: bytes = TempFileHelper.get_conteudo_e_deleta(
            nome_arq_xlsx_depara_ativos_credito_privado
        )
        dataframe_depara: DataFrame = RendaFixaHelper.__get_dataframe_depara(
            buffer_arq_xlsx_depara
        )

        linhas_depara: list[LinhaDEPARACreditoPrivado] = []
        for _, row in dataframe_depara.iterrows():
            codigo_cetip: str = str(row["Codigo_Cetip"]).strip()
            id_titulo_britech: str = str(row["Id_Titulo"]).strip()
            id_serie_britech: str = str(row["Id_Serie"]).strip()
            tipo: str = str(row["Descricao"]).strip()
            isin: str | None = row["ISIN"]

            if row["ISIN"] == 0 or row["ISIN"] == "0" or row["ISIN"] == "":
                isin = None
            else:
                isin = str(row["ISIN"])

            linha: LinhaDEPARACreditoPrivado = LinhaDEPARACreditoPrivado(
                codigo_cetip=codigo_cetip,
                id_titulo=id_titulo_britech,
                id_serie=id_serie_britech,
                tipo=tipo,
                isin=isin,
            )
            linhas_depara.append(linha)

        return linhas_depara

    @staticmethod
    def get_linhas_depara_ativos_marcados_na_curva(
        nome_arq_xlsx_depara_ativos_marcados_na_curva: str,
    ) -> list[LinhaDEPARARendaFixaMarcadaNaCurva]:
        buffer_arq_xlsx_depara: bytes = TempFileHelper.get_conteudo_e_deleta(
            nome_arq_xlsx_depara_ativos_marcados_na_curva
        )
        dataframe_depara: DataFrame = RendaFixaHelper.__get_dataframe_depara(
            buffer_arq_xlsx_depara
        )

        linhas_depara: list[LinhaDEPARARendaFixaMarcadaNaCurva] = []
        for _, row in dataframe_depara.iterrows():
            codigo_operacao: str = str(row["Cod_Oper"]).strip()
            ativo: str = str(row["Ativo"]).strip()
            data_vencimento: date = row["Vencimento"]
            id_serie: str = str(row["ID_Serie"]).strip()

            linha: LinhaDEPARARendaFixaMarcadaNaCurva = (
                LinhaDEPARARendaFixaMarcadaNaCurva(
                    id_interno_ativo=codigo_operacao,
                    ativo=ativo,
                    data_vencimento=data_vencimento,
                    id_serie=id_serie,
                )
            )
            linhas_depara.append(linha)

        return linhas_depara

    @staticmethod
    def get_id_serie_britech_from_ativo_codigo_cetip(
        codigo_cetip: str,
        linhas_depara_ativos_credito_privado: list[LinhaDEPARACreditoPrivado],
    ) -> str | None:
        for linha in linhas_depara_ativos_credito_privado:
            if codigo_cetip == linha.codigo_cetip:
                return linha.id_serie

        return None

    @staticmethod
    def get_id_titulo_britech_from_ativo_codigo_cetip(
        codigo_cetip: str,
        linhas_depara_ativos_credito_privado: list[LinhaDEPARACreditoPrivado],
    ) -> str | None:
        for linha in linhas_depara_ativos_credito_privado:
            if codigo_cetip == linha.codigo_cetip:
                return linha.id_titulo

        return None

    @staticmethod
    def get_id_serie_britech_from_ativo_id_interno(
        id_interno: str,
        linhas_depara_ativos_precificados_na_curva: list[
            LinhaDEPARARendaFixaMarcadaNaCurva
        ],
    ) -> str | None:
        for linha in linhas_depara_ativos_precificados_na_curva:
            if id_interno == linha.id_interno_ativo:
                return linha.id_serie

        return None

    @staticmethod
    def __get_dataframe_depara(
        buffer_arq_xlsx_depara: bytes,
    ) -> DataFrame:
        dataframe: DataFrame = read_excel(
            buffer_arq_xlsx_depara,
            engine="openpyxl",
        )
        dataframe.columns = dataframe.columns.str.replace(" ", "_")

        return dataframe
