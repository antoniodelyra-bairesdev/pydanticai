"""
Schemas para o módulo FIDCS.

Define os modelos de dados para requests e responses dos endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class PromptInfoSchema(BaseModel):
    """Schema para informações do prompt."""

    model_name: list[str] | None = Field(None, description="Lista de nomes dos modelos de IA")
    schema_name: str | None = Field(None, description="Nome do schema de resposta")
    is_image: bool = Field(False, description="Se deve processar imagens")
    temperatura: float | None = Field(None, description="Temperatura do modelo")
    max_tokens: int | None = Field(None, description="Máximo de tokens")
    system_prompt: str | None = Field(None, description="System prompt")
    user_prompt: str | None = Field(None, description="User prompt")


class ArquivoPromptInfoSchema(PromptInfoSchema):
    """Schema para informações de arquivo e prompt correspondente."""

    arquivo: str = Field(..., description="Nome do arquivo PDF")
    fidc_nome: str = Field(..., description="Nome do FIDC extraído do arquivo")
    ano: int = Field(..., description="Ano extraído do nome do arquivo")
    mes: int = Field(..., description="Mês extraído do nome do arquivo")
    prompt_encontrado: bool = Field(..., description="Se foi encontrado prompt correspondente")


class ProcessarRequestSchema(BaseModel):
    """Schema para request de processamento de arquivos."""

    itens: list[ArquivoPromptInfoSchema] = Field(
        ..., description="Lista de itens a serem processados"
    )


class ProcessamentoDetalheSchema(BaseModel):
    """Schema para detalhes de um processamento individual."""

    arquivo: str = Field(..., description="Nome do arquivo processado")
    sucesso: bool = Field(..., description="Se o processamento foi bem-sucedido")
    registros_inseridos: int = Field(0, description="Número de registros inseridos/atualizados")
    tempo_execucao: str | None = Field(None, description="Tempo de execução da API")
    tokens_utilizados: int | None = Field(None, description="Tokens utilizados")
    modelo_utilizado: str | None = Field(None, description="Modelo de IA utilizado")
    schema_utilizado: str | None = Field(None, description="Schema utilizado")
    erro: str | None = Field(None, description="Mensagem de erro se houver falha")


class ProcessarResponseSchema(BaseModel):
    """Schema para response do processamento de arquivos."""

    total_processados: int = Field(..., description="Total de arquivos processados")
    sucessos: int = Field(..., description="Número de sucessos")
    falhas: int = Field(..., description="Número de falhas")
    erros_gerais: list[str] = Field(default_factory=list, description="Lista de erros gerais")
    detalhes: list[ProcessamentoDetalheSchema] = Field(
        default_factory=list, description="Detalhes de cada processamento"
    )


class DadosConsolidadosSchema(BaseModel):
    """Schema para dados consolidados da consulta SQL."""

    apelido: str = Field(..., description="Apelido do ativo")
    indicador_fidc_nm: str = Field(..., description="Nome do indicador FIDC")
    valor: float | None = Field(None, description="Valor do indicador")
    limite: str | None = Field(None, description="Limite do indicador")
    limite_superior: bool | None = Field(None, description="Se é limite superior")
    extra_data: dict | None = Field(None, description="Dados extras em JSON")
    mes: str = Field(..., description="Mês de referência")
    ano: int = Field(..., description="Ano de referência")
    data_captura: datetime = Field(..., description="Data de captura dos dados")


class DadosCadastraisResponseSchema(BaseModel):
    """Schema para dados cadastrais da consulta SQL."""

    apelido: str = Field(..., description="Apelido do ativo")
    indicador_fidc_nm: str = Field(..., description="Nome do indicador FIDC")
    valor: str = Field(..., description="Valor do indicador como string")


class ArquivoInfoSchema(BaseModel):
    """Schema básico para informações de arquivo."""

    nome_arquivo: str = Field(..., description="Nome do arquivo")
    caminho_completo: str = Field(..., description="Caminho completo do arquivo")
    tamanho: int = Field(..., description="Tamanho do arquivo em bytes")
    data_modificacao: datetime = Field(..., description="Data de última modificação")
