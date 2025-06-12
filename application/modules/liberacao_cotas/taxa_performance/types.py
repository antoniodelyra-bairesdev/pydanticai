from dataclasses import dataclass


@dataclass
class PefeeDespesaBritech:
    codigo: str
    fundo_codigo: str
    descricao: str


@dataclass
class PefeeTaxaPerformance:
    id_tabela: int | None
    id_carteira: int
    valor_dia: float
    valor_acumulado: float
    data_fim_apropriacao: str
    data_pagamento: str
