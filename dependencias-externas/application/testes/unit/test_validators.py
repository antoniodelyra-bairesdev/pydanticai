import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import UploadFile

from modules.leitor_documentos.exceptions import (
    FileSizeException,
    FileValidationException,
)
from modules.leitor_documentos.validators import (
    validate_document_file,
    validate_file_size,
)


class TestValidators:
    """Testes unitários isolados dos validadores"""

    def test_validate_document_file_valid_pdf(self):
        """Testa validação de arquivo PDF válido"""
        mock_upload_file = Mock(spec=UploadFile)
        mock_upload_file.filename = "documento.pdf"

        # Não deve lançar exceção
        validate_document_file(mock_upload_file)

    def test_validate_document_file_valid_docx(self):
        """Testa validação de arquivo DOCX válido"""
        mock_upload_file = Mock(spec=UploadFile)
        mock_upload_file.filename = "documento.docx"

        # Não deve lançar exceção
        validate_document_file(mock_upload_file)

    def test_validate_document_file_no_filename(self):
        """Testa erro quando não há nome de arquivo"""
        mock_upload_file = Mock(spec=UploadFile)
        mock_upload_file.filename = None

        with pytest.raises(FileValidationException) as exc_info:
            validate_document_file(mock_upload_file)

        assert "Nome do arquivo não fornecido" in str(exc_info.value)

    def test_validate_document_file_invalid_extension(self):
        """Testa erro com extensão inválida"""
        mock_upload_file = Mock(spec=UploadFile)
        mock_upload_file.filename = "arquivo.txt"

        with pytest.raises(FileValidationException) as exc_info:
            validate_document_file(mock_upload_file)

        assert "Extensão 'txt' não permitida" in str(exc_info.value)

    def test_validate_document_file_custom_extensions(self):
        """Testa validação com extensões customizadas"""
        mock_upload_file = Mock(spec=UploadFile)
        mock_upload_file.filename = "arquivo.txt"

        # Deve passar com extensões customizadas
        validate_document_file(mock_upload_file, supported_extensions=["txt", "md"])

        # Deve falhar com extensões customizadas que não incluem txt
        with pytest.raises(FileValidationException):
            validate_document_file(mock_upload_file, supported_extensions=["pdf"])

    def test_validate_file_size_valid(self):
        """Testa validação de tamanho válido"""
        mock_upload_file = Mock(spec=UploadFile)
        mock_upload_file.filename = "documento.pdf"
        mock_upload_file.size = 1024 * 1024  # 1MB

        # Não deve lançar exceção
        validate_file_size(mock_upload_file, max_size=10 * 1024 * 1024)

    def test_validate_file_size_too_large(self):
        """Testa erro quando arquivo é muito grande"""
        mock_upload_file = Mock(spec=UploadFile)
        mock_upload_file.filename = "documento.pdf"
        mock_upload_file.size = 10 * 1024 * 1024  # 10MB

        with pytest.raises(FileSizeException) as exc_info:
            validate_file_size(
                mock_upload_file, max_size=5 * 1024 * 1024
            )  # Limite de 5MB

        assert "muito grande" in str(exc_info.value)

    def test_validate_file_size_no_size(self):
        """Testa validação quando arquivo não tem tamanho informado"""
        mock_upload_file = Mock(spec=UploadFile)
        mock_upload_file.filename = "documento.pdf"
        mock_upload_file.size = None

        # Não deve lançar exceção
        validate_file_size(mock_upload_file)

    @pytest.mark.parametrize(
        "env_value,expected_max_size",
        [
            ("10485760", 10 * 1024 * 1024),  # 10MB
            ("5242880", 5 * 1024 * 1024),  # 5MB
        ],
    )
    def test_validate_file_size_env_var(self, env_value, expected_max_size):
        """Testa uso da variável de ambiente para tamanho máximo"""

        with patch.dict("os.environ", {"LEITOR_DOCS_MAX_FILE_SIZE": env_value}):
            mock_upload_file = Mock(spec=UploadFile)
            mock_upload_file.filename = "documento.pdf"
            mock_upload_file.size = (
                expected_max_size + 1024
            )  # Um pouco maior que o limite

            with pytest.raises(FileSizeException):
                validate_file_size(mock_upload_file)
