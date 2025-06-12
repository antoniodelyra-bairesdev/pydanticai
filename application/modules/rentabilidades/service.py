import pandas as pd
from dataclasses import dataclass
from typing import BinaryIO


class RentabilidadesService:
    @classmethod
    def get_dataframe(
        cls,
        arquivo_rentabilidades: BinaryIO,
        nome_sheet: str,
        skip_rows: int,
    ) -> pd.DataFrame:
        df = pd.read_excel(arquivo_rentabilidades, sheet_name=nome_sheet, header=None)

        headers = df.iloc[1].astype(str).values
        NOME_HEADER_DATA_POSICAO = "data_posicao"
        headers[0] = NOME_HEADER_DATA_POSICAO
        df = df.iloc[skip_rows:]
        df.columns = headers

        df[NOME_HEADER_DATA_POSICAO] = pd.to_numeric(
            df[NOME_HEADER_DATA_POSICAO], errors="coerce"
        )

        DATA_ORIGEM_EXCEL = "1899-12-30"
        df[NOME_HEADER_DATA_POSICAO] = pd.to_datetime(
            df[NOME_HEADER_DATA_POSICAO], unit="D", origin=DATA_ORIGEM_EXCEL
        )
        df[NOME_HEADER_DATA_POSICAO] = df[NOME_HEADER_DATA_POSICAO].dt.date

        df.set_index("data_posicao", inplace=True)
        return df
