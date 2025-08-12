import sys
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent))


from modules.leitor_documentos.exceptions import DocumentExtractionException, FileNotFoundException
from modules.leitor_documentos.impl.docling import DOCXDoclingExtractor, PDFDoclingExtractor
from modules.leitor_documentos.impl.docx2txt import DOCXDocx2TxtExtractor
from modules.leitor_documentos.impl.llmwhisperer import (
    DOCXLLMWhispererExtractor,
    PDFLLMWhispererExtractor,
)
from modules.leitor_documentos.impl.pypdf import PDFPypdfExtractor


class TestDocumentExtractors:
    """Testes unitários isolados dos extractors com mocks"""

    def test_pdf_docling_extractor_properties(self):
        """Testa propriedades básicas do PDFDoclingExtractor"""
        extractor = PDFDoclingExtractor()
        assert extractor.name == "docling_pdf"
        assert extractor.supported_extensions == ["pdf"]

    def test_docx_docling_extractor_properties(self):
        """Testa propriedades básicas do DOCXDoclingExtractor"""
        extractor = DOCXDoclingExtractor()
        assert extractor.name == "docling_docx"
        assert extractor.supported_extensions == ["docx"]

    def test_pdf_pypdf_extractor_properties(self):
        """Testa propriedades básicas do PDFPypdfExtractor"""
        extractor = PDFPypdfExtractor()
        assert extractor.name == "pypdf"
        assert extractor.supported_extensions == ["pdf"]

    def test_docx_docx2txt_extractor_properties(self):
        """Testa propriedades básicas do DOCXDocx2TxtExtractor"""
        extractor = DOCXDocx2TxtExtractor()
        assert extractor.name == "docx2txt"
        assert extractor.supported_extensions == ["docx"]

    @patch("modules.leitor_documentos.impl.docling.Path.exists")
    @patch("modules.leitor_documentos.impl.docling.DocumentConverter")
    def test_pdf_docling_extract_raw_data_success(
        self, mock_converter_class, mock_exists
    ):
        """Testa extração de dados brutos de PDF com Docling (mockado)"""
        # Setup mocks
        mock_exists.return_value = True
        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter

        # Mock do resultado da conversão
        mock_text = Mock()
        mock_text.text = "Texto extraído do PDF"
        mock_conv_result = Mock()
        mock_conv_result.document.texts = [mock_text]
        mock_converter.convert.return_value = mock_conv_result

        # Executar teste
        extractor = PDFDoclingExtractor()
        result = extractor.extract_raw_data(Path("exemplo.pdf"))

        # Verificações
        assert result == "Texto extraído do PDF"
        mock_converter.convert.assert_called_once_with("exemplo.pdf")

    @patch("modules.leitor_documentos.impl.docling.Path.exists")
    def test_pdf_docling_extract_raw_data_file_not_found(self, mock_exists):
        """Testa erro quando arquivo PDF não existe"""
        mock_exists.return_value = False

        extractor = PDFDoclingExtractor()

        with pytest.raises(FileNotFoundException):
            extractor.extract_raw_data(Path("inexistente.pdf"))

    @patch("modules.leitor_documentos.impl.docling.Path.exists")
    @patch("modules.leitor_documentos.impl.docling.DocumentConverter")
    def test_pdf_docling_extract_raw_data_extraction_error(
        self, mock_converter_class, mock_exists
    ):
        """Testa erro durante extração com Docling"""
        mock_exists.return_value = True
        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        mock_converter.convert.side_effect = Exception("Erro de conversão")

        extractor = PDFDoclingExtractor()

        with pytest.raises(DocumentExtractionException):
            extractor.extract_raw_data(Path("exemplo.pdf"))

    @patch("modules.leitor_documentos.impl.docling.Path.exists")
    @patch("modules.leitor_documentos.impl.docling.DocumentConverter")
    def test_pdf_docling_extract_to_markdown_success(
        self, mock_converter_class, mock_exists
    ):
        """Testa conversão de PDF para markdown com Docling (mockado)"""
        mock_exists.return_value = True
        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter

        mock_conv_result = Mock()
        mock_conv_result.document.export_to_markdown.return_value = (
            "# Título\n\nConteúdo em markdown"
        )
        mock_converter.convert.return_value = mock_conv_result

        extractor = PDFDoclingExtractor()
        result = extractor.extract_to_markdown(Path("exemplo.pdf"))

        assert result == "# Título\n\nConteúdo em markdown"
        mock_conv_result.document.export_to_markdown.assert_called_once()

    @patch("modules.leitor_documentos.impl.pypdf.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"PDF content")
    @patch("modules.leitor_documentos.impl.pypdf.pypdf.PdfReader")
    def test_pdf_pypdf_extract_raw_data_success(
        self, mock_pdf_reader_class, mock_file, mock_exists
    ):
        """Testa extração de dados brutos de PDF com pypdf (mockado)"""
        mock_exists.return_value = True

        # Mock das páginas do PDF
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Texto da página 1"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Texto da página 2"

        mock_pdf_reader = Mock()
        mock_pdf_reader.pages = [mock_page1, mock_page2]
        mock_pdf_reader_class.return_value = mock_pdf_reader

        extractor = PDFPypdfExtractor()
        result = extractor.extract_raw_data(Path("exemplo.pdf"))

        assert result == "Texto da página 1Texto da página 2"

    @patch("modules.leitor_documentos.impl.pypdf.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("modules.leitor_documentos.impl.pypdf.pypdf.PdfReader")
    def test_pdf_pypdf_extract_raw_data_pypdf_error(
        self, mock_pdf_reader_class, mock_file, mock_exists
    ):
        """Testa erro do pypdf durante extração"""
        from pypdf.errors import PyPdfError

        mock_exists.return_value = True
        mock_pdf_reader_class.side_effect = PyPdfError("Erro do pypdf")

        extractor = PDFPypdfExtractor()

        with pytest.raises(DocumentExtractionException):
            extractor.extract_raw_data(Path("exemplo.pdf"))

    def test_pdf_pypdf_not_implemented_methods(self):
        """Testa métodos não implementados do PDFPypdfExtractor"""
        extractor = PDFPypdfExtractor()

        with pytest.raises(NotImplementedError):
            extractor.extract_to_markdown(Path("exemplo.pdf"))

        with pytest.raises(NotImplementedError):
            extractor.extract_image_data(Path("exemplo.pdf"))

    @patch("modules.leitor_documentos.impl.docx2txt.Path.exists")
    @patch("modules.leitor_documentos.impl.docx2txt.docx2txt.process")
    def test_docx_docx2txt_extract_raw_data_success(self, mock_process, mock_exists):
        """Testa extração de dados brutos de DOCX com docx2txt (mockado)"""
        mock_exists.return_value = True
        mock_process.return_value = "Texto extraído do DOCX"

        extractor = DOCXDocx2TxtExtractor()
        result = extractor.extract_raw_data(Path("exemplo.docx"))

        assert result == "Texto extraído do DOCX"
        mock_process.assert_called_once_with("exemplo.docx")

    @patch("modules.leitor_documentos.impl.docx2txt.Path.exists")
    @patch("modules.leitor_documentos.impl.docx2txt.docx2txt.process")
    def test_docx_docx2txt_extract_raw_data_none_result(
        self, mock_process, mock_exists
    ):
        """Testa quando docx2txt retorna None"""
        mock_exists.return_value = True
        mock_process.return_value = None

        extractor = DOCXDocx2TxtExtractor()
        result = extractor.extract_raw_data(Path("exemplo.docx"))

        assert result == ""

    def test_docx_docx2txt_not_implemented_methods(self):
        """Testa métodos não implementados do DOCXDocx2TxtExtractor"""
        extractor = DOCXDocx2TxtExtractor()

        with pytest.raises(NotImplementedError):
            extractor.extract_to_markdown(Path("exemplo.docx"))

        with pytest.raises(NotImplementedError):
            extractor.extract_image_data(Path("exemplo.docx"))


class TestExceptionHandling:
    """Testes unitários específicos para tratamento de exceções"""

    @patch("modules.leitor_documentos.impl.docling.Path.exists")
    @patch("modules.leitor_documentos.impl.docling.DocumentConverter")
    def test_docling_extractor_generic_exception(
        self, mock_converter_class, mock_exists
    ):
        """Testa tratamento de exceção genérica no Docling"""
        mock_exists.return_value = True
        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        mock_converter.convert.side_effect = RuntimeError("Erro inesperado")

        extractor = PDFDoclingExtractor()

        with pytest.raises(DocumentExtractionException) as exc_info:
            extractor.extract_raw_data(Path("exemplo.pdf"))

        assert "Erro ao extrair dados do PDF" in str(exc_info.value)

    @patch("modules.leitor_documentos.impl.pypdf.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("modules.leitor_documentos.impl.pypdf.pypdf.PdfReader")
    def test_pypdf_extractor_generic_exception(
        self, mock_pdf_reader_class, mock_file, mock_exists
    ):
        """Testa tratamento de exceção genérica no pypdf"""
        mock_exists.return_value = True
        mock_pdf_reader_class.side_effect = ValueError("Erro inesperado")

        extractor = PDFPypdfExtractor()

        with pytest.raises(DocumentExtractionException) as exc_info:
            extractor.extract_raw_data(Path("exemplo.pdf"))

        assert "Erro ao extrair dados do PDF" in str(exc_info.value)

    @patch("modules.leitor_documentos.impl.docx2txt.Path.exists")
    @patch("modules.leitor_documentos.impl.docx2txt.docx2txt.process")
    def test_docx2txt_extractor_exception(self, mock_process, mock_exists):
        """Testa tratamento de exceção no docx2txt"""
        mock_exists.return_value = True
        mock_process.side_effect = Exception("Erro ao processar DOCX")

        extractor = DOCXDocx2TxtExtractor()

        with pytest.raises(DocumentExtractionException) as exc_info:
            extractor.extract_raw_data(Path("exemplo.docx"))

        assert "Erro ao extrair dados do DOCX" in str(exc_info.value)


class TestMockingHelpers:
    """Testes para verificar se os mocks estão funcionando corretamente"""

    @patch("modules.leitor_documentos.impl.docling.DocumentConverter")
    def test_docling_converter_mock_verification(self, mock_converter_class):
        """Verifica se o mock do DocumentConverter está funcionando"""
        extractor = PDFDoclingExtractor()

        # Verificar se o converter foi instanciado
        mock_converter_class.assert_called_once()

        # Verificar se a instância foi armazenada
        assert extractor.converter is not None

    @patch("modules.leitor_documentos.impl.pypdf.pypdf.PdfReader")
    @patch("builtins.open", new_callable=mock_open)
    @patch("modules.leitor_documentos.impl.pypdf.Path.exists")
    def test_pypdf_mock_verification(self, mock_exists, mock_file, mock_pdf_reader):
        """Verifica se os mocks do pypdf estão funcionando"""
        mock_exists.return_value = True
        mock_page = Mock()
        mock_page.extract_text.return_value = "texto"
        mock_pdf_reader.return_value.pages = [mock_page]

        extractor = PDFPypdfExtractor()
        result = extractor.extract_raw_data(Path("teste.pdf"))

        # Verificar chamadas dos mocks
        mock_file.assert_called_once()
        mock_pdf_reader.assert_called_once()
        assert result == "texto"

    @patch("modules.leitor_documentos.impl.docx2txt.docx2txt.process")
    @patch("modules.leitor_documentos.impl.docx2txt.Path.exists")
    def test_docx2txt_mock_verification(self, mock_exists, mock_process):
        """Verifica se os mocks do docx2txt estão funcionando"""
        mock_exists.return_value = True
        mock_process.return_value = "texto docx"

        extractor = DOCXDocx2TxtExtractor()
        result = extractor.extract_raw_data(Path("teste.docx"))

        mock_process.assert_called_once_with("teste.docx")
        assert result == "texto docx"


class TestLLMWhispererExtractor:
    """Testes unitários para o LLMWhispererExtractor"""

    def test_pdf_llmwhisperer_extractor_properties(self):
        """Testa propriedades básicas do PDFLLMWhispererExtractor"""
        extractor = PDFLLMWhispererExtractor()
        assert extractor.name == "llmwhisperer_pdf"
        assert extractor.supported_extensions == ["pdf"]

    def test_docx_llmwhisperer_extractor_properties(self):
        """Testa propriedades básicas do DOCXLLMWhispererExtractor"""
        extractor = DOCXLLMWhispererExtractor()
        assert extractor.name == "llmwhisperer_docx"
        assert extractor.supported_extensions == ["docx"]

    @patch("modules.leitor_documentos.impl.llmwhisperer.Path.exists")
    @patch("modules.leitor_documentos.impl.llmwhisperer.LLMWhispererClientV2")
    def test_pdf_llmwhisperer_extract_raw_data_success(
        self, mock_client_class, mock_exists
    ):
        """Testa extração de dados brutos de PDF com LLMWhisperer (mockado)"""
        # Setup mocks
        mock_exists.return_value = True
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock do resultado da extração
        mock_result = {
            "extraction": {
                "result_text": "Texto extraído do PDF com LLMWhisperer"
            }
        }
        mock_client.whisper.return_value = mock_result

        # Executar teste
        extractor = PDFLLMWhispererExtractor()
        result = extractor.extract_raw_data(Path("exemplo.pdf"))

        # Verificações
        assert result == "Texto extraído do PDF com LLMWhisperer"
        mock_client.whisper.assert_called_once_with(
            file_path="exemplo.pdf",
            wait_for_completion=True,
        )

    @patch("modules.leitor_documentos.impl.llmwhisperer.Path.exists")
    @patch("modules.leitor_documentos.impl.llmwhisperer.LLMWhispererClientV2")
    def test_docx_llmwhisperer_extract_raw_data_success(
        self, mock_client_class, mock_exists
    ):
        """Testa extração de dados brutos de DOCX com LLMWhisperer (mockado)"""
        # Setup mocks
        mock_exists.return_value = True
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock do resultado da extração
        mock_result = {
            "extraction": {
                "result_text": "Texto extraído do DOCX com LLMWhisperer"
            }
        }
        mock_client.whisper.return_value = mock_result

        # Executar teste
        extractor = DOCXLLMWhispererExtractor()
        result = extractor.extract_raw_data(Path("exemplo.docx"))

        # Verificações
        assert result == "Texto extraído do DOCX com LLMWhisperer"
        mock_client.whisper.assert_called_once_with(
            file_path="exemplo.docx",
            wait_for_completion=True,
        )

    @patch("modules.leitor_documentos.impl.llmwhisperer.Path.exists")
    def test_pdf_llmwhisperer_extract_raw_data_file_not_found(self, mock_exists):
        """Testa erro quando arquivo PDF não existe"""
        mock_exists.return_value = False

        extractor = PDFLLMWhispererExtractor()

        with pytest.raises(FileNotFoundException):
            extractor.extract_raw_data(Path("inexistente.pdf"))

    @patch("modules.leitor_documentos.impl.llmwhisperer.Path.exists")
    def test_docx_llmwhisperer_extract_raw_data_file_not_found(self, mock_exists):
        """Testa erro quando arquivo DOCX não existe"""
        mock_exists.return_value = False

        extractor = DOCXLLMWhispererExtractor()

        with pytest.raises(FileNotFoundException):
            extractor.extract_raw_data(Path("inexistente.docx"))

    @patch("modules.leitor_documentos.impl.llmwhisperer.Path.exists")
    @patch("modules.leitor_documentos.impl.llmwhisperer.LLMWhispererClientV2")
    def test_pdf_llmwhisperer_extract_raw_data_client_exception(
        self, mock_client_class, mock_exists
    ):
        """Testa erro específico do LLMWhispererClientException para PDF"""
        mock_exists.return_value = True
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        from unstract.llmwhisperer.client_v2 import LLMWhispererClientException
        mock_client.whisper.side_effect = LLMWhispererClientException("Erro do cliente")

        extractor = PDFLLMWhispererExtractor()

        with pytest.raises(DocumentExtractionException) as exc_info:
            extractor.extract_raw_data(Path("exemplo.pdf"))

        assert "Erro ao extrair dados do PDF com LLMWhisperer" in str(exc_info.value)

    @patch("modules.leitor_documentos.impl.llmwhisperer.Path.exists")
    @patch("modules.leitor_documentos.impl.llmwhisperer.LLMWhispererClientV2")
    def test_docx_llmwhisperer_extract_raw_data_client_exception(
        self, mock_client_class, mock_exists
    ):
        """Testa erro específico do LLMWhispererClientException para DOCX"""
        mock_exists.return_value = True
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        from unstract.llmwhisperer.client_v2 import LLMWhispererClientException
        mock_client.whisper.side_effect = LLMWhispererClientException("Erro do cliente")

        extractor = DOCXLLMWhispererExtractor()

        with pytest.raises(DocumentExtractionException) as exc_info:
            extractor.extract_raw_data(Path("exemplo.docx"))

        assert "Erro ao extrair dados do DOCX com LLMWhisperer" in str(exc_info.value)

    @patch("modules.leitor_documentos.impl.llmwhisperer.Path.exists")
    @patch("modules.leitor_documentos.impl.llmwhisperer.LLMWhispererClientV2")
    def test_pdf_llmwhisperer_extract_raw_data_generic_exception(
        self, mock_client_class, mock_exists
    ):
        """Testa erro genérico durante extração de PDF"""
        mock_exists.return_value = True
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.whisper.side_effect = Exception("Erro inesperado")

        extractor = PDFLLMWhispererExtractor()

        with pytest.raises(DocumentExtractionException) as exc_info:
            extractor.extract_raw_data(Path("exemplo.pdf"))

        assert "Erro inesperado na extração do PDF" in str(exc_info.value)

    @patch("modules.leitor_documentos.impl.llmwhisperer.Path.exists")
    @patch("modules.leitor_documentos.impl.llmwhisperer.LLMWhispererClientV2")
    def test_docx_llmwhisperer_extract_raw_data_generic_exception(
        self, mock_client_class, mock_exists
    ):
        """Testa erro genérico durante extração de DOCX"""
        mock_exists.return_value = True
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.whisper.side_effect = Exception("Erro inesperado")

        extractor = DOCXLLMWhispererExtractor()

        with pytest.raises(DocumentExtractionException) as exc_info:
            extractor.extract_raw_data(Path("exemplo.docx"))

        assert "Erro inesperado na extração do DOCX" in str(exc_info.value)

    @patch("modules.leitor_documentos.impl.llmwhisperer.Path.exists")
    @patch("modules.leitor_documentos.impl.llmwhisperer.LLMWhispererClientV2")
    def test_pdf_llmwhisperer_extract_to_markdown_success(
        self, mock_client_class, mock_exists
    ):
        """Testa extração para markdown de PDF (deve retornar mesmo resultado que raw_data)"""
        mock_exists.return_value = True
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_result = {
            "extraction": {
                "result_text": "Texto PDF para markdown"
            }
        }
        mock_client.whisper.return_value = mock_result

        extractor = PDFLLMWhispererExtractor()
        result = extractor.extract_to_markdown(Path("exemplo.pdf"))

        assert result == "Texto PDF para markdown"

    @patch("modules.leitor_documentos.impl.llmwhisperer.Path.exists")
    @patch("modules.leitor_documentos.impl.llmwhisperer.LLMWhispererClientV2")
    def test_docx_llmwhisperer_extract_to_markdown_success(
        self, mock_client_class, mock_exists
    ):
        """Testa extração para markdown de DOCX (deve retornar mesmo resultado que raw_data)"""
        mock_exists.return_value = True
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_result = {
            "extraction": {
                "result_text": "Texto DOCX para markdown"
            }
        }
        mock_client.whisper.return_value = mock_result

        extractor = DOCXLLMWhispererExtractor()
        result = extractor.extract_to_markdown(Path("exemplo.docx"))

        assert result == "Texto DOCX para markdown"

    @patch("modules.leitor_documentos.impl.llmwhisperer.Path.exists")
    @patch("modules.leitor_documentos.impl.llmwhisperer.LLMWhispererClientV2")
    def test_pdf_llmwhisperer_extract_image_data_success(
        self, mock_client_class, mock_exists
    ):
        """Testa extração de dados de imagem de PDF (deve retornar mesmo resultado que raw_data)"""
        mock_exists.return_value = True
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_result = {
            "extraction": {
                "result_text": "Texto PDF incluindo dados de imagem"
            }
        }
        mock_client.whisper.return_value = mock_result

        extractor = PDFLLMWhispererExtractor()
        result = extractor.extract_image_data(Path("exemplo.pdf"))

        assert result == "Texto PDF incluindo dados de imagem"

    @patch("modules.leitor_documentos.impl.llmwhisperer.Path.exists")
    @patch("modules.leitor_documentos.impl.llmwhisperer.LLMWhispererClientV2")
    def test_docx_llmwhisperer_extract_image_data_success(
        self, mock_client_class, mock_exists
    ):
        """Testa extração de dados de imagem de DOCX (deve retornar mesmo resultado que raw_data)"""
        mock_exists.return_value = True
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_result = {
            "extraction": {
                "result_text": "Texto DOCX incluindo dados de imagem"
            }
        }
        mock_client.whisper.return_value = mock_result

        extractor = DOCXLLMWhispererExtractor()
        result = extractor.extract_image_data(Path("exemplo.docx"))

        assert result == "Texto DOCX incluindo dados de imagem"

    @patch("modules.leitor_documentos.impl.llmwhisperer.LLMWhispererClientV2")
    def test_llmwhisperer_client_initialization(self, mock_client_class):
        """Testa se o cliente LLMWhisperer é inicializado corretamente"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Testar ambas as classes
        extractor_pdf = PDFLLMWhispererExtractor()
        extractor_docx = DOCXLLMWhispererExtractor()

        # Verificar se o cliente foi instanciado duas vezes (uma para cada extractor)
        assert mock_client_class.call_count == 2
        assert extractor_pdf.client is not None
        assert extractor_docx.client is not None
