"""
Exception handlers para o módulo leitor_documentos.

Este módulo centraliza o tratamento de todas as exceções específicas
do sistema de extração de documentos.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from logger import leitor_logger as logger

from .exceptions import (
    DocumentExtractionException,
    ExtractorNotFoundException,
    FileNotFoundException,
    FileSizeException,
    FileValidationException,
    UnsupportedFormatException,
)


async def file_validation_exception_handler(
    request: Request, exc: FileValidationException
) -> JSONResponse:
    """Handler para erros de validação de arquivo."""
    logger.error("Erro de validação de arquivo na rota {}: {}", request.url.path, str(exc))
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": exc.message,
            "error_code": exc.error_code,
        },
    )


async def file_size_exception_handler(request: Request, exc: FileSizeException) -> JSONResponse:
    """Handler para erros de tamanho de arquivo."""
    logger.error("Arquivo muito grande na rota {}: {}", request.url.path, str(exc))
    return JSONResponse(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        content={
            "success": False,
            "error": exc.message,
            "error_code": exc.error_code,
        },
    )


async def unsupported_format_exception_handler(
    request: Request, exc: UnsupportedFormatException
) -> JSONResponse:
    """Handler para formatos de arquivo não suportados."""
    logger.error("Formato não suportado na rota {}: {}", request.url.path, str(exc))
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": exc.message,
            "error_code": exc.error_code,
        },
    )


async def extractor_not_found_exception_handler(
    request: Request, exc: ExtractorNotFoundException
) -> JSONResponse:
    """Handler para extractor não encontrado."""
    logger.error("Extractor não encontrado na rota {}: {}", request.url.path, str(exc))
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": exc.message,
            "error_code": exc.error_code,
        },
    )


async def file_not_found_exception_handler(
    request: Request, exc: FileNotFoundException
) -> JSONResponse:
    """Handler para arquivo não encontrado."""
    logger.error("Arquivo não encontrado na rota {}: {}", request.url.path, str(exc))
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": exc.message,
            "error_code": exc.error_code,
        },
    )


async def document_extraction_exception_handler(
    request: Request, exc: DocumentExtractionException
) -> JSONResponse:
    """Handler genérico para erros de extração de documentos."""
    logger.error("Erro na extração de documento na rota {}: {}", request.url.path, str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": exc.message,
            "error_code": exc.error_code,
        },
    )


async def not_implemented_exception_handler(
    request: Request, exc: NotImplementedError
) -> JSONResponse:
    """Handler para funcionalidades não implementadas."""
    logger.error("Funcionalidade não implementada na rota {}: {}", request.url.path, str(exc))
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "success": False,
            "error": str(exc),
            "error_code": "NOT_IMPLEMENTED",
        },
    )


# Mapeamento de exceções para handlers
EXCEPTION_HANDLERS: dict[type[Exception], callable] = {
    FileValidationException: file_validation_exception_handler,
    FileSizeException: file_size_exception_handler,
    UnsupportedFormatException: unsupported_format_exception_handler,
    ExtractorNotFoundException: extractor_not_found_exception_handler,
    FileNotFoundException: file_not_found_exception_handler,
    DocumentExtractionException: document_extraction_exception_handler,
    NotImplementedError: not_implemented_exception_handler,
}


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registra todos os exception handlers do módulo na aplicação FastAPI.

    Args:
        app: Instância da aplicação FastAPI

    Example:
        from fastapi import FastAPI
        from modules.leitor_documentos.handlers import register_exception_handlers

        app = FastAPI()
        register_exception_handlers(app)
    """
    for exception_class, handler in EXCEPTION_HANDLERS.items():
        app.add_exception_handler(exception_class, handler)

    logger.info(
        "Exception handlers do módulo leitor_documentos registrados: {} handlers",
        len(EXCEPTION_HANDLERS),
    )
