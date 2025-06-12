from datetime import date
from dataclasses import dataclass
from enum import Enum


class AluguelLado(Enum):
    DOADOR = "D"
    TOMADOR = "T"


class AluguelTipoContrato(Enum):
    DIRETO = "Direto"
    RENOVACAO = "Renovacao"


@dataclass
class AluguelLinhaRelatorioBIP:
    numero_contrato: str
    papel: str
    codigo_administrador: str
    nome_fundo: str
    lado_aluguel: AluguelLado
    quantidade: int
    taxa_cliente: float
    taxa_derivada: float
    data_vencimento: date
    data_carencia: date
    tipo_contrato: AluguelTipoContrato


@dataclass
class AluguelLinhaRelatorioAntecipacao:
    lado: str
    numero_contrato: str
    numero_conta: str
    nome_fundo: str
    papel: str
    quantidade_liquidacao: int
    quantidade_renovada: int
    quantidade_vencida: int
    data_liquidacao: date
    data_vencimento: date
    id_execucao_participante: str
    id_corretora: str
