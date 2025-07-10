"""
Schemas de API para o módulo PydanticAI.

Este módulo contém os schemas Pydantic utilizados para validação e serialização
de requisições e respostas da API do módulo PydanticAI.

Schemas incluídos:
- ConsultaRequestSchema: Para requisições de consulta de IA
- ConsultaResponseSchema: Para respostas de consulta de IA
- ModeloDisponivelSchema: Para representação de modelos disponíveis
- SchemaDisponivelSchema: Para listagem de schemas disponíveis
"""

from typing import Optional, Any

from pydantic import BaseModel as Schema, Field, field_validator


class ConsultaRequestSchema(Schema):
    """Schema para requisições de consulta de IA."""

    user_prompt: str = Field(..., description="Pergunta ou instrução para o agente de IA")
    model: str = Field(
        default="groq:llama-3.3-70b-versatile", description="Modelo de IA a ser utilizado"
    )
    system_prompt: str = Field(
        default="Seja preciso e direto nas respostas.",
        description="Prompt do sistema para configurar o comportamento do agente",
    )
    retries: int = Field(
        default=2, ge=1, le=5, description="Número de tentativas em caso de falha"
    )
    max_tokens: int = Field(
        default=1440, ge=1, le=8000, description="Número máximo de tokens na resposta"
    )
    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description=(
            "Temperatura para controle de criatividade "
            "(0=determinístico, 2=muito criativo)"
        ),
    )
    schema_name: str = Field(
        default="default", description="Nome do schema Pydantic para estruturar a resposta"
    )
    doc: Optional[str] = Field(default="", description="Documento a ser analisado (opcional)")

    @field_validator("user_prompt")
    @classmethod
    def validate_prompts_not_empty(cls, v: str) -> str:
        """Valida que o prompt não seja vazio."""
        if not v.strip():
            raise ValueError("prompt não pode ser vazio")
        return v.strip()

    @field_validator("schema_name")
    @classmethod
    def validate_schema_name(cls, v: str) -> str:
        """Valida que o schema name seja válido."""
        from modules.pydanticai.enum import ModelSchemaEnum

        try:
            ModelSchemaEnum.get_schema_class(v)
        except ValueError:
            available = ModelSchemaEnum.get_available_schemas()
            raise ValueError(f"Schema '{v}' não encontrado. Disponíveis: {available}")
        return v


class ConsultaResponseSchema(Schema):
    """Schema para respostas de consulta do PydanticAI."""

    resultado: Any = Field(..., description="Resultado estruturado da consulta")
    tempo_execucao: float = Field(..., description="Tempo de execução em segundos")
    tokens_utilizados: Optional[int] = Field(
        default=None, description="Número de tokens utilizados na consulta"
    )
    modelo_utilizado: str = Field(..., description="Modelo de IA que foi utilizado")
    schema_utilizado: str = Field(..., description="Schema de resposta utilizado")


class ModeloDisponivelSchema(Schema):
    """Schema para representação de modelos disponíveis."""

    client_model_id: int
    model_name: str
    client_name: str
    client_abrev: str
    description: Optional[str]
    cost: Optional[str]
    order: int
