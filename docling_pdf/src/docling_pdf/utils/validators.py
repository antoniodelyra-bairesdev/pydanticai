from pathlib import Path

from fastapi import UploadFile

from ..config import settings
from ..exceptions.custom_exceptions import FileSizeException, FileValidationException


def validate_pdf_file(file: UploadFile) -> None:
    """Valida se o arquivo é um PDF válido."""
    if not file.filename:
        raise FileValidationException("Nome do arquivo não fornecido.")

    # Verificar extensão
    file_extension = Path(file.filename).suffix.lower().lstrip(".")
    if file_extension not in settings.allowed_extensions:
        raise FileValidationException(
            f"Extensão '{file_extension}' não permitida para '{file.filename}'. "
            f"Permitidas: {settings.allowed_extensions}"
        )

    # Verificar content type
    if file.content_type != "application/pdf":
        raise FileValidationException(
            f"Tipo de arquivo '{file.content_type}' inválido para '{file.filename}'. "
            f"Apenas PDF permitido."
        )


def validate_file_size(file: UploadFile) -> None:
    """Valida o tamanho do arquivo."""
    # UploadFile não tem .size, então precisamos ler o arquivo
    file.file.seek(0, 2)  # Vai para o final do arquivo
    size = file.file.tell()
    file.file.seek(0)  # Volta para o início

    if size > settings.max_file_size:
        max_size_mb = settings.max_file_size / (1024 * 1024)
        raise FileSizeException(
            f"Arquivo '{file.filename}' muito grande ({size} bytes). "
            f"Tamanho máximo: {max_size_mb:.1f}MB"
        )


def sanitize_filename(filename: str) -> str:
    """Remove caracteres perigosos do nome do arquivo."""
    return Path(filename).name.replace("..", "").replace("/", "_").replace("\\", "_")
