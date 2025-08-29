import os

from fastapi import UploadFile

from .exceptions import FileSizeException, FileValidationException
from .utils import format_file_size, get_file_extension


def validate_document_file(
    file: UploadFile,
    supported_extensions: list[str] = ["pdf", "docx"],
) -> None:
    """
    Valida arquivo de documento enviado via upload.

    Verifica se o arquivo tem nome, extensão suportada e tipo MIME correto.

    Args:
        file (UploadFile): Arquivo enviado via upload
        supported_extensions (list[str]): Lista de extensões permitidas

    Raises:
        FileValidationException: Se o arquivo não passar na validação
    """
    if not file.filename:
        raise FileValidationException("Nome do arquivo não fornecido.")
    file_extension = get_file_extension(file.filename)
    if file_extension not in supported_extensions:
        raise FileValidationException(
            f"Extensão '{file_extension}' não permitida para '{file.filename}'. "
            f"Permitidas: {supported_extensions}"
        )


def validate_file_size(file: UploadFile, max_size: int | None = None) -> None:
    """
    Valida o tamanho do arquivo enviado via upload.

    Verifica se o arquivo não excede o tamanho máximo permitido.
    Se max_size não for fornecido, usa o valor da variável de ambiente
    LEITOR_DOCS_MAX_FILE_SIZE (padrão: 50MB).

    Args:
        file (UploadFile): Arquivo enviado via upload
        max_size (int | None): Tamanho máximo em bytes (opcional)

    Raises:
        FileSizeException: Se o arquivo exceder o tamanho máximo
    """
    if max_size is None:
        max_size = int(os.getenv("LEITOR_DOCS_MAX_FILE_SIZE", str(50 * 1024 * 1024)))
    if file.size and file.size > max_size:
        raise FileSizeException(
            f"Arquivo '{file.filename}' muito grande ({format_file_size(file.size)}). "
            f"Tamanho máximo: {format_file_size(max_size)}"
        )
