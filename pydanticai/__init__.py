"""
Módulo PydanticAI para integração com agentes de IA estruturados.
"""

from .entity import ClientIa, ClientModel, ModelSchema, Prompt
from .schema import ConsultaRequestSchema, ConsultaResponseSchema, ModeloDisponivelSchema

__all__ = [
    "ConsultaRequestSchema",
    "ConsultaResponseSchema",
    "ModeloDisponivelSchema",
    "ClientIa",
    "ClientModel",
    "ModelSchema",
    "Prompt",
]
