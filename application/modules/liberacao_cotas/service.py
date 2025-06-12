from datetime import date
from dateutil.relativedelta import relativedelta
from fastapi.datastructures import UploadFile
from io import BytesIO
from math import isnan
from numpy import busday_offset
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
from pandas import ExcelWriter, DataFrame, read_excel

from modules.util.temp_file import TempFileHelper
from modules.util.string import get_cnpj_sem_formatacao


class LiberacaoCotasService:
    identificador_arqs_temp: str

    def __init__(self, identificador_arqs_temp) -> None:
        self.identificador_arqs_temp = identificador_arqs_temp

    async def cria_arqs_temporarios(self, arqs: list[UploadFile]) -> list[str]:
        nomes_arqs: list[str] = []

        for arq in arqs:
            nome_arq: str = await TempFileHelper.async_cria(
                arq, self.identificador_arqs_temp
            )
            nomes_arqs.append(nome_arq)

        return nomes_arqs

    def _get_excel_buffer(self, dataframe: DataFrame, sheet_name: str) -> BytesIO:
        buffer_excel = BytesIO()
        writer = ExcelWriter(buffer_excel, engine="openpyxl")

        with ExcelWriter(buffer_excel, engine="openpyxl") as writer:
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)

            assert isinstance(writer.book.active, Worksheet)
            writer.book.active.protection.sheet = False
            writer.book.active.protection.disable()
            self._formata_excel_sheet(writer.book.active)

        buffer_excel.seek(0)
        return buffer_excel

    def _formata_excel_sheet(self, worksheet: Worksheet) -> None:
        for column in worksheet.columns:
            length = max(len(str(cell.value) or "") for cell in column)
            worksheet.column_dimensions[get_column_letter(column[0].column)].width = (
                length + 4
            )

        return None

    def _get_d_util_menos_1(self, data_input: date) -> date:
        dia_anterior: date = data_input - relativedelta(days=1)

        dia_util_anterior: date = busday_offset(
            dates=dia_anterior, offsets=0, roll="backward"
        ).astype(date)

        return dia_util_anterior

    def _get_dataframe_caracteristicas_fundos(
        self,
        nome_arq_xls_caracteristicas_fundos: str,
    ) -> DataFrame:
        buffer_arq_xls_caracteristicas_fundos = TempFileHelper.get_conteudo_e_deleta(
            nome_arq_xls_caracteristicas_fundos
        )

        sheet_name: str = "Gestão Icatu"
        dataframe: DataFrame = read_excel(
            buffer_arq_xls_caracteristicas_fundos, sheet_name=sheet_name, dtype="object"
        )

        return dataframe

    def _get_fundo_codigo_britech_by_fundo_codigo_administrador(
        self,
        fundo_codigo_administrador: str,
        dataframe_caracteristicas_fundos: DataFrame,
    ) -> int | None:
        NOME_COLUNA_CODIGO_ADMINISTRADOR: str = "Código ADMINISTRADOR"
        NOME_COLUNA_CODIGO_BRIT: str = "Cód. Brit"

        dataframe_caracteristicas_fundos[NOME_COLUNA_CODIGO_ADMINISTRADOR] = (
            dataframe_caracteristicas_fundos[NOME_COLUNA_CODIGO_ADMINISTRADOR].astype(
                str
            )
        )

        for _, row in dataframe_caracteristicas_fundos.iterrows():
            codigo_administrador_procurado: str = str(
                row[NOME_COLUNA_CODIGO_ADMINISTRADOR]
            ).strip()

            if (
                codigo_administrador_procurado == fundo_codigo_administrador
                or codigo_administrador_procurado.lstrip("0")
                == fundo_codigo_administrador
            ):
                return int(row[NOME_COLUNA_CODIGO_BRIT])

        return None

    def _get_fundo_codigo_britech_by_fundo_codigo_corretora(
        self,
        fundo_codigo_corretora: str,
        dataframe_caracteristicas_fundos: DataFrame,
    ) -> str | None:
        for _, row in dataframe_caracteristicas_fundos.iterrows():
            if str(row["Código BMF (Bradesco Corretora)"]) == fundo_codigo_corretora:
                return row["Cód. Brit"]

        return None

    def _get_fundo_codigo_britech_by_cnpj(
        self,
        cnpj: str,
        dataframe_caracteristicas_fundos: DataFrame,
    ) -> str | None:
        for _, row in dataframe_caracteristicas_fundos.iterrows():
            cnpj_procurado: str = get_cnpj_sem_formatacao(str(row["CNPJ"]))

            if cnpj == cnpj_procurado:
                codigo_brit: int = row["Cód. Brit"]
                if isnan(codigo_brit):
                    return None

                return str(codigo_brit)

        return None

    def _get_fundo_administrador_by_codigo_britech(
        self,
        codigo_britech: str,
        dataframe_caracteristicas_fundos: DataFrame,
    ) -> str | None:
        for _, row in dataframe_caracteristicas_fundos.iterrows():
            codigo_britech_procurado: str = str(row["Cód. Brit"])

            if codigo_britech == codigo_britech_procurado:
                administrador: str = row["ADMINISTRADOR"]
                return administrador

        return None

    def _get_fundo_controlador_by_codigo_britech(
        self,
        codigo_britech: str,
        dataframe_caracteristicas_fundos: DataFrame,
    ) -> str | None:
        for _, row in dataframe_caracteristicas_fundos.iterrows():
            codigo_britech_procurado: str = str(row["Cód. Brit"])

            if codigo_britech == codigo_britech_procurado:
                controlador: str = row["CONTROLADOR"]
                return controlador

        return None

    def _get_fundo_controlador_by_cnpj(
        self,
        cnpj: str,
        dataframe_caracteristicas_fundos: DataFrame,
    ) -> str | None:
        for _, row in dataframe_caracteristicas_fundos.iterrows():
            cnpj_procurado: str = str(row["CNPJ"])

            if cnpj == cnpj_procurado:
                controlador: str = row["CONTROLADOR"]
                return controlador

        return None
