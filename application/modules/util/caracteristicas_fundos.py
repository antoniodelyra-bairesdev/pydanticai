from pandas import read_excel, DataFrame


class CaractersticasFundosHelper:
    @staticmethod
    def get_dataframe_from_buffer(
        buffer_arq_xls_caracteristicas_fundos: bytes,
    ) -> DataFrame:
        sheet_name: str = "Gestão Icatu"
        dataframe: DataFrame = read_excel(
            buffer_arq_xls_caracteristicas_fundos, sheet_name=sheet_name, dtype="object"
        )

        return dataframe
