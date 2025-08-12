"""
Schemas de API para o módulo PydanticAI.

Este módulo contém os schemas Pydantic utilizados para validação e serialização
de requisições e respostas da API do módulo PydanticAI.

Schemas incluídos:
- ConsultaRequestSchema: Para requisições de consulta de IA
- ConsultaComArquivoRequestSchema: Para requisições de consulta com arquivo
- ConsultaResponseSchema: Para respostas de consulta de IA
- ModeloDisponivelSchema: Para representação de modelos disponíveis
"""

from typing import Any

from fastapi import UploadFile
from modules.integrations.enums import FerramentaExtracaoEnum, TipoExtracaoEnum
from modules.pydanticai.enum_modules import ModelSchemaEnum
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
            "Temperatura para controle de criatividade (0=determinístico, 2=muito criativo)"
        ),
    )
    schema_name: str = Field(
        default="default", description="Nome do schema Pydantic para estruturar a resposta"
    )
    doc: str | None = Field(default="", description="Documento a ser analisado (opcional)")

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
        try:
            ModelSchemaEnum.get_schema_class(v)
        except ValueError:
            available = ModelSchemaEnum.get_available_schemas()
            raise ValueError(f"Schema '{v}' não encontrado. Disponíveis: {available}")
        return v


class ConsultaComArquivoRequestSchema(Schema):
    """Schema para requisições de consulta de IA com arquivo."""

    user_prompt: str = Field(..., description="Pergunta ou instrução para o agente de IA")
    arquivo: UploadFile = Field(..., description="Arquivo a ser processado")
    ferramenta_extracao: FerramentaExtracaoEnum | None = Field(
        default=None, description="Ferramenta para extração do conteúdo (opcional)"
    )
    tipo_extracao: TipoExtracaoEnum = Field(
        ..., description="Tipo de extração desejado (markdown, dados-brutos, imagens)"
    )
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
            "Temperatura para controle de criatividade (0=determinístico, 2=muito criativo)"
        ),
    )
    schema_name: str = Field(
        default="default", description="Nome do schema Pydantic para estruturar a resposta"
    )

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
        try:
            ModelSchemaEnum.get_schema_class(v)
        except ValueError:
            available = ModelSchemaEnum.get_available_schemas()
            raise ValueError(f"Schema '{v}' não encontrado. Disponíveis: {available}")
        return v

    @field_validator("arquivo")
    @classmethod
    def validate_arquivo(cls, v: UploadFile) -> UploadFile:
        """Valida que o arquivo seja válido."""
        if v.filename is None or v.filename == "":
            raise ValueError("Nome do arquivo não pode ser vazio")

        # Validar tipos de arquivo suportados
        valid_content_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
            "text/plain",
        ]

        if v.content_type not in valid_content_types:
            raise ValueError(
                f"Tipo de arquivo '{v.content_type}' não suportado. "
                f"Tipos válidos: {valid_content_types}"
            )

        return v


class ConsultaResponseSchema(Schema):
    """Schema para respostas de consulta do PydanticAI."""

    resultado: Any = Field(..., description="Resultado estruturado da consulta")
    tempo_execucao: str = Field(..., description="Tempo de execução")
    tokens_utilizados: int | None = Field(
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
    description: str | None
    cost: str | None
    order: int
