from pandas import DataFrame, read_excel
from numpy import nan

from .types import LinhaDeparaCotaFundo


class DeparaCotasService:
    __linhas_depara_cotas_fundos: list[LinhaDeparaCotaFundo]

    def __init__(self, buffer_xlsx_depara_cotas: bytes):
        self.__linhas_depara_cotas_fundos = self.__get_linhas_depara_cotas_fundos(
            buffer_xlsx_depara_cotas
        )

    def get_linhas_depara_cotas_fundos(self) -> list[LinhaDeparaCotaFundo]:
        return self.__linhas_depara_cotas_fundos

    def get_linha_depara_cota_fundo_by_isin(
        self,
        isin: str,
    ) -> LinhaDeparaCotaFundo | None:
        for linha in self.__linhas_depara_cotas_fundos:
            if linha.isin == isin:
                return linha

        return None

    @staticmethod
    def get_fundo_codigo_britech_nao_encontrado_depara_cotas(isin: str) -> str:
        return f'Cota de fundo de isin "{isin}" não encontrada na planilha de DE/PARA cotas de fundos'

    def __get_linhas_depara_cotas_fundos(
        self, buffer_xlsx_depara_cotas
    ) -> list[LinhaDeparaCotaFundo]:
        dataframe_depara: DataFrame = self.__get_dataframe_depara_cotas_fundos(
            buffer_xlsx_depara_cotas
        )
        dataframe_depara = dataframe_depara.replace(nan, None)
        dataframe_depara = dataframe_depara.replace("", None)

        linhas_depara: list[LinhaDeparaCotaFundo] = []
        for _, row in dataframe_depara.iterrows():
            id_carteira: str = str(row["Id_Pessoa"]).strip()
            apelido_fundo: str = str(row["Apelido"]).strip()
            nome_fundo: str = str(row["Nome"]).strip()
            tipo: str = str(row["Tipo"]).strip()

            cnpj: str | None = (
                str(row["CPF/Cnpj"]).strip()
                if str(row["CPF/Cnpj"]).strip() != ""
                else None
            )

            isin: str | None = (
                str(row["ISIN"]).strip() if str(row["ISIN"]).strip() != "" else None
            )
            if isin is None:
                continue

            codigo_interface: str | None = (
                row["Código_Interface"] if str(row["Código_Interface"]) != "" else None
            )

            codigo_britech_fundo_espelho: str | None = (
                str(row["Cod._Britech_Fundo_Espelho"])
                if row["Cod._Britech_Fundo_Espelho"] is not None
                else None
            )

            linha: LinhaDeparaCotaFundo = LinhaDeparaCotaFundo(
                id_carteira=id_carteira,
                apelido_fundo=apelido_fundo,
                nome_fundo=nome_fundo,
                tipo=tipo,
                cnpj=cnpj,
                isin=isin,
                codigo_interface=codigo_interface,
                codigo_britech_fundo_espelho=codigo_britech_fundo_espelho,
            )
            linhas_depara.append(linha)

        return linhas_depara

    def __get_dataframe_depara_cotas_fundos(
        self,
        buffer_arq_xlsx_depara_cotas_fundos: bytes,
    ) -> DataFrame:
        dataframe: DataFrame = read_excel(
            buffer_arq_xlsx_depara_cotas_fundos,
            engine="openpyxl",
            dtype={
                "CPF/Cnpj": str,
                "Id Pessoa": str,
                "Cod. Britech Fundo Espelho": str,
            },
            header=0,
        )
        dataframe.columns = dataframe.columns.str.replace(" ", "_")
        dataframe["CPF/Cnpj"] = dataframe["CPF/Cnpj"].astype(str)

        return dataframe
