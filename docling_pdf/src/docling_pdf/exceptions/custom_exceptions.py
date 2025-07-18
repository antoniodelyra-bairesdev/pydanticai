from fastapi import HTTPException


class PDFConversionException(Exception):
    """Exceção para erros de conversão de PDF."""

    def __init__(self, message: str, error_code: str = "CONVERSION_ERROR") -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class FileValidationException(Exception):
    """Exceção para erros de validação de arquivo."""

    def __init__(self, message: str, error_code: str = "FILE_VALIDATION_ERROR") -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class FileSizeException(Exception):
    """Exceção para erros de tamanho de arquivo."""

    def __init__(self, message: str, error_code: str = "FILE_SIZE_ERROR") -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class FileNotFoundException(Exception):
    """Exceção para arquivo não encontrado."""

    def __init__(self, message: str, error_code: str = "FILE_NOT_FOUND") -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


def create_http_exception(
    status_code: int, message: str, error_code: str = "GENERIC_ERROR"
) -> HTTPException:
    """Cria uma exceção HTTP padronizada."""
    return HTTPException(
        status_code=status_code,
        detail={"success": False, "error": message, "error_code": error_code},
    )
