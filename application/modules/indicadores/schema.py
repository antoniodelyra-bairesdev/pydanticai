from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel as Schema


class IndicadorSchema(Schema):
    id: int
    nome: str


# Curvas

# Curva DI


class PontoCurvaDISchema(Schema):
    dias_uteis: int
    dias_corridos: int
    data_referencia: date
    taxa: float
    interpolado: bool


class CurvaDIResponse(Schema):
    dia: date
    curva: list[PontoCurvaDISchema]
    atualizacao: datetime | None = None


class AtualizarPontoCurvaDISchema(Schema):
    dias_corridos: int
    taxa: float


# Curva NTN-B


class TaxasIndicativasSchema(Schema):
    data_vencimento: date
    taxa: float
    duration: float


class TaxasIndicativasDetailsSchema(Schema):
    data_referencia: date
    atualizacao: datetime | None = None
    dados: list[TaxasIndicativasSchema]


class AjusteDAPSchema(Schema):
    data_vencimento: date
    taxa: float
    duration: int
    utilizado: bool


class AjusteDAPDetailsSchema(Schema):
    data_referencia: date
    atualizacao: datetime | None = None
    dados: list[AjusteDAPSchema]


class PontoCurvaNTNBSchema(Schema):
    duration: int
    taxa: float


class CurvaNTNBResponse(Schema):
    data: date
    taxas_indicativas: TaxasIndicativasDetailsSchema
    ajustes_dap: AjusteDAPDetailsSchema
    curva: list[PontoCurvaNTNBSchema]


class AtualizarPontoCurvaNTNBSchema(Schema):
    data_vencimento: date
    taxa: Decimal
    duration: float


class AtualizarAjusteDAPSchema(Schema):
    data_vencimento: date
    taxa: Decimal
    duration: int


# Historicos e projeções

# CDI


class HistoricoCDISchema(Schema):
    data: date
    indice_acumulado: float
    indice: float
    taxa: Decimal
    atualizacao: datetime


class AtualizarCDIRequest(Schema):
    taxa: Decimal


# IGPM


class HistoricoIGPMSchema(Schema):
    data: date
    indice_acumulado: float
    indice_mes: float
    percentual: float
    atualizacao: datetime


class IGPMProjecaoSchema(Schema):
    data: date
    projetado: bool
    indice: float
    projecao: float
    atualizacao: datetime


class SalvarIGPMRequest(Schema):
    indice_acumulado: float
    data: date


class AtualizacaoIGPMProjecaoSchema(Schema):
    projetado: bool
    taxa: float
    data: date


# IPCA


class HistoricoIPCASchema(Schema):
    data: date
    indice_acumulado: float
    indice_mes: float
    percentual: float
    atualizacao: datetime


class IPCAProjecaoSchema(Schema):
    data: date
    projetado: bool
    indice: float
    projecao: float
    atualizacao: datetime


class SalvarIPCARequest(Schema):
    indice_acumulado: float
    data: date


class AtualizacaoIPCAProjecaoSchema(Schema):
    projetado: bool
    taxa: float
    data: date
