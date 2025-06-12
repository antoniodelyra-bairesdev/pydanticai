from fastapi import UploadFile
from pydantic import BaseModel as Schema, validator


class PostAluguelAcoes(Schema):
    xls_caracteristicas_fundos: UploadFile
    csv_relatorio_bip: UploadFile
    xlsx_relatorio_antecipacao: UploadFile

    @validator("xls_caracteristicas_fundos")
    def validate_xls(cls, file: UploadFile):
        if file.content_type != "application/vnd.ms-excel":
            raise ValueError(
                "Input característica de fundos inválida. O arquivo deve ser um .xls."
            )

        return file

    @validator("csv_relatorio_bip")
    def validate_csv(cls, file: UploadFile):
        if file.content_type != "text/csv":
            raise ValueError(
                "Input relatório BIP inválido. O arquivo deve ser um .csv."
            )

        return file

    @validator("xlsx_relatorio_antecipacao")
    def validate_xlsx(cls, file: UploadFile):
        if (
            file.content_type
            != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            raise ValueError(
                "Input relatório antecipação inválido. O arquivo deve ser um .xlsx."
            )

        return file
