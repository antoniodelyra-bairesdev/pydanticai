from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ExtractionResult(BaseModel):
    original_md: str = Field(..., description="Conteúdo markdown extraído do PDF")

    @field_validator("original_md")
    @classmethod
    def validate_markdown(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Conteúdo markdown não pode estar vazio")
        return v


class ConversionMetadata(BaseModel):
    file_size: str = Field(..., description="Tamanho do arquivo formatado")
    conversion_time: str = Field(..., description="Tempo de conversão formatado")
    character_count: int = Field(..., description="Número de caracteres no markdown")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Data/hora da conversão"
    )


class PDFUpload(BaseModel):
    filename: str = Field(..., description="Nome do arquivo enviado")
    content_type: str = Field(..., description="Tipo MIME do arquivo")
    file_size: int = Field(..., description="Tamanho do arquivo em bytes")

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        if v != "application/pdf":
            raise ValueError("Apenas arquivos PDF são permitidos")
        return v

    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Tamanho do arquivo deve ser maior que zero")
        return v


class ConversionResponse(BaseModel):
    success: bool = Field(..., description="Indica se a conversão foi bem-sucedida")
    data: ExtractionResult | None = Field(None, description="Dados da conversão")
    metadata: ConversionMetadata | None = Field(None, description="Metadados da conversão")
    error: str | None = Field(None, description="Mensagem de erro, se houver")


class PDFInfo(BaseModel):
    filename: str = Field(..., description="Nome do arquivo")
    file_size: int = Field(..., description="Tamanho em bytes")
    file_path: str = Field(..., description="Caminho completo do arquivo")
    created_at: float = Field(..., description="Timestamp de criação")
    modified_at: float = Field(..., description="Timestamp de modificação")
