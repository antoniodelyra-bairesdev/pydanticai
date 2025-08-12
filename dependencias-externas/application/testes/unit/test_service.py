import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

from modules.leitor_documentos.base import DocumentExtractor
from modules.leitor_documentos.exceptions import (
    DocumentExtractionException,
    ExtractorNotFoundException,
    FileNotFoundException,
)
from modules.leitor_documentos.impl.docling import PDFDoclingExtractor
from modules.leitor_documentos.impl.pypdf import PDFPypdfExtractor
from modules.leitor_documentos.service import LeitorDocumentosService


class TestLeitorDocumentosService:
    """Testes unitários isolados do serviço principal"""

    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.service = LeitorDocumentosService()

    @patch.object(DocumentExtractor, "get_extractor")
    def test_get_extractor_pdf_default(self, mock_get_extractor):
        """Testa obtenção do extractor padrão para PDF"""
        mock_extractor = Mock(spec=PDFDoclingExtractor)
        mock_extractor.name = "docling_pdf"
        mock_get_extractor.return_value = mock_extractor

        result = self.service._get_extractor("pdf")

        assert result == mock_extractor
        mock_get_extractor.assert_called_once_with("pdf")

    @patch.object(DocumentExtractor, "get_extractor")
    def test_get_extractor_with_tool_preference(self, mock_get_extractor):
        """Testa obtenção do extractor com preferência de ferramenta"""
        mock_extractor = Mock(spec=PDFPypdfExtractor)
        mock_extractor.name = "pypdf"
        mock_get_extractor.return_value = mock_extractor

        result = self.service._get_extractor("pdf", "pypdf")

        assert result == mock_extractor
        mock_get_extractor.assert_called_once_with("pdf", "pypdf")

    @patch.object(DocumentExtractor, "get_extractor")
    def test_get_extractor_nonexistent_tool(self, mock_get_extractor):
        """Testa erro ao solicitar ferramenta inexistente"""
        mock_get_extractor.side_effect = KeyError("Extractor não encontrado")

        with pytest.raises(ExtractorNotFoundException):
            self.service._get_extractor("pdf", "ferramenta_inexistente")

    @patch.object(DocumentExtractor, "__subclasses__")
    def test_get_extractor_names_for_format_pdf(self, mock_subclasses):
        """Testa obtenção de nomes de extractors para PDF"""
        # Mock das classes de extractor
        mock_pdf_docling = Mock()
        mock_pdf_docling.return_value.supported_extensions = ["pdf"]
        mock_pdf_docling.return_value.name = "docling_pdf"

        mock_pdf_pypdf = Mock()
        mock_pdf_pypdf.return_value.supported_extensions = ["pdf"]
        mock_pdf_pypdf.return_value.name = "pypdf"

        mock_docx_extractor = Mock()
        mock_docx_extractor.return_value.supported_extensions = ["docx"]
        mock_docx_extractor.return_value.name = "docling_docx"

        mock_subclasses.return_value = [
            mock_pdf_docling,
            mock_pdf_pypdf,
            mock_docx_extractor,
        ]

        result = self.service.get_extractor_names_for_format("pdf")

        assert "pdf" in result
        extractors = result["pdf"]
        assert len(extractors) == 2

        extractor_names = [e["name"] for e in extractors]
        assert "docling_pdf" in extractor_names
        assert "pypdf" in extractor_names

    @patch("modules.leitor_documentos.service.time.time")
    @patch("pathlib.Path.stat")
    @patch.object(LeitorDocumentosService, "_get_extractor")
    def test_extract_to_markdown_success(
        self, mock_get_extractor, mock_stat, mock_time
    ):
        """Testa extração para markdown com sucesso"""
        # Mock do tempo
        mock_time.side_effect = [1000.0, 1001.5]  # start_time, end_time

        # Mock do stat do arquivo
        mock_stat_result = Mock()
        mock_stat_result.st_size = 2048
        mock_stat.return_value = mock_stat_result

        # Mock do extractor
        mock_extractor = Mock()
        mock_extractor.name = "docling_pdf"
        mock_extractor.extract_to_markdown.return_value = "# Título\n\nConteúdo"
        mock_get_extractor.return_value = mock_extractor

        result = self.service.extract_to_markdown(Path("exemplo.pdf"))

        # Verificar que o resultado é do tipo correto
        assert hasattr(result, "extraction_result")
        assert hasattr(result, "metadata")

        # Verificar o extraction_result
        assert result.extraction_result.content == "# Título\n\nConteúdo"
        assert result.extraction_result.format == "markdown"
        assert result.extraction_result.extractor_used == "docling_pdf"

        # Verificar o metadata
        assert result.metadata.character_count == 18
        assert result.metadata.extractor_used == "docling_pdf"

    @patch("modules.leitor_documentos.service.time.time")
    @patch("pathlib.Path.stat")
    @patch.object(LeitorDocumentosService, "_get_extractor")
    def test_extract_raw_data_success(self, mock_get_extractor, mock_stat, mock_time):
        """Testa extração de dados brutos com sucesso"""
        mock_time.side_effect = [1000.0, 1002.0]

        mock_stat_result = Mock()
        mock_stat_result.st_size = 1024
        mock_stat.return_value = mock_stat_result

        mock_extractor = Mock()
        mock_extractor.name = "pypdf"
        mock_extractor.extract_raw_data.return_value = "Dados brutos extraídos"
        mock_get_extractor.return_value = mock_extractor

        result = self.service.extract_raw_data(Path("exemplo.pdf"), tool="pypdf")

        # Verificar o extraction_result
        assert result.extraction_result.content == "Dados brutos extraídos"
        assert result.extraction_result.format == "raw"
        assert result.extraction_result.extractor_used == "pypdf"

    @patch("modules.leitor_documentos.service.time.time")
    @patch("pathlib.Path.stat")
    @patch.object(LeitorDocumentosService, "_get_extractor")
    def test_extract_image_data_success(self, mock_get_extractor, mock_stat, mock_time):
        """Testa extração de dados de imagens com sucesso"""
        mock_time.side_effect = [1000.0, 1003.5]

        mock_stat_result = Mock()
        mock_stat_result.st_size = 4096
        mock_stat.return_value = mock_stat_result

        mock_extractor = Mock()
        mock_extractor.name = "docling_pdf"
        mock_extractor.extract_image_data.return_value = "Texto das imagens"
        mock_get_extractor.return_value = mock_extractor

        result = self.service.extract_image_data(Path("exemplo.pdf"))

        # Verificar o extraction_result
        assert result.extraction_result.content == "Texto das imagens"
        assert result.extraction_result.format == "images"
        assert result.extraction_result.extractor_used == "docling_pdf"


class TestServiceErrorHandling:
    """Testes unitários para tratamento de erros no serviço"""

    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.service = LeitorDocumentosService()

    @patch.object(LeitorDocumentosService, "_get_extractor")
    def test_extract_to_markdown_extractor_error(self, mock_get_extractor):
        """Testa propagação de erro do extractor no extract_to_markdown"""
        mock_extractor = Mock()
        mock_extractor.extract_to_markdown.side_effect = DocumentExtractionException(
            "Erro de extração"
        )
        mock_get_extractor.return_value = mock_extractor

        with pytest.raises(DocumentExtractionException):
            self.service.extract_to_markdown(Path("exemplo.pdf"))

    @patch.object(LeitorDocumentosService, "_get_extractor")
    def test_extract_raw_data_extractor_error(self, mock_get_extractor):
        """Testa propagação de erro do extractor no extract_raw_data"""
        mock_extractor = Mock()
        mock_extractor.extract_raw_data.side_effect = FileNotFoundException(
            "Arquivo não encontrado"
        )
        mock_get_extractor.return_value = mock_extractor

        with pytest.raises(FileNotFoundException):
            self.service.extract_raw_data(Path("inexistente.pdf"))

    @patch.object(LeitorDocumentosService, "_get_extractor")
    def test_extract_image_data_extractor_error(self, mock_get_extractor):
        """Testa propagação de erro do extractor no extract_image_data"""
        mock_extractor = Mock()
        mock_extractor.extract_image_data.side_effect = NotImplementedError(
            "Método não implementado"
        )
        mock_get_extractor.return_value = mock_extractor

        with pytest.raises(NotImplementedError):
            self.service.extract_image_data(Path("exemplo.pdf"))
