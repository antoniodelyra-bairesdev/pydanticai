import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

from modules.leitor_documentos.service import LeitorDocumentosService, FileService
from modules.leitor_documentos.exceptions import (
    UnsupportedFormatException,
    FileNotFoundException,
    DocumentExtractionException,
    ExtractorNotFoundException,
)
from modules.leitor_documentos.impl.docling import PDFDoclingExtractor, DOCXDoclingExtractor
from modules.leitor_documentos.impl.pypdf import PDFPypdfExtractor
from modules.leitor_documentos.impl.docx2txt import DOCXDocx2TxtExtractor


class TestLeitorDocumentosService:
    """Testes unitários do serviço principal"""

    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.service = LeitorDocumentosService()

    def test_formatos_suportados(self):
        """Testa obtenção de formatos suportados"""
        formats = self.service.get_supported_formats()
        assert isinstance(formats, dict)
        assert "pdf" in formats
        assert "docx" in formats
        
        # Verificar se os extractors estão registrados
        pdf_extractors = formats["pdf"]
        docx_extractors = formats["docx"]
        
        assert len(pdf_extractors) > 0
        assert len(docx_extractors) > 0

    def test_extractor_names_formato_valido(self):
        """Testa obtenção de nomes de extractors para formato válido"""
        extractors = self.service.get_extractor_names_for_format("pdf")
        assert isinstance(extractors, list)
        assert len(extractors) > 0
        assert "docling_pdf" in extractors

    def test_extractor_names_formato_invalido(self):
        """Testa obtenção de extractors para formato inválido"""
        extractors = self.service.get_extractor_names_for_format("xyz")
        assert extractors == []

    def test_get_extractor_pdf_padrao(self):
        """Testa obtenção do extractor padrão para PDF"""
        extractor = self.service._get_extractor("pdf")
        assert isinstance(extractor, PDFDoclingExtractor)
        assert extractor.name == "docling_pdf"

    def test_get_extractor_docx_padrao(self):
        """Testa obtenção do extractor padrão para DOCX"""
        extractor = self.service._get_extractor("docx")
        assert isinstance(extractor, DOCXDoclingExtractor)
        assert extractor.name == "docling_docx"

    def test_get_extractor_com_preferencia(self):
        """Testa obtenção do extractor com preferência específica"""
        extractor = self.service._get_extractor("pdf", "pypdf")
        assert isinstance(extractor, PDFPypdfExtractor)
        assert extractor.name == "pypdf"

    def test_get_extractor_preferencia_inexistente(self):
        """Testa obtenção com extractor preferido inexistente"""
        with pytest.raises(ExtractorNotFoundException):
            self.service._get_extractor("pdf", "ExtractorInexistente")

    def test_get_extractor_formato_nao_suportado(self):
        """Testa obtenção de extractor para formato não suportado"""
        with pytest.raises(UnsupportedFormatException):
            self.service._get_extractor("xyz")

    @patch('modules.leitor_documentos.service.DocumentExtractor.get_extractor')
    def test_extract_to_markdown_sucesso(self, mock_get_extractor):
        """Testa extração para markdown com sucesso"""
        # Mock do extractor
        mock_extractor = Mock()
        mock_extractor.name = "docling_pdf"
        mock_extractor.extract_to_markdown.return_value = "# Título\n\nConteúdo"
        mock_get_extractor.return_value = mock_extractor

        # Mock do Path.stat()
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 1024

            result = self.service.extract_to_markdown("exemplo.pdf")

            assert "extraction_result" in result
            assert "metadata" in result
            assert result["extraction_result"]["content"] == "# Título\n\nConteúdo"
            assert result["extraction_result"]["format"] == "markdown"
            assert result["extraction_result"]["extractor_used"] == "docling_pdf"
            assert result["metadata"]["character_count"] == 15

    @patch('modules.leitor_documentos.service.DocumentExtractor.get_extractor')
    def test_extract_raw_data_sucesso(self, mock_get_extractor):
        """Testa extração de dados brutos com sucesso"""
        # Mock do extractor
        mock_extractor = Mock()
        mock_extractor.name = "docling_pdf"
        mock_extractor.extract_raw_data.return_value = "Texto extraído"
        mock_get_extractor.return_value = mock_extractor

        # Mock do Path.stat()
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 1024

            result = self.service.extract_raw_data("exemplo.pdf")

            assert "extraction_result" in result
            assert "metadata" in result
            assert result["extraction_result"]["content"] == "Texto extraído"
            assert result["extraction_result"]["format"] == "raw"
            assert result["extraction_result"]["extractor_used"] == "docling_pdf"

    @patch('modules.leitor_documentos.service.DocumentExtractor.get_extractor')
    def test_extract_image_data_sucesso(self, mock_get_extractor):
        """Testa extração de dados de imagens com sucesso"""
        # Mock do extractor
        mock_extractor = Mock()
        mock_extractor.name = "docling_pdf"
        mock_extractor.extract_image_data.return_value = "Texto das imagens"
        mock_get_extractor.return_value = mock_extractor

        # Mock do Path.stat()
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 1024

            result = self.service.extract_image_data("exemplo.pdf")

            assert "extraction_result" in result
            assert "metadata" in result
            assert result["extraction_result"]["content"] == "Texto das imagens"
            assert result["extraction_result"]["format"] == "images"
            assert result["extraction_result"]["extractor_used"] == "docling_pdf"


class TestFileService:
    """Testes unitários do FileService"""

    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.file_service = FileService()

    @patch('pathlib.Path.mkdir')
    def test_init_cria_diretorio(self, mock_mkdir):
        """Testa se o diretório temporário é criado na inicialização"""
        FileService()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch('pathlib.Path.exists')
    def test_cleanup_temp_file_arquivo_existe(self, mock_exists):
        """Testa limpeza de arquivo temporário que existe"""
        mock_exists.return_value = True
        
        with patch('pathlib.Path.unlink') as mock_unlink:
            result = self.file_service.cleanup_temp_file("exemplo.pdf")
            
            assert result is True
            mock_unlink.assert_called_once()

    @patch('pathlib.Path.exists')
    def test_cleanup_temp_file_arquivo_nao_existe(self, mock_exists):
        """Testa limpeza de arquivo temporário que não existe"""
        mock_exists.return_value = False
        
        result = self.file_service.cleanup_temp_file("exemplo.pdf")
        assert result is False

    @patch('pathlib.Path.glob')
    @patch('time.time')
    def test_cleanup_old_files(self, mock_time, mock_glob):
        """Testa limpeza de arquivos antigos"""
        mock_time.return_value = 1000  # Timestamp atual
        
        # Mock de arquivos antigos
        mock_file1 = Mock()
        mock_file1.is_file.return_value = True
        mock_file1.stat.return_value.st_mtime = 500  # 500 segundos atrás
        
        mock_file2 = Mock()
        mock_file2.is_file.return_value = True
        mock_file2.stat.return_value.st_mtime = 900  # 100 segundos atrás
        
        mock_glob.return_value = [mock_file1, mock_file2]
        
        # Mock do método unlink para não executar realmente
        with patch.object(mock_file1, 'unlink') as mock_unlink1:
            with patch.object(mock_file2, 'unlink') as mock_unlink2:
                result = self.file_service.cleanup_old_files(max_age_hours=1)  # 3600 segundos
                
                # Verificar se os métodos foram chamados
                mock_unlink1.assert_called_once()
                mock_unlink2.assert_not_called()
                assert result == 1  # Apenas o arquivo mais antigo foi removido


class TestExtractors:
    """Testes unitários dos extractors"""

    def test_docling_pdf_extractor_properties(self):
        """Testa propriedades do DoclingPDFExtractor"""
        extractor = PDFDoclingExtractor()
        
        assert extractor.name == "docling_pdf"
        assert extractor.supported_extensions == ["pdf"]

    def test_docling_docx_extractor_properties(self):
        """Testa propriedades do DoclingDOCXExtractor"""
        extractor = DOCXDoclingExtractor()
        
        assert extractor.name == "docling_docx"
        assert extractor.supported_extensions == ["docx"]

    def test_pypdf_extractor_properties(self):
        """Testa propriedades do PypdfExtractor"""
        extractor = PDFPypdfExtractor()
        
        assert extractor.name == "pypdf"
        assert extractor.supported_extensions == ["pdf"]

    def test_docx2txt_extractor_properties(self):
        """Testa propriedades do Docx2TxtExtractor"""
        extractor = DOCX2Docx2TxtExtractor()
        
        assert extractor.name == "docx2txt"
        assert extractor.supported_extensions == ["docx"]

    @patch('pathlib.Path.exists')
    def test_extractor_arquivo_nao_existe(self, mock_exists):
        """Testa extractor com arquivo que não existe"""
        mock_exists.return_value = False
        
        extractor = PDFDoclingExtractor()
        
        with pytest.raises(FileNotFoundException):
            extractor.extract_raw_data("arquivo_inexistente.pdf")

    def test_pypdf_extractor_not_implemented_methods(self):
        """Testa métodos não implementados do PypdfExtractor"""
        extractor = PDFPypdfExtractor()
        
        with pytest.raises(NotImplementedError):
            extractor.extract_to_markdown("exemplo.pdf")
        
        with pytest.raises(NotImplementedError):
            extractor.extract_image_data("exemplo.pdf")

    def test_docx2txt_extractor_not_implemented_methods(self):
        """Testa métodos não implementados do Docx2TxtExtractor"""
        extractor = DOCX2Docx2TxtExtractor()
        
        with pytest.raises(NotImplementedError):
            extractor.extract_to_markdown("exemplo.docx")
        
        with pytest.raises(NotImplementedError):
            extractor.extract_image_data("exemplo.docx") 