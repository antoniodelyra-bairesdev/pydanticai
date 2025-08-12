import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, mock_open, patch

import pytest

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

from modules.leitor_documentos.exceptions import DocumentExtractionException
from modules.leitor_documentos.service import FileService


class TestFileService:
    """Testes unitários isolados do FileService"""

    def setup_method(self):
        """Configuração inicial para cada teste"""
        with patch("pathlib.Path.mkdir"):
            self.file_service = FileService()

    @patch("modules.leitor_documentos.service.datetime")
    @patch("modules.leitor_documentos.service.uuid.uuid4")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    @pytest.mark.asyncio
    async def test_save_upload_file_success(
        self, mock_mkdir, mock_file, mock_uuid, mock_datetime
    ):
        """Testa salvamento de arquivo de upload com sucesso"""
        # Setup mocks
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        mock_uuid.return_value = "abc123"

        # Mock do UploadFile com read assíncrono
        mock_upload_file = Mock()
        mock_upload_file.filename = "documento.pdf"
        mock_upload_file.read = AsyncMock(return_value=b"conteudo do arquivo")

        # Mock do Path para o arquivo retornado
        mock_file_path = Mock()
        mock_file_path.name = "20240101_120000_abc123.pdf"

        with patch.object(self.file_service, "temp_dir") as mock_temp_dir:
            mock_temp_dir.__truediv__.return_value = mock_file_path

            # Executar teste
            result = await self.file_service.save_upload_file(mock_upload_file)

            # Verificações
            assert result.name == "20240101_120000_abc123.pdf"
            mock_file.assert_called_once()
            mock_upload_file.read.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_upload_file_no_filename(self):
        """Testa erro quando arquivo não tem nome"""
        mock_upload_file = Mock()
        mock_upload_file.filename = None

        with pytest.raises(DocumentExtractionException):
            await self.file_service.save_upload_file(mock_upload_file)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.unlink")
    def test_cleanup_temp_file_exists(self, mock_unlink, mock_exists):
        """Testa limpeza de arquivo que existe"""
        mock_exists.return_value = True

        result = self.file_service.cleanup_temp_file(Path("teste.txt"))

        assert result is True
        mock_unlink.assert_called_once()

    @patch("pathlib.Path.exists")
    def test_cleanup_temp_file_not_exists(self, mock_exists):
        """Testa limpeza de arquivo que não existe"""
        mock_exists.return_value = False

        result = self.file_service.cleanup_temp_file(Path("inexistente.txt"))

        assert result is False

    def test_cleanup_old_files_exception(self):
        """Testa tratamento de exceção durante limpeza"""
        with patch("pathlib.Path.glob") as mock_glob:
            mock_glob.side_effect = Exception("Erro de acesso ao diretório")

            result = self.file_service.cleanup_old_files()

            assert result == 0


class TestFileServiceErrorHandling:
    """Testes unitários para tratamento de erros no FileService"""

    def setup_method(self):
        """Configuração inicial para cada teste"""
        with patch("pathlib.Path.mkdir"):
            self.file_service = FileService()

    @pytest.mark.asyncio
    async def test_save_upload_file_read_error(self):
        """Testa erro durante leitura do arquivo de upload"""
        mock_upload_file = Mock()
        mock_upload_file.filename = "documento.pdf"
        mock_upload_file.read = AsyncMock(side_effect=Exception("Erro de leitura"))

        with pytest.raises(DocumentExtractionException) as exc_info:
            await self.file_service.save_upload_file(mock_upload_file)

        assert "Erro ao salvar arquivo" in str(exc_info.value)

    @patch("builtins.open", new_callable=mock_open)
    @patch("modules.leitor_documentos.service.datetime")
    @patch("modules.leitor_documentos.service.uuid.uuid4")
    @pytest.mark.asyncio
    async def test_save_upload_file_write_error(
        self, mock_uuid, mock_datetime, mock_file
    ):
        """Testa erro durante escrita do arquivo"""
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        mock_uuid.return_value = "abc123"

        mock_upload_file = Mock()
        mock_upload_file.filename = "documento.pdf"
        mock_upload_file.read = AsyncMock(return_value=b"conteudo")

        # Mock do Path para o arquivo retornado
        mock_file_path = Mock()
        mock_file_path.name = "20240101_120000_abc123.pdf"

        with patch.object(self.file_service, "temp_dir") as mock_temp_dir:
            mock_temp_dir.__truediv__.return_value = mock_file_path

            # Mock do open para lançar exceção na escrita
            mock_file.side_effect = IOError("Erro de escrita")

            with pytest.raises(DocumentExtractionException):
                await self.file_service.save_upload_file(mock_upload_file)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.unlink")
    def test_cleanup_temp_file_unlink_error(self, mock_unlink, mock_exists):
        """Testa erro durante remoção de arquivo"""
        mock_exists.return_value = True
        mock_unlink.side_effect = OSError("Erro ao remover arquivo")

        result = self.file_service.cleanup_temp_file(Path("teste.txt"))

        # Deve retornar False quando há erro, mas não lançar exceção
        assert result is False
