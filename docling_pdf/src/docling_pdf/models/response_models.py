from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ConversionResponse(BaseModel):
    success: bool = Field(..., description="Status da conversão")
    markdown_content: str | None = Field(None, description="Conteúdo markdown convertido")
    metadata: dict[str, Any] | None = Field(None, description="Metadados da conversão")
    message: str | None = Field(None, description="Mensagem adicional")


class ErrorResponse(BaseModel):
    success: bool = False
    error: str = Field(..., description="Descrição do erro")
    error_code: str = Field(..., description="Código do erro")
    timestamp: datetime = Field(default_factory=datetime.now, description="Momento do erro (UTC)")


class StatusResponse(BaseModel):
    status: str = Field(..., description="Status da aplicação")
    version: str = Field(..., description="Versão da aplicação")
    uptime: str | None = Field(None, description="Tempo de execução")
