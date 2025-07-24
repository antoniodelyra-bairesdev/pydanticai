import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import UploadFile
from logger import leitor_logger as logger

from .base import DocumentExtractor
from .exceptions import DocumentExtractionException, ExtractorNotFoundException
from .schema import ConversionMetadata, ExtractionResult
from .utils import format_duration, format_file_size, get_file_extension

# Import extractors to ensure they are registered
from .impl import *


class LeitorDocumentosService:
    """
    Serviço principal que gerencia todos os extractors de documentos.

    Responsável por orquestrar a extração de conteúdo de diferentes formatos
    de arquivo (PDF, DOCX) usando extractors específicos.
    """

    def extract_to_markdown(
        self, file_path: Path, tool: str | None = None
    ) -> dict[str, Any]:
        """
        Extrai conteúdo de um arquivo e converte para formato markdown.

        Args:
            file_path (Path): Caminho para o arquivo a ser processado
            tool (str, optional): Nome da ferramenta de extração

        Returns:
            dict: Dicionário contendo extraction_result e metadata

        Raises:
            DocumentExtractionException: Se houver erro na extração
            ExtractorNotFoundException: Se a ferramenta de extração não for encontrada
        """
        logger.info("Iniciando extração para markdown: {}", file_path.name)
        start_time = time.time()

        # Identificar extensão do arquivo e selecionar extractor
        file_extension = get_file_extension(file_path.name)
        extractor = self._get_extractor(file_extension, tool)
        logger.info("Usando extractor: {} para arquivo: {}", extractor.name, file_path)

        # Realizar extração
        content = extractor.extract_to_markdown(file_path)
        extraction_time = time.time() - start_time
        file_stats = file_path.stat()

        # Preparar resultado estruturado
        extraction_result = ExtractionResult(
            content=content,
            format="markdown",
            extractor_used=extractor.name,
        )
        metadata = ConversionMetadata(
            file_size=format_file_size(file_stats.st_size),
            extraction_time=format_duration(extraction_time),
            character_count=len(content),
            extractor_used=extractor.name,
        )

        logger.info(
            "Extração markdown concluída. Tempo: {}, Arquivo: {}, Tamanho: {} chars",
            format_duration(extraction_time),
            format_file_size(file_stats.st_size),
            len(content),
        )

        return {
            "extraction_result": extraction_result.model_dump(),
            "metadata": metadata.model_dump(),
        }

    def extract_raw_data(
        self, file_path: Path, tool: str | None = None
    ) -> dict[str, Any]:
        """
        Extrai dados brutos (texto) de um arquivo.

        Args:
            file_path (Path): Caminho para o arquivo a ser processado
            tool (str, optional): Nome da ferramenta de extração

        Returns:
            dict: Dicionário contendo extraction_result e metadata

        Raises:
            DocumentExtractionException: Se houver erro na extração
            ExtractorNotFoundException: Se o extractor preferido não for encontrado
        """
        logger.info("Iniciando extração de dados brutos: {}", file_path.name)
        start_time = time.time()

        # Identificar extensão do arquivo e selecionar extractor
        file_extension = get_file_extension(file_path.name)
        extractor = self._get_extractor(file_extension, tool)
        logger.info("Usando extractor: {} para arquivo: {}", extractor.name, file_path)

        # Realizar extração
        data = extractor.extract_raw_data(file_path)
        extraction_time = time.time() - start_time
        file_stats = file_path.stat()

        # Preparar resultado estruturado
        extraction_result = ExtractionResult(
            content=str(data),
            format="raw",
            extractor_used=extractor.name,
        )
        metadata = ConversionMetadata(
            file_size=format_file_size(file_stats.st_size),
            extraction_time=format_duration(extraction_time),
            character_count=len(str(data)),
            extractor_used=extractor.name,
        )

        logger.info(
            "Extração de dados brutos concluída. Tempo: {}, Arquivo: {}, "
            "Tamanho: {} chars",
            format_duration(extraction_time),
            format_file_size(file_stats.st_size),
            len(str(data)),
        )

        return {
            "extraction_result": extraction_result.model_dump(),
            "metadata": metadata.model_dump(),
        }

    def extract_image_data(
        self, file_path: Path, tool: str | None = None
    ) -> dict[str, Any]:
        """
        Extrai texto de imagens contidas em um documento.

        Args:
            file_path (Path): Caminho para o arquivo a ser processado
            tool (str, optional): Nome da ferramenta de extração

        Returns:
            dict: Dicionário contendo extraction_result e metadata

        Raises:
            DocumentExtractionException: Se houver erro na extração
            ExtractorNotFoundException: Se a ferramenta de extração não for encontrada
        """
        logger.info("Iniciando extração de dados de imagens: {}", file_path.name)
        start_time = time.time()

        # Identificar extensão do arquivo e selecionar extractor
        file_extension = get_file_extension(file_path.name)
        extractor = self._get_extractor(file_extension, tool)
        logger.info(
            "Usando extractor: {} para arquivo: {}", extractor.name, file_path.name
        )

        # Realizar extração de imagens
        result = extractor.extract_image_data(file_path)
        extraction_time = time.time() - start_time
        file_stats = file_path.stat()

        # Preparar resultado estruturado
        extraction_result = ExtractionResult(
            content=result,
            format="images",
            extractor_used=extractor.name,
        )
        metadata = ConversionMetadata(
            file_size=format_file_size(file_stats.st_size),
            extraction_time=format_duration(extraction_time),
            character_count=len(result),
            extractor_used=extractor.name,
        )

        logger.info(
            "Extração de imagens concluída. Tempo: {}, Arquivo: {}, Tamanho: {} chars",
            format_duration(extraction_time),
            format_file_size(file_stats.st_size),
            len(result),
        )

        return {
            "extraction_result": extraction_result.model_dump(),
            "metadata": metadata.model_dump(),
        }

    def _get_extractor(
        self, file_extension: str, tool: str | None = None
    ) -> DocumentExtractor:
        """
        Obtém o melhor extractor para o formato especificado.

        Args:
            file_extension (str): Extensão do arquivo (ex: 'pdf', 'docx')
            tool (str, optional): Nome da ferramenta de extração

        Returns:
            DocumentExtractor: Instância do extractor selecionado

        Raises:
            ExtractorNotFoundException: Se a ferramenta de extração não for encontrada
        """
        # Se tem preferência específica, tentar usar o registry
        if tool:
            try:
                return DocumentExtractor.get_extractor(file_extension, tool)
            except KeyError:
                raise ExtractorNotFoundException(f"Extractor '{tool}' não encontrado")

        # Sempre usar docling como padrão
        return DocumentExtractor.get_extractor(file_extension)

    def get_extractor_names_for_format(self, file_extension: str) -> dict[str, list[dict]]:
        """
        Retorna nomes dos extractors disponíveis para um formato específico.

        Args:
            file_extension (str): Extensão do arquivo

        Returns:
            dict[str, list[dict]]: Dicionário com formatos e extractors disponíveis
        """
        extractors_info = []

        # Buscar extractors que suportam a extensão
        for extractor_class in DocumentExtractor.__subclasses__():
            if file_extension in extractor_class().supported_extensions:
                extractor = extractor_class()
                extractors_info.append({
                    "name": extractor.name,
                    "extensions": extractor.supported_extensions
                })

        return {file_extension: extractors_info}


class FileService:
    """
    Gerenciamento de arquivos temporários e uploads.

    Responsável por salvar, limpar e gerenciar arquivos temporários
    durante o processo de extração.
    """

    def __init__(self):
        """Inicializa o serviço criando o diretório temporário."""
        self.temp_dir = Path("files/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload_file(self, file: UploadFile) -> Path:
        """
        Salva arquivo temporariamente e retorna o caminho.

        Args:
            file (UploadFile): Arquivo enviado via upload

        Returns:
            str: Caminho completo do arquivo salvo

        Raises:
            DocumentExtractionException: Se houver erro ao salvar o arquivo
        """
        try:
            # Validar se o arquivo tem nome
            if not file.filename:
                raise ValueError("Nome do arquivo não fornecido")

            # Gerar nome único para o arquivo com timestamp
            file_extension = f".{get_file_extension(file.filename)}"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{uuid.uuid4()}{file_extension}"
            file_path = self.temp_dir / unique_filename

            # Salvar arquivo no sistema
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)

            logger.info(
                "Arquivo salvo temporariamente: {} (Tamanho: {})",
                file_path,
                format_file_size(len(content)),
            )
            return file_path

        except Exception as e:
            logger.error("Erro ao salvar arquivo: {}", str(e))
            raise DocumentExtractionException(f"Erro ao salvar arquivo: {str(e)}")

    def cleanup_temp_file(self, file_path: Path) -> bool:
        """
        Remove arquivo temporário específico.

        Args:
            file_path (Path): Caminho do arquivo a ser removido

        Returns:
            bool: True se o arquivo foi removido, False caso contrário
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info("Arquivo temporário removido: {}", file_path)
                return True
            return False
        except Exception as e:
            logger.error("Erro ao remover arquivo temporário: {}", str(e))
            return False

    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Remove arquivos temporários antigos.

        Args:
            max_age_hours (int): Idade máxima em horas para manter arquivos

        Returns:
            int: Número de arquivos removidos
        """
        removed_count = 0
        current_time = time.time()

        try:
            # Iterar sobre todos os arquivos no diretório temporário
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (max_age_hours * 3600):
                        file_path.unlink()
                        removed_count += 1

            if removed_count > 0:
                logger.info("Removidos {} arquivos temporários antigos", removed_count)

            return removed_count
        except Exception as e:
            logger.error("Erro ao limpar arquivos antigos: {}", str(e))
            return 0
