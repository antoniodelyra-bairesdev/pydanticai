class DocumentExtractionException(Exception):
    """Exceção base para erros de extração de documentos"""

    def __init__(self, message: str, error_code: str = "EXTRACTION_ERROR") -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class UnsupportedFormatException(DocumentExtractionException):
    """Formato de documento não suportado"""

    def __init__(self, message: str, error_code: str = "UNSUPPORTED_FORMAT") -> None:
        super().__init__(message, error_code)


class FileValidationException(DocumentExtractionException):
    """Erro de validação de arquivo"""

    def __init__(self, message: str, error_code: str = "FILE_VALIDATION_ERROR") -> None:
        super().__init__(message, error_code)


class ExtractionTimeoutException(DocumentExtractionException):
    """Timeout na extração de documento"""

    def __init__(self, message: str, error_code: str = "EXTRACTION_TIMEOUT") -> None:
        super().__init__(message, error_code)


class FileSizeException(DocumentExtractionException):
    """Arquivo muito grande para processamento"""

    def __init__(self, message: str, error_code: str = "FILE_SIZE_ERROR") -> None:
        super().__init__(message, error_code)


class ExtractorNotFoundException(DocumentExtractionException):
    """Extrator específico não encontrado"""

    def __init__(self, message: str, error_code: str = "EXTRACTOR_NOT_FOUND") -> None:
        super().__init__(message, error_code)


class FileNotFoundException(DocumentExtractionException):
    """Arquivo não encontrado"""

    def __init__(self, message: str, error_code: str = "FILE_NOT_FOUND") -> None:
        super().__init__(message, error_code)
