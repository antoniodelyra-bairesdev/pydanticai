"""
Schemas de API para o módulo PydanticAI.

Este módulo contém os schemas Pydantic utilizados para validação e serialização
de requisições e respostas da API do módulo PydanticAI.

Schemas incluídos:
- ConsultaRequestSchema: Para requisições de consulta de IA (com suporte a fallback)
- ConsultaComArquivoRequestSchema: Para requisições de consulta com arquivo
- ConsultaResponseSchema: Para respostas de consulta de IA
- ModeloDisponivelSchema: Para representação de modelos disponíveis
- PromptCadastroSchema: Para cadastro de prompts
- PromptResponseSchema: Para resposta de prompts cadastrados
"""

from datetime import datetime
from typing import Annotated, Any, Literal

from fastapi import UploadFile
from modules.integrations.enums import FerramentaExtracaoEnum, TipoExtracaoEnum
from pydantic import BaseModel as Schema, Field, field_validator

from .enum_modules import ModelSchemaEnum


def validate_schema_name(v: str) -> str:
    """Valida que o schema name seja válido."""
    try:
        ModelSchemaEnum.get_schema_class(v)
    except ValueError:
        available = ModelSchemaEnum.get_available_schemas()
        raise ValueError(f"Schema '{v}' não encontrado. Disponíveis: {available}")
    return v


def validate_not_empty(v: str, field_name: str) -> str:
    """Valida que o campo não seja vazio."""
    if not v.strip():
        raise ValueError(f"{field_name} não pode ser vazio")
    return v.strip()


class ConsultaRequestSchema(Schema):
    """
    Schema para requisições de consulta de IA com suporte a fallback.

    O campo 'model' aceita:
    - String única: "groq:llama-3.3-70b-versatile"
    - Lista de strings para fallback: ["groq:llama", "openai:gpt-4o", "anthropic:claude-3"]
    """

    user_prompt: str = Field(..., description="Pergunta ou instrução para o agente de IA")
    model: str | list[str] = Field(
        default="groq:llama-3.3-70b-versatile",
        description=(
            "Modelo(s) de IA. Aceita string única ou lista de strings para fallback sequencial"
        ),
    )
    system_prompt: str = Field(
        default="Seja preciso e direto nas respostas.",
        description="Prompt do sistema para configurar o comportamento do agente",
    )
    retries: int = Field(
        default=2, ge=1, le=5, description="Número de tentativas em caso de falha"
    )
    max_tokens: int = Field(
        default=2400, ge=1, le=8000, description="Número máximo de tokens na resposta"
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
    def validate_user_prompt(cls, v: str) -> str:
        return validate_not_empty(v, "user_prompt")

    @field_validator("schema_name")
    @classmethod
    def validate_schema_name(cls, v: str) -> str:
        return validate_schema_name(v)

    @field_validator("model")
    @classmethod
    def validate_model_config(cls, v: str | list[str]):
        """
        Valida a configuração do modelo.

        Aceita:
        - String no formato "provider:model"
        - Lista de strings no mesmo formato
        """

        def validate_model_string(model_str: str) -> str:
            """Valida formato de string de modelo."""
            if not isinstance(model_str, str):
                raise ValueError(f"Modelo deve ser string, recebido: {type(model_str)}")

            model_str = model_str.strip()
            if not model_str:
                raise ValueError("String de modelo não pode estar vazia")

            if ":" not in model_str:
                raise ValueError(
                    f"Formato inválido: '{model_str}'. "
                    f"Use 'provider:model' (ex: 'openai:gpt-4o', 'groq:llama-3.3-70b')"
                )

            provider, model_name = model_str.split(":", 1)
            if not provider or not model_name:
                raise ValueError(
                    f"Provider e nome do modelo devem ser especificados: '{model_str}'"
                )

            return model_str

        # Validar baseado no tipo
        if isinstance(v, str):
            return validate_model_string(v)

        elif isinstance(v, list):
            if len(v) == 0:
                raise ValueError("Lista de modelos não pode estar vazia")

            validated = []
            for i, item in enumerate(v):
                try:
                    validated.append(validate_model_string(item))
                except ValueError as e:
                    raise ValueError(f"Erro no modelo {i}: {e}")

            # Verificar se não há duplicados
            if len(validated) != len(set(validated)):
                raise ValueError("Lista de modelos contém duplicados")

            return validated

        else:
            raise ValueError(f"'model' deve ser string ou lista de strings, recebido: {type(v)}")


class ConsultaComArquivoRequestSchema(Schema):
    """Schema para requisições de consulta de IA com arquivo e suporte a fallback."""

    user_prompt: str = Field(..., description="Pergunta ou instrução para o agente de IA")
    arquivo: UploadFile = Field(..., description="Arquivo a ser processado")
    ferramenta_extracao: FerramentaExtracaoEnum | None = Field(
        default=None, description="Ferramenta para extração do conteúdo (opcional)"
    )
    tipo_extracao: TipoExtracaoEnum = Field(
        ..., description="Tipo de extração desejado (markdown, dados-brutos, imagens)"
    )
    model: str | list[str] = Field(
        default="groq:llama-3.3-70b-versatile",
        description=(
            "Modelo(s) de IA. Aceita string única ou lista de strings para fallback sequencial"
        ),
    )
    system_prompt: str = Field(
        default="Seja preciso e direto nas respostas.",
        description="Prompt do sistema para configurar o comportamento do agente",
    )
    retries: int = Field(
        default=2, ge=1, le=5, description="Número de tentativas em caso de falha"
    )
    max_tokens: int = Field(
        default=2400, ge=1, le=8000, description="Número máximo de tokens na resposta"
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
    def validate_user_prompt(cls, v: str) -> str:
        return validate_not_empty(v, "user_prompt")

    @field_validator("schema_name")
    @classmethod
    def validate_schema_name(cls, v: str) -> str:
        return validate_schema_name(v)

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

    @field_validator("model")
    @classmethod
    def validate_model_config(cls, v: str | list[str]):
        """
        Valida a configuração do modelo (reutiliza lógica do ConsultaRequestSchema).
        """
        # Reutilizar a validação do ConsultaRequestSchema
        return ConsultaRequestSchema.validate_model_config(v)


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


class PromptCadastroSchema(Schema):
    """Schema para cadastro de novos prompts."""

    client_name: str = Field(
        default="Open AI",
        description="Nome do cliente de IA (ex: 'OpenAI', 'Anthropic')",
    )
    model_name: str = Field(..., description="Nome do modelo (ex: 'gpt-4.1-mini')")
    mesa_nome: str = Field(
        default="Crédito Privado", description="Nome da mesa para classificação"
    )
    codigo_ativo: str = Field(..., description="Código do ativo financeiro")
    model_schema_name: str = Field(
        default="default", description="Nome do schema para estruturação da resposta"
    )
    temperatura: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Temperatura para controle de criatividade do modelo",
    )
    max_tokens: int = Field(
        default=2400, ge=1, le=8000, description="Número máximo de tokens na resposta"
    )
    prompt_sistema: str = Field(
        default="Seja preciso e direto nas respostas",
        description="Instruções do sistema para o modelo",
    )
    prompt_usuario: str = Field(..., description="Prompt principal a ser enviado ao modelo")
    is_image: bool = Field(
        default=False, description="Indica se o prompt é destinado ao processamento de imagens"
    )
    descricao: str | None = Field(default=None, description="Descrição opcional do prompt")

    @field_validator("prompt_usuario")
    @classmethod
    def validate_prompt_usuario(cls, v: str) -> str:
        return validate_not_empty(v, "prompt_usuario")

    @field_validator("model_schema_name")
    @classmethod
    def validate_model_schema_name(cls, v: str) -> str:
        return validate_schema_name(v)

    @field_validator("codigo_ativo")
    @classmethod
    def validate_codigo_ativo(cls, v: str) -> str:
        """Valida e normaliza o código do ativo."""
        v = validate_not_empty(v, "codigo_ativo")
        # Normalizar para maiúsculas e remover espaços extras
        return v.strip().upper()


class PromptResponseSchema(Schema):
    """Schema para resposta de prompts cadastrados."""

    prompt_id: int = Field(..., description="ID único do prompt cadastrado")
    client_name: str = Field(..., description="Nome do cliente de IA utilizado")
    model_name: str = Field(..., description="Nome do modelo utilizado")
    mesa_nome: str = Field(..., description="Nome da mesa associada")
    codigo_ativo: str = Field(..., description="Código do ativo")
    schema_name: str = Field(..., description="Nome do schema utilizado")
    temperatura: float = Field(..., description="Temperatura configurada")
    max_tokens: int = Field(..., description="Máximo de tokens configurado")
    prompt_sistema: str = Field(..., description="Prompt do sistema")
    prompt_usuario: str = Field(..., description="Prompt do usuário")
    is_image: bool = Field(..., description="Indica se é para processamento de imagens")
    data_criacao: datetime = Field(..., description="Data e hora da criação")
    ativo: bool = Field(..., description="Status de ativação do prompt")
    descricao: str | None = Field(..., description="Descrição do prompt")


class PromptStatusUpdateSchema(Schema):
    """
    Schema para atualização do status de um prompt.

    Permite ativar ou desativar um prompt existente através do campo 'ativo'.
    """

    status: Annotated[
        Literal["enabled", "disabled"],
        Field(
            ..., description="Status do prompt: 'enabled' para ativar ou 'disabled' para desativar"
        ),
    ]


class PromptStatusResponseSchema(Schema):
    """
    Schema para resposta da atualização de status do prompt.

    Retorna informações sobre a operação realizada, incluindo o novo status
    e timestamp da atualização.
    """

    prompt_id: int = Field(..., description="ID do prompt atualizado")
    status: str = Field(..., description="Novo status do prompt (enabled/disabled)")
    message: str = Field(..., description="Mensagem de confirmação da operação")
    updated_at: datetime = Field(..., description="Data e hora da atualização")
    previous_status: str = Field(..., description="Status anterior do prompt")
