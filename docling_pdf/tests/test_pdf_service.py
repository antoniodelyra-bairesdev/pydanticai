from pathlib import Path

import pytest

from src.docling_pdf.exceptions.custom_exceptions import FileNotFoundException
from src.docling_pdf.services.pdf_service import PDFService


class TestPDFService:
    def setup_method(self):
        self.pdf_service = PDFService()

    def test_extract_markdown_from_nonexistent_file(self):
        """Testa extração de arquivo que não existe"""
        with pytest.raises(FileNotFoundException):
            self.pdf_service.extract_markdown_from_pdf("nonexistent.pdf")

    def test_validate_pdf_content_invalid_file(self):
        """Testa validação de arquivo inválido"""
        result = self.pdf_service.validate_pdf_content("invalid.pdf")
        assert result == False

    def test_get_pdf_info_nonexistent_file(self):
        """Testa obtenção de informações de arquivo inexistente"""
        result = self.pdf_service.get_pdf_info("nonexistent.pdf")
        assert result is None

    def test_validate_pdf_content_nonexistent_file(self):
        """Testa validação de arquivo que não existe"""
        result = self.pdf_service.validate_pdf_content("nonexistent.pdf")
        assert result == False

    def test_get_pdf_info_structure(self):
        """Testa estrutura do retorno de get_pdf_info quando arquivo existe"""
        test_file = Path("tests/sample_files/sample.pdf")

        if test_file.exists():
            result = self.pdf_service.get_pdf_info(test_file)

            assert result is not None
            assert hasattr(result, "filename")
            assert hasattr(result, "file_size")
            assert hasattr(result, "file_path")
            assert hasattr(result, "created_at")
            assert hasattr(result, "modified_at")

    @pytest.mark.asyncio
    async def test_extract_markdown_success(self):
        """Testa extração bem-sucedida (requer arquivo PDF de teste)"""
        # Este teste requer um arquivo PDF válido
        test_pdf_path = Path("tests/sample_files/sample.pdf")
        if test_pdf_path.exists():
            result = self.pdf_service.extract_markdown_from_pdf(str(test_pdf_path))
            assert result is not None
            assert "extraction_result" in result
            assert "metadata" in result
            assert "original_md" in result["extraction_result"]
            assert "file_size" in result["metadata"]
            assert "conversion_time" in result["metadata"]
            assert "character_count" in result["metadata"]
