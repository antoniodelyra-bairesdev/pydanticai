from datetime import date
from decimal import Decimal
from pydantic import BaseModel as Schema

from .types import FundoInfo
from modules.util.api_warning import APIWarning


class AtivoPrecoFundo(Schema):
    codigo: str
    isin: str
    preco_unitario_posicao: Decimal
    data_referente: date
    fundo_info: FundoInfo


class ResponseSchema(Schema):
    ativos: list[AtivoPrecoFundo]
    warnings: list[APIWarning]
