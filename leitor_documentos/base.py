from abc import abstractmethod
from pathlib import Path
from typing import cast

from autoregistry import Registry


class DocumentExtractor(Registry, suffix="Extractor"):
    """Classe base para todos os extractors de documentos"""

    @abstractmethod
    def extract_raw_data(self, file_path: Path) -> str:
        """Extrai dados brutos sem processamento"""
        raise NotImplementedError()

    @abstractmethod
    def extract_to_markdown(self, file_path: Path) -> str:
        """Extrai e converte para markdown"""
        raise NotImplementedError()

    @abstractmethod
    def extract_image_data(self, file_path: Path) -> str:
        """Extrai dados de imagens do documento"""
        raise NotImplementedError()

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome único do extractor"""
        raise NotImplementedError()

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """Lista de extensões suportadas pelo extractor"""
        raise NotImplementedError()

    @classmethod
    def get_extractor(
        cls, extension: str, tool: str = "docling"
    ) -> "DocumentExtractor":
        """
        Obtém o extractor baseado na extensão e ferramenta.
        A ferramenta padrão é 'docling'.
        """
        key = f"{extension}{tool}"
        return cast(DocumentExtractor, cls[key]())
