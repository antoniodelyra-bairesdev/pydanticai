"""
Módulo FIDCS - Processamento automatizado de relatórios FIDC.

Este módulo fornece funcionalidades para:
- Listagem de arquivos PDF FIDC
- Processamento automatizado via PydanticAI
- Extração e armazenamento de dados estruturados
- Consulta de dados consolidados
"""

from .entity import FIDCDadosCadastrais, IndicadorFIDC, IndicadorFIDCValor
from .repository import FidcsRepository
from .router import router
from .schema import (
    ArquivoPromptInfoSchema,
    DadosConsolidadosSchema,
    ProcessamentoDetalheSchema,
    ProcessarRequestSchema,
    ProcessarResponseSchema,
)
from .service import FidcsService

__all__ = [
    "FidcsService",
    "FidcsRepository",
    "router",
    "IndicadorFIDC",
    "IndicadorFIDCValor",
    "FIDCDadosCadastrais",
    "ArquivoPromptInfoSchema",
    "ProcessarRequestSchema",
    "ProcessarResponseSchema",
    "ProcessamentoDetalheSchema",
    "DadosConsolidadosSchema",
]
