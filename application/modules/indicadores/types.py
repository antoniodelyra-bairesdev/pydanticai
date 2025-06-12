from dataclasses import dataclass
from datetime import date, datetime

from .model import TaxasDAP, TaxaNTNB as CurvaNTNBModel
from scipy.interpolate import CubicSpline


@dataclass
class CurvaDI:
    dominio: set[int]
    funcao: CubicSpline
    data: date
    atualizacao: datetime | None = None


@dataclass
class CurvaNTNB:
    taxas_indicativas: list[CurvaNTNBModel]
    ajustes_dap: list[TaxasDAP]
    data_dap: date
    data_ntnb: date
    atualizacao_dap: datetime | None = None
    atualizacao_ntnb: datetime | None = None
