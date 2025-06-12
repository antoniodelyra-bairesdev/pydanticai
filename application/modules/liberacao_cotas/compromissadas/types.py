from typing import Literal
from dataclasses import dataclass
from datetime import date


@dataclass
class Compromissada:
    fundo_codigo_brit: str
    id_titulo: int
    data_operacao: date
    tipo_operacao: Literal["CompraRevenda"]
    quantidade: int
    pu_operacao: float
    valor: float
    taxa_operacao: float
    data_retorno: date
    taxa_retorno: float
    pu_retorno: float
    valor_retorno: float
    ipo: Literal["N"]
    local_negociacao: Literal["SELIC"]
    data_liquidacao: date
    operacao_termo: Literal["N"]
