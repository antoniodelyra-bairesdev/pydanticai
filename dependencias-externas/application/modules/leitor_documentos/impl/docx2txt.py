import docx2txt
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from logger import leitor_logger as logger

from ..base import DocumentExtractor
from ..exceptions import DocumentExtractionException, FileNotFoundException


class DOCXDocx2TxtExtractor(DocumentExtractor):
    """
    Extrator DOCX usando docx2txt - fallback rápido e leve.
    Retorna apenas o texto extraído.
    """
    @property
    def name(self) -> str:
        return "docx2txt"

    @property
    def supported_extensions(self) -> list[str]:
        return ["docx"]

    def extract_raw_data(self, file_path: Path) -> str:
        """
        Extrai texto bruto de um DOCX usando docx2txt.

        Args:
            file_path (str): Caminho para o arquivo DOCX

        Returns:
            str: Texto extraído do DOCX

        Raises:
            FileNotFoundException: Se o arquivo não for encontrado
            DocumentExtractionException: Se houver erro na extração
        """
        logger.info("Iniciando extração de texto bruto: {}", file_path)

        if not file_path.exists():
            raise FileNotFoundException(f"Arquivo não encontrado: {file_path}")

        try:
            text = docx2txt.process(str(file_path))
            logger.info(
                "Extração concluída. Tamanho do texto: {} caracteres", len(text or "")
            )
            return text or ""

        except Exception as e:
            logger.error("Erro na extração: {}", str(e))
            raise DocumentExtractionException(
                f"Erro ao extrair dados do DOCX: {str(e)}"
            )

    def extract_to_markdown(self, file_path: Path) -> str:
        """
        Conversão para markdown não suportada pelo Docx2TxtExtractor.
        """
        raise NotImplementedError(
            "Conversão para markdown não suportada pelo Docx2TxtExtractor."
        )

    def extract_image_data(self, file_path: Path) -> str:
        """
        Extração de imagens não suportada pelo Docx2TxtExtractor.
        """
        raise NotImplementedError(
            "Extração de imagens não suportada pelo Docx2TxtExtractor."
        )
