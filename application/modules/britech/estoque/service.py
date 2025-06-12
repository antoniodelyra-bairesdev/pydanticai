from datetime import date
from decimal import Decimal
from pandas import read_excel, to_datetime, DataFrame
from typing import cast, Literal

from modules.util.dataframe import get_str_dataframe_item
from .enums import EstoqueHeaders
from .types import (
    EstoqueBritechRendaFixa,
    EstoqueBritechRendaVariavel,
    EstoqueBritechFuturo,
    EstoqueBritechCota,
)


class BritechEstoqueService:
    def get_renda_fixa(
        self, buffer_estoque_renda_fixa: bytes
    ) -> list[EstoqueBritechRendaFixa]:
        estoque: list[EstoqueBritechRendaFixa] = []

        dataframe_estoque: DataFrame = read_excel(
            buffer_estoque_renda_fixa, engine="openpyxl"
        )
        for _, row in dataframe_estoque.iterrows():
            data_historico: date = to_datetime(
                row[EstoqueHeaders.DATA_HISTORICO.value]
            ).date()
            id_cliente: int = int(row[EstoqueHeaders.ID_CLIENTE.value])
            codigo_isin: str | None = get_str_dataframe_item(
                row[EstoqueHeaders.CODIGO_ISIN.value]
            )
            codigo_cetip: str | None = get_str_dataframe_item(
                row[EstoqueHeaders.CODIGO_CETIP.value]
            )
            id_titulo: int = int(row[EstoqueHeaders.ID_TITULO.value])
            descricao: str = str(row[EstoqueHeaders.DESCRICAO.value]).strip()
            descricao_completa: str = str(
                row[EstoqueHeaders.DESCRICAO_COMPLETA.value]
            ).strip()
            taxa: Decimal = Decimal(row[EstoqueHeaders.TAXA.value])
            data_emissao: date = to_datetime(
                row[EstoqueHeaders.DATA_EMISSAO.value]
            ).date()
            data_vencimento: date = to_datetime(
                row[EstoqueHeaders.DATA_VENCIMENTO.value]
            ).date()
            codigo_custodia: str | None = get_str_dataframe_item(
                row[EstoqueHeaders.CODIGO_CUSTODIA.value]
            )
            pu_mercado: Decimal = Decimal(row[EstoqueHeaders.PU_MERCADO.value])
            valor_curva: Decimal = Decimal(row[EstoqueHeaders.VALOR_CURVA.value])
            valor_mercado: Decimal = Decimal(row[EstoqueHeaders.VALOR_MERCADO.value])
            quantidade: Decimal = Decimal(row[EstoqueHeaders.QUANTIDADE.value])

            item: EstoqueBritechRendaFixa = EstoqueBritechRendaFixa(
                data_historico=data_historico,
                id_cliente=id_cliente,
                codigo_isin=codigo_isin,
                codigo_cetip=codigo_cetip,
                id_titulo=id_titulo,
                descricao=descricao,
                descricao_completa=descricao_completa,
                taxa=taxa,
                data_emissao=data_emissao,
                data_vencimento=data_vencimento,
                codigo_custodia=codigo_custodia,
                pu_mercado=pu_mercado,
                valor_curva=valor_curva,
                valor_mercado=valor_mercado,
                quantidade=quantidade,
            )
            estoque.append(item)

        return estoque

    def get_renda_variavel(
        self, buffer_estoque_renda_variavel: bytes
    ) -> list[EstoqueBritechRendaVariavel]:
        estoque: list[EstoqueBritechRendaVariavel] = []

        dataframe_estoque: DataFrame = read_excel(
            buffer_estoque_renda_variavel, engine="openpyxl"
        )
        for _, row in dataframe_estoque.iterrows():
            data_historico: date = to_datetime(
                row[EstoqueHeaders.DATA_HISTORICO.value]
            ).date()
            id_cliente: int = int(row[EstoqueHeaders.ID_CLIENTE.value])
            cd_ativo_bolsa: str = str(row[EstoqueHeaders.CD_ATIVO_BOLSA.value]).strip()
            tipo_mercado: Literal["IMO", "OPC", "OPV", "VIST"] = cast(
                Literal["IMO", "OPC", "OPV", "VIST"],
                str(row[EstoqueHeaders.TIPO_MERCADO.value]).strip(),
            )
            pu_mercado: Decimal = Decimal(row[EstoqueHeaders.PU_MERCADO.value])
            quantidade: Decimal = Decimal(row[EstoqueHeaders.QUANTIDADE.value])

            item: EstoqueBritechRendaVariavel = EstoqueBritechRendaVariavel(
                data_historico=data_historico,
                id_cliente=id_cliente,
                cd_ativo_bolsa=cd_ativo_bolsa,
                tipo_mercado=tipo_mercado,
                pu_mercado=pu_mercado,
                quantidade=quantidade,
            )
            estoque.append(item)

        return estoque

    def get_futuro(self, buffer_estoque_futuro: bytes) -> list[EstoqueBritechFuturo]:
        estoque: list[EstoqueBritechFuturo] = []

        dataframe_estoque: DataFrame = read_excel(
            buffer_estoque_futuro, engine="openpyxl"
        )
        for _, row in dataframe_estoque.iterrows():
            data_historico: date = to_datetime(
                row[EstoqueHeaders.DATA_HISTORICO.value]
            ).date()
            id_cliente: int = int(row[EstoqueHeaders.ID_CLIENTE.value])
            cd_ativo_bmf: str = str(row[EstoqueHeaders.CD_ATIVO_BMF.value]).strip()
            serie: str = str(row[EstoqueHeaders.SERIE.value]).strip()
            tipo_mercado: int = int(row[EstoqueHeaders.TIPO_MERCADO.value])
            data_vencimento: date = to_datetime(
                row[EstoqueHeaders.DATA_VENCIMENTO.value]
            ).date()
            pu_mercado: Decimal = Decimal(row[EstoqueHeaders.PU_MERCADO.value])
            quantidade: Decimal = Decimal(row[EstoqueHeaders.QUANTIDADE.value])

            item: EstoqueBritechFuturo = EstoqueBritechFuturo(
                data_historico=data_historico,
                id_cliente=id_cliente,
                cd_ativo_bmf=cd_ativo_bmf,
                serie=serie,
                tipo_mercado=tipo_mercado,
                data_vencimento=data_vencimento,
                pu_mercado=pu_mercado,
                quantidade=quantidade,
            )
            estoque.append(item)

        return estoque

    def get_cotas(self, buffer_estoque_cotas: bytes) -> list[EstoqueBritechCota]:
        estoque: list[EstoqueBritechCota] = []

        dataframe_estoque: DataFrame = read_excel(
            buffer_estoque_cotas, engine="openpyxl"
        )
        for _, row in dataframe_estoque.iterrows():
            data_historico: date = to_datetime(row["Column1"]).date()
            id_cliente: int = int(row["idcliente"])
            nome: str = str(row["Nome Fundo"]).strip()
            id_carteira: int = int(row["idcarteira"])
            nome_cota: str = str(row["Nome Fundo - Produto"]).strip()

            pu_mercado: Decimal = Decimal(row["Valor Cota"])
            valor_financeiro: Decimal = Decimal(row["Valor Bruto"])
            quantidade: Decimal = Decimal(valor_financeiro / pu_mercado)

            codigo_isin_nao_tratado: str = str(row["ISIN - Produto"]).strip()
            codigo_isin: str | None = (
                codigo_isin_nao_tratado
                if codigo_isin_nao_tratado != "" and codigo_isin_nao_tratado != "nan"
                else None
            )

            item: EstoqueBritechCota = EstoqueBritechCota(
                data_historico=data_historico,
                id_cliente=id_cliente,
                nome=nome,
                id_carteira=id_carteira,
                isin_cota=codigo_isin,
                nome_cota=nome_cota,
                pu_mercado=pu_mercado,
                quantidade=quantidade,
            )
            estoque.append(item)

        return estoque

    @staticmethod
    def get_codigo_ativo_renda_fixa(
        codigo_ativo: str, data_vencimento: date, tipo_ativo: str
    ) -> str:
        tipos_titulo_publico: set[str] = {"LFT", "LTN", "NTN-B", "NTN-C", "NTN-F"}

        if tipo_ativo in tipos_titulo_publico:
            return codigo_ativo + data_vencimento.strftime("%Y")

        return codigo_ativo

    @staticmethod
    def get_codigo_ntnb_compromissada() -> str:
        return "760199"

    @staticmethod
    def get_vencimento_ntnb_compromissada() -> str:
        return "2050"
