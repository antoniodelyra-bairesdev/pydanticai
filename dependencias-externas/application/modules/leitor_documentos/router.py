import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from logger import leitor_logger as logger

from .exceptions import (
    DocumentExtractionException,
    ExtractorNotFoundException,
    FileNotFoundException,
    FileSizeException,
    FileValidationException,
    UnsupportedFormatException,
)
from .schema import (
    CleanupResponse,
    ConversionMetadata,
    DocumentExtractionResponse,
    ExtractionResult,
    FerramentaExtracaoEnum,
    SupportedFormatsResponse,
)
from .service import FileService, LeitorDocumentosService
from .utils import sanitize_filename
from .validators import validate_document_file, validate_file_size

router = APIRouter(prefix="/leitor-documentos", tags=["Leitor de Documentos"])


def get_document_service() -> LeitorDocumentosService:
    """
    Factory function para criar uma instância do LeitorDocumentosService.
    Esta função é usada como dependência nos endpoints.
    """
    return LeitorDocumentosService()


def get_file_service() -> FileService:
    """
    Factory function para criar uma instância do FileService.
    Esta função é usada como dependência nos endpoints.
    """
    return FileService()


def _handle_extraction_error(
    error: Exception,
    temp_file_path: Path,
    file_service: FileService,
    operation: str,
) -> None:
    """
    Função helper para tratar erros de extração de forma consistente.

    Args:
        error: Exceção capturada
        temp_file_path: Caminho do arquivo temporário
        background_tasks: Tarefas em background
        operation: Nome da operação para log
    """
    # Limpar arquivo temporário se existir
    if temp_file_path:
        file_service.cleanup_temp_file(temp_file_path)

    # Mapear exceções para códigos HTTP apropriados
    if isinstance(error, FileValidationException):
        logger.error("Erro de validação de arquivo: {}", str(error))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": error.message,
                "error_code": error.error_code,
            },
        )
    elif isinstance(error, FileSizeException):
        logger.error("Arquivo muito grande: {}", str(error))
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "success": False,
                "error": error.message,
                "error_code": error.error_code,
            },
        )
    elif isinstance(error, UnsupportedFormatException):
        logger.error("Formato não suportado: {}", str(error))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": error.message,
                "error_code": error.error_code,
            },
        )
    elif isinstance(error, ExtractorNotFoundException):
        logger.error("Extractor não encontrado: {}", str(error))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": error.message,
                "error_code": error.error_code,
            },
        )
    elif isinstance(error, FileNotFoundException):
        logger.error("Arquivo não encontrado: {}", str(error))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": error.message,
                "error_code": error.error_code,
            },
        )
    elif isinstance(error, DocumentExtractionException):
        logger.error("Erro na {}: {}", operation, str(error))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": error.message,
                "error_code": error.error_code,
            },
        )
    elif isinstance(error, NotImplementedError):
        logger.error("Funcionalidade não implementada na {}: {}", operation, str(error))
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "success": False,
                "error": str(error),
                "error_code": "NOT_IMPLEMENTED",
            },
        )
    else:
        logger.error("Erro inesperado na {}: {}", operation, str(error))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Erro interno do servidor",
                "error_code": "INTERNAL_ERROR",
            },
        )


@router.post("/extrair-markdown")
async def extrair_para_markdown(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    ferramenta_extracao: FerramentaExtracaoEnum = Query(None),
    service: LeitorDocumentosService = Depends(get_document_service),
    file_service: FileService = Depends(get_file_service),
) -> DocumentExtractionResponse:
    """
    Extrai conteúdo de um documento e converte para formato markdown.

    Args:
        background_tasks (BackgroundTasks): Tarefas em background para limpeza
        file (UploadFile): Arquivo enviado via upload
        ferramenta_extracao (str, optional): Nome da ferramenta de extração

    Returns:
        DocumentExtractionResponse: Resposta com conteúdo em markdown e metadados

    Raises:
        DocumentExtractionException: Se houver erro na extração
    """
    logger.info(
        "Iniciando extração para markdown: {}", sanitize_filename(file.filename)
    )
    temp_file_path = Path()

    try:
        # Validar arquivo enviado
        validate_document_file(file)
        validate_file_size(file)

        # Salvar arquivo temporariamente
        temp_file_path = await file_service.save_upload_file(file)
        logger.info("Arquivo salvo temporariamente: {}", temp_file_path)

        # Realizar extração
        result = service.extract_to_markdown(
            file_path=temp_file_path,
            tool=ferramenta_extracao.value if ferramenta_extracao else None,
        )

        # Preparar resposta
        response = DocumentExtractionResponse(
            success=True,
            data=ExtractionResult(**result["extraction_result"]),
            metadata=ConversionMetadata(
                **{**result["metadata"], "filename": sanitize_filename(file.filename)}
            ),
        )

        # Agendar limpeza do arquivo temporário
        background_tasks.add_task(file_service.cleanup_temp_file, temp_file_path)

        logger.info(
            "Extração markdown concluída com sucesso: {}",
            sanitize_filename(file.filename),
        )
        return response

    except Exception as e:
        _handle_extraction_error(e, temp_file_path, file_service, "extração markdown")


@router.post("/extrair-dados-brutos")
async def extrair_dados_brutos(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    ferramenta_extracao: FerramentaExtracaoEnum = Query(None),
    service: LeitorDocumentosService = Depends(get_document_service),
    file_service: FileService = Depends(get_file_service),
) -> DocumentExtractionResponse:
    """
    Extrai dados brutos (texto) de um documento.

    Args:
        background_tasks (BackgroundTasks): Tarefas em background para limpeza
        file (UploadFile): Arquivo enviado via upload
        ferramenta_extracao (str, optional): Nome da ferramenta de extração

    Returns:
        DocumentExtractionResponse: Resposta com dados brutos e metadados

    Raises:
        DocumentExtractionException: Se houver erro na extração
    """
    logger.info(
        "Iniciando extração de dados brutos: {}", sanitize_filename(file.filename)
    )
    temp_file_path = Path()

    try:
        # Validar arquivo enviado
        validate_document_file(file)
        validate_file_size(file)

        # Salvar arquivo temporariamente
        temp_file_path = await file_service.save_upload_file(file)
        logger.info("Arquivo salvo temporariamente: {}", temp_file_path)

        # Realizar extração
        result = service.extract_raw_data(
            file_path=temp_file_path,
            tool=ferramenta_extracao.value if ferramenta_extracao else None,
        )

        # Preparar resposta
        response = DocumentExtractionResponse(
            success=True,
            data=ExtractionResult(**result["extraction_result"]),
            metadata=ConversionMetadata(
                **{**result["metadata"], "filename": sanitize_filename(file.filename)}
            ),
        )

        # Agendar limpeza do arquivo temporário
        background_tasks.add_task(file_service.cleanup_temp_file, temp_file_path)

        logger.info(
            "Extração de dados brutos concluída com sucesso: {}",
            sanitize_filename(file.filename),
        )
        return response

    except Exception as e:
        _handle_extraction_error(
            e,
            temp_file_path,
            file_service,
            "extração de dados brutos",
        )


@router.post("/extrair-dados-imagens")
async def extrair_imagens(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    ferramenta_extracao: FerramentaExtracaoEnum = Query(None),
    service: LeitorDocumentosService = Depends(get_document_service),
    file_service: FileService = Depends(get_file_service),
) -> DocumentExtractionResponse:
    """
    Extrai texto de imagens contidas em um documento.

    Args:
        background_tasks (BackgroundTasks): Tarefas em background para limpeza
        file (UploadFile): Arquivo enviado via upload
        ferramenta_extracao (str, optional): Nome da ferramenta de extração

    Returns:
        DocumentExtractionResponse: Resposta com texto das imagens e metadados

    Raises:
        DocumentExtractionException: Se houver erro na extração
    """
    logger.info(
        "Iniciando extração de dados de imagens: {}", sanitize_filename(file.filename)
    )
    temp_file_path = Path()

    try:
        # Validar arquivo enviado
        validate_document_file(file)
        validate_file_size(file)

        # Salvar arquivo temporariamente
        temp_file_path = await file_service.save_upload_file(file)
        logger.info("Arquivo salvo temporariamente: {}", temp_file_path)

        # Realizar extração de imagens
        result = service.extract_image_data(
            file_path=temp_file_path,
            tool=ferramenta_extracao.value if ferramenta_extracao else None,
        )

        # Preparar resposta
        response = DocumentExtractionResponse(
            success=True,
            data=ExtractionResult(**result["extraction_result"]),
            metadata=ConversionMetadata(
                **{**result["metadata"], "filename": sanitize_filename(file.filename)}
            ),
        )

        # Agendar limpeza do arquivo temporário
        background_tasks.add_task(file_service.cleanup_temp_file, temp_file_path)

        logger.info(
            "Extração de imagens concluída com sucesso: {}",
            sanitize_filename(file.filename),
        )
        return response

    except Exception as e:
        _handle_extraction_error(e, temp_file_path, file_service, "extração de imagens")


@router.get("/formatos-suportados")
async def listar_formatos_suportados(
    extensao: str = Query("pdf"),
    service: LeitorDocumentosService = Depends(get_document_service),
) -> SupportedFormatsResponse:
    """
    Lista todos os formatos de arquivo suportados e seus extractors disponíveis.

    Returns:
        SupportedFormatsResponse: Resposta com formatos suportados

    Raises:
        DocumentExtractionException: Se houver erro ao obter formatos
    """
    logger.info("Solicitando lista de formatos suportados")

    try:
        formats = service.get_extractor_names_for_format(extensao)
        logger.info("Formatos suportados obtidos com sucesso")
        return SupportedFormatsResponse(success=True, formats=formats)
    except Exception as e:
        logger.error("Erro ao obter formatos suportados: {}", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Erro ao obter formatos suportados",
                "error_code": "INTERNAL_ERROR",
            },
        )


@router.post("/limpeza")
async def limpar_arquivos_temporarios(
    max_age_hours: int = Query(24, ge=1, le=168),
    file_service: FileService = Depends(get_file_service),
) -> CleanupResponse:
    """
    Remove arquivos temporários antigos do sistema.

    Args:
        max_age_hours (int): Idade máxima em horas para manter arquivos (1-168)

    Returns:
        CleanupResponse: Resposta com número de arquivos removidos

    Raises:
        DocumentExtractionException: Se houver erro durante a limpeza
    """
    logger.info(
        "Iniciando limpeza de arquivos temporários (max_age: {}h)", max_age_hours
    )

    try:
        removed_count = file_service.cleanup_old_files(max_age_hours)
        logger.info("Limpeza concluída. {} arquivo(s) removido(s)", removed_count)

        return CleanupResponse(
            success=True,
            message=f"{removed_count} arquivo(s) removido(s).",
            removed_count=removed_count,
        )
    except Exception as e:
        logger.error("Erro durante limpeza de arquivos temporários: {}", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Erro durante limpeza de arquivos temporários",
                "error_code": "INTERNAL_ERROR",
            },
        )
