from math import isnan
from pandas import DataFrame

from .types import FundoInfo
from modules.util.string import get_cnpj_sem_formatacao, get_cnpj_com_formatacao


class CaracteristicasFundosService:
    dataframe_caracteristicas_fundos: DataFrame

    def __init__(self, dataframe_caracteristicas_fundos: DataFrame):
        self.dataframe_caracteristicas_fundos = dataframe_caracteristicas_fundos

    def get_fundo_codigo_britech_from_cnpj(
        self,
        fundo_cnpj: str,
    ) -> str | None:
        for _, row in self.dataframe_caracteristicas_fundos.iterrows():
            cnpj_procurado: str = get_cnpj_sem_formatacao(str(row["CNPJ"]))

            if fundo_cnpj == cnpj_procurado:
                codigo_brit: int = row["Cód. Brit"]
                if isnan(codigo_brit):
                    return None

                return str(codigo_brit)

        return None

    def get_fundo_nome_by_cnpj(
        self,
        cnpj: str,
    ) -> str | None:
        for _, row in self.dataframe_caracteristicas_fundos.iterrows():
            cnpj_procurado: str = get_cnpj_sem_formatacao(str(row["CNPJ"]))

            if cnpj == cnpj_procurado:
                nome_fundo: str = str(row["NOME DO FUNDO"])
                return nome_fundo

        return None

    def get_fundo_custodiante_by_cnpj(
        self,
        cnpj: str,
    ) -> str | None:
        for _, row in self.dataframe_caracteristicas_fundos.iterrows():
            cnpj_procurado: str = get_cnpj_sem_formatacao(str(row["CNPJ"]))

            if cnpj == cnpj_procurado:
                custodiante: str = str(row["CUSTODIANTE"])
                return custodiante

        return None

    def get_fundo_codigo_administrador_by_cnpj(
        self,
        cnpj: str,
    ) -> str | None:
        for _, row in self.dataframe_caracteristicas_fundos.iterrows():
            cnpj_procurado: str = get_cnpj_sem_formatacao(str(row["CNPJ"]))

            if cnpj == cnpj_procurado:
                codigo_administrador: str = str(row["Código ADMINISTRADOR"])
                return codigo_administrador

        return None

    def get_fundo_tipo_cota_by_cnpj(self, cnpj: str) -> str | None:
        for _, row in self.dataframe_caracteristicas_fundos.iterrows():
            cnpj_procurado: str = get_cnpj_sem_formatacao(str(row["CNPJ"]))

            if cnpj == cnpj_procurado:
                tipo_cota: str = str(row["Tipo de Cota"])
                return tipo_cota

        return None

    def get_fundos_infos(self) -> list[FundoInfo]:
        fundos_infos: list[FundoInfo] = []
        for _, row in self.dataframe_caracteristicas_fundos.iterrows():
            codigo_britech: str = str(row["Cód. Brit"])
            if codigo_britech == "nan" or codigo_britech == "x":
                continue

            codigo_administrador: str = str(row["Código ADMINISTRADOR"])
            custodiante: str = str(row["CUSTODIANTE"])
            cnpj: str = get_cnpj_sem_formatacao(str(row["CNPJ"]))
            nome: str = row["NOME DO FUNDO"]
            tipo_cota: str = row["Tipo de Cota"]
            fundo_info: FundoInfo = FundoInfo(
                codigo_britech=codigo_britech,
                codigo_administrador=codigo_administrador,
                custodiante=custodiante,
                cnpj=cnpj,
                nome=nome,
                tipo_cota=tipo_cota,
            )
            fundos_infos.append(fundo_info)

        return fundos_infos

    @staticmethod
    def get_fundo_cnpj_nao_encontrado(fundo_cnpj: str) -> str:
        return f'Fundo de cnpj "{get_cnpj_com_formatacao(fundo_cnpj)}" não encontrado na planilha de características dos fundos'
