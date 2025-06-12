from io import BytesIO
from fastapi import UploadFile
from pandas import DataFrame, ExcelWriter, read_csv, notnull
from enum import Enum
from json import dumps


class Operacao(Enum):
    APLICACAO = "A"
    RESGATE = "R"


class PassivoService:
    async def get_omnis_arquivo_passivo(
        self, arquivo: UploadFile
    ) -> tuple[BytesIO, str]:
        dataframe: DataFrame = read_csv(
            arquivo.file, sep=";", dtype={"CD_FUNDO": "string"}
        )
        dataframe = dataframe.where(notnull(dataframe), None)

        fundos_sem_valor_bruto: list[str] = []
        linhas_dataframe_movimentacoes_passivo: list[dict] = []
        for _, row in dataframe.iterrows():
            fundo_codigo_administrador: str = str(row.CD_FUNDO).strip()
            fundo_codigo_administrador_tratado: str = (
                fundo_codigo_administrador[1:]
                if fundo_codigo_administrador.startswith("0")
                else fundo_codigo_administrador
            )

            if (
                row.VL_BRUTO == None
                or row.VL_BRUTO == ""
                or row.VL_BRUTO == 0
                or row.VL_BRUTO == "0"
            ):
                if fundo_codigo_administrador not in fundos_sem_valor_bruto:
                    fundos_sem_valor_bruto.append(fundo_codigo_administrador)
                continue

            valor_bruto: float = float(row.VL_BRUTO.replace(",", "."))
            operacao: str = self.__get_operacao_tratada(str(row.CD_TIPO).strip())
            data_movimentacao: str = str(row.DT_MOVIMENTO).strip()

            linha_dataframe_movimentacoes_passivo: dict = {
                "Portfólio": fundo_codigo_administrador_tratado,
                "Data de solicitação": data_movimentacao,
                "Data de conversão": "",
                "Data de Liquidação": "",
                "Valor": valor_bruto,
                "Tipo de Mvto": operacao,
                "Afeta Qtd Cotas": "S",
            }
            linhas_dataframe_movimentacoes_passivo.append(
                linha_dataframe_movimentacoes_passivo
            )

        dataframe_omnis_movimentacoes_passivo: DataFrame = DataFrame(
            linhas_dataframe_movimentacoes_passivo
        )
        buffer_excel_omnis_movimentacoes_passivo: BytesIO = BytesIO()
        SHEET_NAME: str = "Plan1"

        with ExcelWriter(
            buffer_excel_omnis_movimentacoes_passivo, engine="openpyxl"
        ) as writer:
            dataframe_omnis_movimentacoes_passivo.to_excel(
                writer, index=False, sheet_name=SHEET_NAME
            )
        buffer_excel_omnis_movimentacoes_passivo.seek(0)
        avisos_json: str = (
            dumps(
                {
                    "codigos_fundos_fora_da_data_ou_em_reprocessamento": fundos_sem_valor_bruto
                }
            )
            if len(fundos_sem_valor_bruto) > 0
            else dumps({})
        )

        return (
            buffer_excel_omnis_movimentacoes_passivo,
            avisos_json,
        )

    def __get_operacao_tratada(self, operacao: str) -> str:
        if operacao.startswith(Operacao.APLICACAO.value):
            return Operacao.APLICACAO.value

        if operacao.startswith(Operacao.RESGATE.value):
            return Operacao.RESGATE.value

        return operacao
