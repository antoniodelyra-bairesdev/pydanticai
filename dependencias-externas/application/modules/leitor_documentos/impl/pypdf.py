import sys
from pathlib import Path

import pypdf

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from logger import leitor_logger as logger
from pypdf.errors import PyPdfError

from ..base import DocumentExtractor
from ..exceptions import DocumentExtractionException, FileNotFoundException


class PDFPypdfExtractor(DocumentExtractor):
    """
    Extrator PDF usando pypdf - alternativo ao Docling.
    Retorna apenas o texto extraído.
    """

    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return "pypdf"

    @property
    def supported_extensions(self) -> list[str]:
        return ["pdf"]

    def extract_raw_data(self, file_path: Path) -> str:
        """
        Extrai texto bruto de um PDF usando pypdf.

        Args:
            file_path (str): Caminho para o arquivo PDF

        Returns:
            str: Texto extraído do PDF

        Raises:
            FileNotFoundException: Se o arquivo não for encontrado
            DocumentExtractionException: Se houver erro na extração
        """
        logger.info("Iniciando extração de texto bruto: {}", file_path)

        if not file_path.exists():
            raise FileNotFoundException(f"Arquivo não encontrado: {file_path}")

        try:
            with open(file_path, "rb") as f:
                pdf_reader = pypdf.PdfReader(f)
                text = "".join(
                    page.extract_text() or "" for page in pdf_reader.pages
                ).strip()
                logger.info(
                    "Extração concluída. Tamanho do texto: {} caracteres", len(text)
                )
                return text

        except PyPdfError as e:
            logger.error("Erro na extração: {}", str(e))
            raise DocumentExtractionException(f"Erro ao ler PDF: {str(e)}") from e

        except Exception as e:
            logger.error("Erro na extração: {}", str(e))
            raise DocumentExtractionException(
                f"Erro ao extrair dados do PDF: {str(e)}"
            ) from e

    def extract_to_markdown(self, file_path: Path) -> str:
        """
        Conversão para markdown não suportada pelo PypdfExtractor.
        """
        raise NotImplementedError(
            "Conversão para markdown não suportada pelo PypdfExtractor."
        )

    def extract_image_data(self, file_path: Path) -> str:
        """
        Extração de imagens não suportada pelo PypdfExtractor.
        """
        raise NotImplementedError(
            "Extração de imagens não suportada pelo PypdfExtractor."
        )
