"""
Processors para diferentes tipos de FIDC.

Cada processor implementa a lógica específica de parseamento
e inserção de dados para um tipo particular de FIDC.
"""

from .base import BaseFIDCProcessor
from .bemol import BemolProcessor
from .brz_consignados_v import BrzProcessor
from .icred import IcredProcessor
from .sol_agora_iii import SolAgoraProcessor
from .somacred import SomacredProcessor
from .valora_alion_ii import AlionProcessor
from .valora_noto import NotoProcessor
from .verde_card import VerdeCardProcessor

__all__ = [
    "BaseFIDCProcessor",
    "BemolProcessor",
    "IcredProcessor",
    "SomacredProcessor",
    "NotoProcessor",
    "SolAgoraProcessor",
    "BrzProcessor",
    "AlionProcessor",
    "VerdeCardProcessor",
]
