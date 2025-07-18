import time
from pathlib import Path
from typing import Any

from docling.document_converter import DocumentConverter
from loguru import logger
from pydantic import ValidationError

from ..exceptions.custom_exceptions import FileNotFoundException, PDFConversionException
from ..models.pdf_models import ConversionMetadata, ExtractionResult, PDFInfo


class PDFService:
    def __init__(self) -> None:
        self.converter = DocumentConverter()

    def extract_markdown_from_pdf(self, pdf_path: str | Path) -> dict[str, Any]:
        """
        Extrai conteúdo markdown de um arquivo PDF.

        Args:
            pdf_path: Caminho para o arquivo PDF

        Returns:
            Dict contendo o markdown original e metadados do arquivo

        Raises:
            PDFConversionException: Se houver erro na conversão
            FileNotFoundException: Se o arquivo não for encontrado
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            logger.error(f"Arquivo não encontrado: {pdf_path}")
            raise FileNotFoundException(f"Arquivo não encontrado: {pdf_path}")

        try:
            logger.info(f"Iniciando conversão do PDF: {pdf_path}")
            start_time = time.time()

            conv_result = self.converter.convert(str(pdf_path))
            original_md = conv_result.document.export_to_markdown()

            conversion_time = time.time() - start_time
            logger.info(
                f"PDF convertido com sucesso: {len(original_md)} caracteres em "
                f"{conversion_time:.2f}s"
            )

            # Criar e validar resultado da extração
            extraction_result = ExtractionResult(
                original_md=original_md,
            )

            # Criar metadados de conversão
            metadata = ConversionMetadata(
                file_size=f"{pdf_path.stat().st_size / 1024:.0f} KB",
                conversion_time=f"{conversion_time:.0f}s",
                character_count=len(original_md),
            )

            # Retornar resultado estruturado
            return {
                "extraction_result": extraction_result.model_dump(),
                "metadata": metadata.model_dump(),
            }

        except ValidationError as e:
            logger.error(f"Erro de validação dos dados: {e}")
            raise PDFConversionException(f"Erro de validação: {e}")
        except Exception as e:
            logger.error(f"Erro ao extrair markdown do PDF: {e}")
            raise PDFConversionException(f"Erro na conversão: {str(e)}")

    def validate_pdf_content(self, pdf_path: str | Path) -> bool:
        """Valida se o PDF pode ser processado."""
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                return False

            # Verificar se o arquivo não está corrompido
            with open(pdf_path, "rb") as f:
                header = f.read(4)
                if header != b"%PDF":
                    return False

            return True
        except Exception as e:
            logger.error(f"Erro na validação do PDF: {e}")
            return False

    def get_pdf_info(self, pdf_path: str | Path) -> PDFInfo | None:
        """Obtém informações básicas do PDF."""
        try:
            pdf_path = Path(pdf_path)
            stat = pdf_path.stat()

            return PDFInfo(
                filename=pdf_path.name,
                file_size=stat.st_size,
                file_path=str(pdf_path),
                created_at=stat.st_ctime,
                modified_at=stat.st_mtime,
            )
        except Exception as e:
            logger.error(f"Erro ao obter informações do PDF: {e}")
            return None
