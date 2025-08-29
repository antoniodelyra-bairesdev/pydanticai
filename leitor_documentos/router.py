import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, Depends, File, Query, UploadFile
from logger import leitor_logger as logger

from .schema import (
    CleanupResponse,
    ConversionMetadata,
    DocumentExtractionResponse,
    FerramentaExtracaoEnum,
    SupportedFormatsResponse,
)
from .service import FileService, LeitorDocumentosService
from .utils import sanitize_filename
from .validators import validate_document_file, validate_file_size

router = APIRouter(prefix="/leitor-documentos", tags=["Leitor de Documentos"])


# Context Manager para limpeza automática de arquivos
@asynccontextmanager
async def temp_file_manager(
    file: UploadFile, file_service: FileService
) -> AsyncGenerator[Path, None]:
    """
    Context manager que garante limpeza de arquivo temporário mesmo em caso de erro.

    Args:
        file: Arquivo enviado via upload
        file_service: Serviço para gerenciar arquivos

    Yields:
        Path: Caminho do arquivo temporário salvo

    Ensures:
        Arquivo temporário é sempre removido, mesmo em caso de exceção
    """
    temp_file_path = None
    try:
        # Validar e salvar arquivo
        validate_document_file(file)
        validate_file_size(file)

        temp_file_path = await file_service.save_upload_file(file)
        logger.info("Arquivo salvo temporariamente: {}", temp_file_path)

        yield temp_file_path

    finally:
        # Garantir limpeza mesmo em caso de erro
        if temp_file_path and temp_file_path.exists():
            file_service.cleanup_temp_file(temp_file_path)


# Factory Functions
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


@router.post("/extrair-markdown")
async def extrair_para_markdown(
    file: UploadFile = File(...),
    ferramenta_extracao: FerramentaExtracaoEnum = Query(None),
    service: LeitorDocumentosService = Depends(get_document_service),
    file_service: FileService = Depends(get_file_service),
) -> DocumentExtractionResponse:
    """
    # Extração para Markdown

    Converte documentos em formato markdown estruturado, preservando formatação e hierarquia.

    ## Funcionalidades
    - Extrai texto com formatação (títulos, listas, tabelas)
    - Preserva estrutura hierárquica do documento
    - Suporta múltiplos formatos de entrada (PDF, DOCX, etc.)

    ## Parâmetros
    - `file`: Arquivo para processar
    - `ferramenta_extracao`: Ferramenta específica (opcional)

    ## Retorna
    Conteúdo em markdown + metadados de processamento
    """
    logger.info("Iniciando extração para markdown: {}", sanitize_filename(file.filename))

    async with temp_file_manager(file, file_service) as temp_file_path:
        # Realizar extração
        result = service.extract_to_markdown(
            file_path=temp_file_path,
            tool=ferramenta_extracao.value if ferramenta_extracao else None,
        )

        # Preparar resposta
        response = DocumentExtractionResponse(
            success=True,
            data=result.extraction_result,
            metadata=ConversionMetadata(
                **{**result.metadata.model_dump(), "filename": sanitize_filename(file.filename)}
            ),
        )

        logger.info(
            "Extração markdown concluída com sucesso: {}", sanitize_filename(file.filename)
        )
        return response


@router.post("/extrair-dados-brutos")
async def extrair_dados_brutos(
    file: UploadFile = File(...),
    ferramenta_extracao: FerramentaExtracaoEnum = Query(None),
    service: LeitorDocumentosService = Depends(get_document_service),
    file_service: FileService = Depends(get_file_service),
) -> DocumentExtractionResponse:
    """
    # Extração de Dados Brutos

    Extrai texto puro de documentos, sem formatação ou estrutura.

    ## Funcionalidades
    - Extrai todo o texto do documento
    - Remove formatação e elementos visuais
    - Ideal para processamento de texto (NLP, análise, etc.)

    ## Parâmetros
    - `file`: Arquivo para processar
    - `ferramenta_extracao`: Ferramenta específica (opcional)

    ## Retorna
    Texto bruto + metadados de processamento
    """
    logger.info("Iniciando extração de dados brutos: {}", sanitize_filename(file.filename))

    async with temp_file_manager(file, file_service) as temp_file_path:
        # Realizar extração
        result = service.extract_raw_data(
            file_path=temp_file_path,
            tool=ferramenta_extracao.value if ferramenta_extracao else None,
        )

        # Preparar resposta
        response = DocumentExtractionResponse(
            success=True,
            data=result.extraction_result,
            metadata=ConversionMetadata(
                **{**result.metadata.model_dump(), "filename": sanitize_filename(file.filename)}
            ),
        )

        logger.info(
            "Extração de dados brutos concluída com sucesso: {}", sanitize_filename(file.filename)
        )
        return response


@router.post("/extrair-dados-imagens")
async def extrair_imagens(
    file: UploadFile = File(...),
    ferramenta_extracao: FerramentaExtracaoEnum = Query(None),
    service: LeitorDocumentosService = Depends(get_document_service),
    file_service: FileService = Depends(get_file_service),
) -> DocumentExtractionResponse:
    """
    # Extração de Texto de Imagens

    Extrai texto de imagens, gráficos e elementos visuais em documentos.

    ## Funcionalidades
    - OCR (Reconhecimento Óptico de Caracteres)
    - Extrai texto de gráficos, tabelas e diagramas
    - Suporta múltiplos idiomas
    - Preserva posicionamento do texto

    ## Parâmetros
    - `file`: Arquivo para processar
    - `ferramenta_extracao`: Ferramenta específica (opcional)

    ## Retorna
    Texto extraído de imagens + metadados de processamento
    """
    logger.info("Iniciando extração de dados de imagens: {}", sanitize_filename(file.filename))

    async with temp_file_manager(file, file_service) as temp_file_path:
        # Realizar extração de imagens
        result = service.extract_image_data(
            file_path=temp_file_path,
            tool=ferramenta_extracao.value if ferramenta_extracao else None,
        )

        # Preparar resposta
        response = DocumentExtractionResponse(
            success=True,
            data=result.extraction_result,
            metadata=ConversionMetadata(
                **{**result.metadata.model_dump(), "filename": sanitize_filename(file.filename)}
            ),
        )

        logger.info(
            "Extração de imagens concluída com sucesso: {}", sanitize_filename(file.filename)
        )
        return response


@router.get("/formatos-suportados")
async def listar_formatos_suportados(
    extensao: str = Query("pdf"),
    service: LeitorDocumentosService = Depends(get_document_service),
) -> SupportedFormatsResponse:
    """
    # Formatos Suportados

    Lista formatos de arquivo e ferramentas de extração disponíveis.

    ## Funcionalidades
    - Consulta formatos suportados por extensão
    - Lista ferramentas de extração disponíveis
    - Informa capacidades de cada extractor

    ## Parâmetros
    - `extensao`: Extensão do arquivo (padrão: "pdf")

    ## Retorna
    Lista de formatos e extractors disponíveis
    """
    logger.info("Solicitando lista de formatos suportados")

    formats = service.get_extractor_names_for_format(extensao)
    logger.info("Formatos suportados obtidos com sucesso")
    return SupportedFormatsResponse(success=True, formats=formats)


@router.post("/limpeza")
async def limpar_arquivos_temporarios(
    max_age_hours: int = Query(24, ge=1, le=168),
    file_service: FileService = Depends(get_file_service),
) -> CleanupResponse:
    """
    # Limpeza de Arquivos Temporários

    Remove arquivos temporários antigos para liberar espaço em disco.

    ## Funcionalidades
    - Remove arquivos com mais de X horas
    - Limpeza automática e segura
    - Relatório de arquivos removidos

    ## Parâmetros
    - `max_age_hours`: Idade máxima em horas (1-168, padrão: 24)

    ## Retorna
    Quantidade de arquivos removidos + relatório
    """
    logger.info("Iniciando limpeza de arquivos temporários (max_age: {}h)", max_age_hours)

    removed_count = file_service.cleanup_old_files(max_age_hours)
    logger.info("Limpeza concluída. {} arquivo(s) removido(s)", removed_count)

    return CleanupResponse(
        success=True,
        message=f"{removed_count} arquivo(s) removido(s).",
        removed_count=removed_count,
    )
