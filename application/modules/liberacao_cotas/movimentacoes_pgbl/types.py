from datetime import date
from dataclasses import dataclass


@dataclass
class MovimentacaoPGBLLinhaRelatorio:
    id_cotista: str
    codigo_brit: str
    data_operacao: date
    data_conversao: date
    data_liquidacao: date
    tipo_operacao: int
    quantidade_cotas: float


@dataclass
class MovimentacaoPGBLFundoCota:
    cnpj: str
    codigo_brit: str | None
    valor_cota: float
