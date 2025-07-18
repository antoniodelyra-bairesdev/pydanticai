from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status
from loguru import logger

from ..exceptions.custom_exceptions import (
    FileSizeException,
    FileValidationException,
    PDFConversionException,
)
from ..models.response_models import ConversionResponse
from ..services.file_service import FileService
from ..services.pdf_service import PDFService
from ..utils.validators import validate_file_size, validate_pdf_file

router = APIRouter(prefix="/pdf", tags=["PDF Conversion"])

pdf_service = PDFService()
file_service = FileService()


@router.post("/convert")
async def convert_pdf_to_markdown(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Arquivo PDF para conversão"),
) -> ConversionResponse:
    """
    Converte um arquivo PDF para formato Markdown.

    - **file**: Arquivo PDF (máximo 50MB)

    Returns:
    - **success**: Status da conversão
    - **markdown_content**: Conteúdo convertido em markdown
    - **metadata**: Metadados da conversão
    """
    temp_file_path = None

    try:
        # Validações
        validate_pdf_file(file)
        validate_file_size(file)

        # Salvar arquivo temporariamente
        temp_file_path = await file_service.save_upload_file(file)

        # Validar conteúdo do PDF
        if not pdf_service.validate_pdf_content(temp_file_path):
            raise PDFConversionException("Arquivo PDF inválido ou corrompido")

        # Converter PDF para Markdown
        result = pdf_service.extract_markdown_from_pdf(temp_file_path)

        if not result:
            raise PDFConversionException("Falha na conversão do PDF")

        # Preparar resposta
        extraction_result = result.get("extraction_result", {})
        metadata_result = result.get("metadata", {})

        response = ConversionResponse(
            success=True,
            markdown_content=extraction_result.get("original_md"),
            metadata={
                "filename": file.filename,
                "conversion_time": metadata_result.get("conversion_time"),
                "character_count": metadata_result.get("character_count"),
                "file_size": metadata_result.get("file_size"),
                "converted_at": datetime.now().isoformat(),
            },
            message="Conversão realizada com sucesso",
        )

        # Agendar limpeza do arquivo temporário
        background_tasks.add_task(file_service.cleanup_temp_file, temp_file_path)

        return response

    except FileValidationException as e:
        if temp_file_path:
            background_tasks.add_task(file_service.cleanup_temp_file, temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "error": e.message, "error_code": e.error_code},
        )

    except FileSizeException as e:
        if temp_file_path:
            background_tasks.add_task(file_service.cleanup_temp_file, temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={"success": False, "error": e.message, "error_code": e.error_code},
        )

    except PDFConversionException as e:
        if temp_file_path:
            background_tasks.add_task(file_service.cleanup_temp_file, temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "error": e.message, "error_code": e.error_code},
        )

    except Exception as e:
        if temp_file_path:
            background_tasks.add_task(file_service.cleanup_temp_file, temp_file_path)
        logger.error(f"Erro inesperado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Erro interno do servidor",
                "error_code": "INTERNAL_ERROR",
            },
        )


@router.get("/health")
async def health_check():
    """Verifica o status da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "PDF to Markdown Converter",
    }


@router.post("/cleanup")
async def cleanup_temp_files(max_age_hours: int = 24):
    """
    Remove arquivos temporários antigos.

    - **max_age_hours**: Idade máxima dos arquivos em horas (padrão: 24)
    """
    try:
        removed_count = file_service.cleanup_old_files(max_age_hours)
        return {
            "success": True,
            "message": f"{removed_count} arquivos removidos",
            "removed_count": removed_count,
        }
    except Exception as e:
        logger.error(f"Erro na limpeza: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Erro na limpeza de arquivos",
                "error_code": "CLEANUP_ERROR",
            },
        )
