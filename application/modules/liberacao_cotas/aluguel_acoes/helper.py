from datetime import date, datetime
from io import BytesIO
from math import nan
from pandas import DataFrame, read_csv, read_excel

from modules.util.string import get_numero_decimal_tratado_from_numero_string
from modules.util.temp_file import TempFileHelper
from .types import (
    AluguelLinhaRelatorioBIP,
    AluguelLado,
    AluguelTipoContrato,
    AluguelLinhaRelatorioAntecipacao,
)


class AluguelAcoesHelper:
    @staticmethod
    def get_linhas_relatorio_bip(
        nome_arq_csv_relatorio_bip: str,
    ) -> list[AluguelLinhaRelatorioBIP]:
        buffer_arq_csv_relatorio_bip: bytes = TempFileHelper.get_conteudo_e_deleta(
            nome_arq_csv_relatorio_bip
        )
        dataframe_relatorio_bip: DataFrame = (
            AluguelAcoesHelper.__get_dataframe_relatorio_bip(
                buffer_arq_csv_relatorio_bip
            )
        )

        linhas_relatorio_bip: list[AluguelLinhaRelatorioBIP] = []

        for _, row in dataframe_relatorio_bip.iterrows():
            fundo_codigo_administrador: str = str(row.Conta_no_Administrador_Conta)
            if fundo_codigo_administrador == "" or fundo_codigo_administrador == "nan":
                continue

            numero_contrato: str = str(row.Numero)
            papel: str = str(row.Papel)
            nome_fundo: str = str(row.Nome_Conta)
            lado_aluguel: AluguelLado = AluguelLado(row.Lado)
            quantidade: int = int(row.Quantidade)
            taxa_cliente: float = get_numero_decimal_tratado_from_numero_string(
                row.Taxa_Cliente
            )
            taxa_derivada: float = get_numero_decimal_tratado_from_numero_string(
                row.Taxa_Derivada
            )
            data_vencimento: date = datetime.strptime(
                str(row.Vencimento), "%d/%m/%Y"
            ).date()
            data_carencia: date = datetime.strptime(
                str(row.Carencia), "%d/%m/%Y"
            ).date()
            tipo_contrato: AluguelTipoContrato = row.Tipo_Contrato

            linha: AluguelLinhaRelatorioBIP = AluguelLinhaRelatorioBIP(
                numero_contrato=numero_contrato,
                papel=papel,
                codigo_administrador=fundo_codigo_administrador,
                nome_fundo=nome_fundo,
                lado_aluguel=lado_aluguel,
                quantidade=quantidade,
                taxa_cliente=taxa_cliente,
                taxa_derivada=taxa_derivada,
                data_vencimento=data_vencimento,
                data_carencia=data_carencia,
                tipo_contrato=tipo_contrato,
            )

            linhas_relatorio_bip.append(linha)

        return linhas_relatorio_bip

    @staticmethod
    def get_linhas_relatorio_antecipacoes(
        nome_arq_xlsx_relatorio_antecipacoes: str,
    ) -> list[AluguelLinhaRelatorioAntecipacao]:
        buffer_arq_xlsx_relatorio_antecipacoes: bytes = (
            TempFileHelper.get_conteudo_e_deleta(nome_arq_xlsx_relatorio_antecipacoes)
        )
        dataframe_relatorio_antecipacoes: DataFrame = (
            AluguelAcoesHelper.__get_dataframe_relatorio_antecipacoes(
                buffer_arq_xlsx_relatorio_antecipacoes
            )
        )

        linhas_relatorio_atencipacao: list[AluguelLinhaRelatorioAntecipacao] = []

        for _, row in dataframe_relatorio_antecipacoes.iterrows():
            lado: str = str(row.Lado)
            numero_contrato: str = str(row.Contrato)
            numero_conta: str = str(row.Numero_Conta)
            nome_fundo: str = str(row.Nome)
            papel: str = str(row.Papel)
            quantidade_liquidacao: int = int(row.Quantidade_Liquidacao)
            quantidade_renovada: int = int(row.Quantidade_Renovada)
            quantidade_vencida: int = int(row.Quantidade_Vencida)
            data_liquidacao: date = datetime.strptime(
                str(row.Liquidacao), "%Y-%m-%d %H:%M:%S"
            ).date()
            data_vencimento: date = datetime.strptime(
                str(row.Vencimento), "%Y-%m-%d %H:%M:%S"
            ).date()
            id_execucao_participante: str = str(row.Execucao_Participante)
            id_corretora: str = str(row.Corretora)

            linha: AluguelLinhaRelatorioAntecipacao = AluguelLinhaRelatorioAntecipacao(
                lado=lado,
                numero_contrato=numero_contrato,
                numero_conta=numero_conta,
                nome_fundo=nome_fundo,
                papel=papel,
                quantidade_liquidacao=quantidade_liquidacao,
                quantidade_renovada=quantidade_renovada,
                quantidade_vencida=quantidade_vencida,
                data_liquidacao=data_liquidacao,
                data_vencimento=data_vencimento,
                id_execucao_participante=id_execucao_participante,
                id_corretora=id_corretora,
            )

            linhas_relatorio_atencipacao.append(linha)

        return linhas_relatorio_atencipacao

    @staticmethod
    def __get_dataframe_relatorio_bip(
        buffer_arq_csv_relatorio_bip: bytes,
    ) -> DataFrame:
        dataframe: DataFrame = read_csv(
            BytesIO(buffer_arq_csv_relatorio_bip), sep=";", skiprows=1, dtype=object
        )

        dataframe.columns = (
            dataframe.columns.str.replace(" ", "_")
            .str.replace("(", "")
            .str.replace(")", "")
            .str.replace("Apelido/", "")
        )

        return dataframe

    @staticmethod
    def __get_dataframe_relatorio_antecipacoes(
        buffer_arq_xlsx_relatorio_antecipacoes: bytes,
    ) -> DataFrame:
        dataframe: DataFrame = read_excel(
            BytesIO(buffer_arq_xlsx_relatorio_antecipacoes), engine="openpyxl"
        )

        dataframe = dataframe.rename(
            columns={
                "Número Conta": "Numero Conta",
                "Quantidade Liquidação": "Quantidade Liquidacao",
                "Liquidação": "Liquidacao",
                "Execução Participante": "Execucao Participante",
            }
        )

        dataframe.columns = dataframe.columns.str.replace(" ", "_").str.replace(
            "Apelido/", ""
        )
        dataframe = dataframe.replace(nan, 0)

        return dataframe
