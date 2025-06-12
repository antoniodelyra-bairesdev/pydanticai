from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal


@dataclass
class EstoqueBritechRendaFixa:
    data_historico: date
    id_cliente: int
    codigo_isin: str | None
    codigo_cetip: str | None
    id_titulo: int
    descricao: str
    descricao_completa: str
    taxa: Decimal
    data_emissao: date
    data_vencimento: date
    codigo_custodia: str | None
    pu_mercado: Decimal
    valor_curva: Decimal
    valor_mercado: Decimal
    quantidade: Decimal


@dataclass
class EstoqueBritechRendaVariavel:
    data_historico: date
    id_cliente: int
    cd_ativo_bolsa: str
    tipo_mercado: Literal["IMO", "OPC", "OPV", "VIST"]
    pu_mercado: Decimal
    quantidade: Decimal


@dataclass
class EstoqueBritechFuturo:
    data_historico: date
    id_cliente: int
    cd_ativo_bmf: str
    serie: str
    tipo_mercado: int
    data_vencimento: date
    pu_mercado: Decimal
    quantidade: Decimal


@dataclass
class EstoqueBritechCota:
    data_historico: date
    id_cliente: int
    nome: str
    id_carteira: int
    isin_cota: str | None
    nome_cota: str
    pu_mercado: Decimal
    quantidade: Decimal
