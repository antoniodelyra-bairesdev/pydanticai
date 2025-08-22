"""
Output types para o módulo PydanticAI.

Este módulo contém todos os tipos de saída Pydantic utilizados para:
- Estruturação de dados FIDC
- Formatação de respostas estruturadas
"""

# Importar as classes principais de cada schema FIDC
from .fidc.bemol import RelatorioFIDCBemol
from .fidc.brz_consignados_v import RelatorioFIDCBRZConsignadosV
from .fidc.icred import RelatorioFIDCICred, RelatorioFIDCICredImage
from .fidc.sol_agora_iii import RelatorioFIDCSolAgoraIII
from .fidc.somacred import RelatorioCompletoSomacred, RelatorioCompletoSomacredImage
from .fidc.valora_alion_ii import RelatorioFIDCValoraAlion, RelatorioFIDCValoraAlionIIImage
from .fidc.valora_noto import RelatorioFIDCNotoImage, RelatorioFIDCValoraNoto
from .fidc.verde_card import RelatorioFIDCVerdeCard

__all__ = [
    "RelatorioFIDCBemol",
    "RelatorioFIDCBRZConsignadosV",
    "RelatorioFIDCICred",
    "RelatorioFIDCICredImage",
    "RelatorioFIDCSolAgoraIII",
    "RelatorioCompletoSomacred",
    "RelatorioCompletoSomacredImage",
    "RelatorioFIDCValoraAlion",
    "RelatorioFIDCValoraAlionIIImage",
    "RelatorioFIDCValoraNoto",
    "RelatorioFIDCNotoImage",
    "RelatorioFIDCVerdeCard",
]
