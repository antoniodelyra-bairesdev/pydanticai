import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from logger import leitor_logger as logger
from unstract.llmwhisperer import LLMWhispererClientV2
from unstract.llmwhisperer.client_v2 import LLMWhispererClientException

from ..base import DocumentExtractor
from ..exceptions import DocumentExtractionException, FileNotFoundException


class PDFLLMWhispererExtractor(DocumentExtractor):
    """
    Extrator PDF usando LLMWhisperer - extração avançada com IA.
    Retorna apenas o texto extraído.
    """

    def __init__(self):
        self.client = LLMWhispererClientV2()

    @property
    def name(self) -> str:
        return "llmwhisperer_pdf"

    @property
    def supported_extensions(self) -> list[str]:
        return ["pdf"]

    def extract_raw_data(self, file_path: Path) -> str:
        """
        Extrai texto bruto de um PDF usando LLMWhisperer.

        Args:
            file_path (Path): Caminho para o arquivo PDF

        Returns:
            str: Texto extraído do PDF

        Raises:
            FileNotFoundException: Se o arquivo não for encontrado
            DocumentExtractionException: Se houver erro na extração
        """
        if not file_path.exists():
            raise FileNotFoundException(f"Arquivo não encontrado: {file_path}")

        try:
            result = self.client.whisper(
                file_path=str(file_path),
                wait_for_completion=True
            )

            return result["extraction"]["result_text"]

        except LLMWhispererClientException as e:
            logger.error("Erro na extração LLMWhisperer PDF: {}", str(e))
            raise DocumentExtractionException(f"Erro ao extrair dados do PDF com LLMWhisperer: {str(e)}")
        except Exception as e:
            logger.error("Erro inesperado na extração PDF: {}", str(e))
            raise DocumentExtractionException(f"Erro inesperado na extração do PDF: {str(e)}")

    def extract_to_markdown(self, file_path: Path) -> str:
        """
        Extrai e converte PDF para markdown usando LLMWhisperer.
        Como LLMWhisperer retorna texto puro, retornamos o mesmo resultado de extract_raw_data.

        Args:
            file_path (Path): Caminho para o arquivo PDF

        Returns:
            str: Conteúdo do PDF (mesmo que extract_raw_data)

        Raises:
            FileNotFoundException: Se o arquivo não for encontrado
            DocumentExtractionException: Se houver erro na extração
        """
        # LLMWhisperer extrai texto puro, então usamos o mesmo método
        return self.extract_raw_data(file_path)

    def extract_image_data(self, file_path: Path) -> str:
        """
        Extrai texto de imagens em um PDF usando LLMWhisperer.
        LLMWhisperer processa automaticamente imagens e texto, então retornamos o mesmo resultado.

        Args:
            file_path (Path): Caminho para o arquivo PDF

        Returns:
            str: Texto extraído do PDF (incluindo texto de imagens)

        Raises:
            FileNotFoundException: Se o arquivo não for encontrado
            DocumentExtractionException: Se houver erro na extração
        """
        # LLMWhisperer processa automaticamente imagens e texto
        return self.extract_raw_data(file_path)


class DOCXLLMWhispererExtractor(DocumentExtractor):
    """
    Extrator DOCX usando LLMWhisperer - extração avançada com IA.
    Retorna apenas o texto extraído.
    """

    def __init__(self):
        self.client = LLMWhispererClientV2()

    @property
    def name(self) -> str:
        return "llmwhisperer_docx"

    @property
    def supported_extensions(self) -> list[str]:
        return ["docx"]

    def extract_raw_data(self, file_path: Path) -> str:
        """
        Extrai texto bruto de um DOCX usando LLMWhisperer.

        Args:
            file_path (Path): Caminho para o arquivo DOCX

        Returns:
            str: Texto extraído do DOCX

        Raises:
            FileNotFoundException: Se o arquivo não for encontrado
            DocumentExtractionException: Se houver erro na extração
        """
        if not file_path.exists():
            raise FileNotFoundException(f"Arquivo não encontrado: {file_path}")

        try:
            result = self.client.whisper(
                file_path=str(file_path),
                wait_for_completion=True
            )

            return result["extraction"]["result_text"]

        except LLMWhispererClientException as e:
            logger.error("Erro na extração LLMWhisperer DOCX: {}", str(e))
            raise DocumentExtractionException(f"Erro ao extrair dados do DOCX com LLMWhisperer: {str(e)}")
        except Exception as e:
            logger.error("Erro inesperado na extração DOCX: {}", str(e))
            raise DocumentExtractionException(f"Erro inesperado na extração do DOCX: {str(e)}")

    def extract_to_markdown(self, file_path: Path) -> str:
        """
        Extrai e converte DOCX para markdown usando LLMWhisperer.
        Como LLMWhisperer retorna texto puro, retornamos o mesmo resultado de extract_raw_data.

        Args:
            file_path (Path): Caminho para o arquivo DOCX

        Returns:
            str: Conteúdo do DOCX (mesmo que extract_raw_data)

        Raises:
            FileNotFoundException: Se o arquivo não for encontrado
            DocumentExtractionException: Se houver erro na extração
        """
        # LLMWhisperer extrai texto puro, então usamos o mesmo método
        return self.extract_raw_data(file_path)

    def extract_image_data(self, file_path: Path) -> str:
        """
        Extrai texto de imagens em um DOCX usando LLMWhisperer.
        LLMWhisperer processa automaticamente imagens e texto, então retornamos o mesmo resultado.

        Args:
            file_path (Path): Caminho para o arquivo DOCX

        Returns:
            str: Texto extraído do DOCX (incluindo texto de imagens)

        Raises:
            FileNotFoundException: Se o arquivo não for encontrado
            DocumentExtractionException: Se houver erro na extração
        """
        # LLMWhisperer processa automaticamente imagens e texto
        return self.extract_raw_data(file_path)
