from datetime import date
from decimal import Decimal
from pydantic import BaseModel as Schema

from modules.util.api_warning import APIWarning


class ComparacaoPLSchema(Schema):
    fundo_codigo_britech: str
    fundo_codigo_administrador: str
    fundo_cnpj: str
    fundo_nome: str
    data_referente: date
    pl_xml: Decimal
    pl_calculado: Decimal
    diferenca_pl: Decimal


class ResponseSchema(Schema):
    batimento_pls: list[ComparacaoPLSchema]
    warnings: list[APIWarning] | None
