
"""
Schemas para o módulo PydanticAI.

Este módulo contém todos os schemas Pydantic utilizados para:
- Validação de entrada da API
- Formatação de respostas
- Estruturação de dados FIDC
"""

from .api import (
    ConsultaRequestSchema,
    ConsultaResponseSchema,
    ModeloDisponivelSchema,
)

__all__ = [
    "ConsultaRequestSchema",
    "ConsultaResponseSchema", 
    "ModeloDisponivelSchema",
]
