from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DocumentUpload(BaseModel):
    """Modelo para upload de documentos"""

    filename: str = Field(..., description="Nome do arquivo enviado")
    content_type: str = Field(..., description="Tipo MIME do arquivo")
    file_size: int = Field(..., gt=0, description="Tamanho do arquivo em bytes")


class ExtractionResult(BaseModel):
    """Resultado da extração de conteúdo"""

    content: str = Field(
        ..., min_length=1, description="Conteúdo extraído do documento"
    )
    format: str = Field(..., description="Formato de saída: 'markdown' ou 'raw'")
    extractor_used: str = Field(..., description="Nome do extractor utilizado")


class ConversionMetadata(BaseModel):
    """Metadados da conversão"""

    file_size: str = Field(..., description="Tamanho do arquivo formatado")
    extraction_time: str = Field(..., description="Tempo de extração formatado")
    character_count: int = Field(..., description="Número de caracteres no conteúdo")
    extractor_used: str = Field(..., description="Nome do extractor utilizado")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Data/hora da extração"
    )
    filename: str | None = Field(None, description="Nome do arquivo")


class DocumentExtractionResponse(BaseModel):
    """Resposta padronizada da API"""

    success: bool = Field(..., description="Indica se a extração foi bem-sucedida")
    data: ExtractionResult | None = Field(None, description="Dados da extração")
    metadata: ConversionMetadata | None = Field(
        None, description="Metadados da extração"
    )
    error: str | None = Field(None, description="Mensagem de erro, se houver")


class ExtractorInfo(BaseModel):
    """Informações sobre um extractor"""

    name: str = Field(..., description="Nome do extractor")
    extensions: list[str] = Field(..., description="Extensões suportadas")


class SupportedFormatsResponse(BaseModel):
    """Lista de formatos suportados"""

    success: bool = Field(..., description="Status da operação")
    formats: dict[str, list[dict]] = Field(
        ..., description="Formatos e extractors disponíveis"
    )


class CleanupResponse(BaseModel):
    """Resposta da limpeza de arquivos"""

    success: bool = Field(..., description="Status da operação")
    message: str = Field(..., description="Mensagem descritiva")
    removed_count: int = Field(..., description="Número de arquivos removidos")


class FerramentaExtracaoEnum(str, Enum):
    docling = "docling"
    docx2txt = "docx2txt"
    llmwhisperer = "llmwhisperer"
    pypdf = "pypdf"
