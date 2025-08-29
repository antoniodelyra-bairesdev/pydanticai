import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from docling.document_converter import DocumentConverter
from logger import leitor_logger as logger

from ..base import DocumentExtractor
from ..exceptions import DocumentExtractionException, FileNotFoundException


class PDFDoclingExtractor(DocumentExtractor):
    """
    Extrator PDF usando Docling - melhor qualidade.
    Retorna apenas o texto extraído.
    """

    def __init__(self):
        self.converter = DocumentConverter()

    @property
    def name(self) -> str:
        return "docling_pdf"

    @property
    def supported_extensions(self) -> list[str]:
        return ["pdf"]

    def extract_raw_data(self, file_path: Path) -> str:
        """
        Extrai texto bruto de um PDF usando Docling.

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
            conv_result = self.converter.convert(str(file_path))
            text = ("\n").join(t.text for t in conv_result.document.texts)
            return text

        except Exception as e:
            logger.error("Erro na extração: {}", str(e))
            raise DocumentExtractionException(f"Erro ao extrair dados do PDF: {str(e)}")

    def extract_to_markdown(self, file_path: Path) -> str:
        """
        Extrai e converte PDF para markdown usando Docling.

        Args:
            file_path (Path): Caminho para o arquivo PDF

        Returns:
            str: Conteúdo do PDF convertido para markdown

        Raises:
            FileNotFoundException: Se o arquivo não for encontrado
            DocumentExtractionException: Se houver erro na extração
        """
        if not file_path.exists():
            raise FileNotFoundException(f"Arquivo não encontrado: {file_path}")

        try:
            conv_result = self.converter.convert(str(file_path))
            markdown = conv_result.document.export_to_markdown()
            return markdown

        except Exception as e:
            logger.error("Erro na extração markdown: {}", str(e))
            raise DocumentExtractionException(f"Erro ao extrair dados do PDF: {str(e)}")

    def extract_image_data(self, file_path: Path) -> str:
        """
        Extrai texto de imagens em um PDF usando Docling.

        Args:
            file_path (Path): Caminho para o arquivo PDF

        Returns:
            str: Texto extraído das imagens do PDF

        Raises:
            FileNotFoundException: Se o arquivo não for encontrado
            DocumentExtractionException: Se houver erro na extração
        """
        try:
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.document_converter import DocumentConverter, PdfFormatOption
            from docling_core.types.doc import TextItem

            if not file_path.exists():
                raise FileNotFoundException(f"Arquivo não encontrado: {file_path}")

            pipeline_options = PdfPipelineOptions()
            pipeline_options.images_scale = 2
            pipeline_options.generate_page_images = True

            doc_converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
            conv_res = doc_converter.convert(str(file_path))
            doc = conv_res.document

            text = []
            for picture in getattr(doc, "pictures", []):
                for item, level in doc.iterate_items(
                    root=picture, traverse_pictures=True
                ):
                    if isinstance(item, TextItem):
                        text.append(item.text)

            extracted_text = "\n".join(text)
            return extracted_text

        except Exception as e:
            logger.error("Erro na extração de imagens: {}", str(e))
            raise DocumentExtractionException(
                f"Erro ao extrair dados de imagens do PDF: {str(e)}"
            )


class DOCXDoclingExtractor(DocumentExtractor):
    """
    Extrator DOCX usando Docling.
    Retorna apenas o texto extraído.
    """

    def __init__(self):
        self.converter = DocumentConverter()

    @property
    def name(self) -> str:
        return "docling_docx"

    @property
    def supported_extensions(self) -> list[str]:
        return ["docx"]

    def extract_raw_data(self, file_path: Path) -> str:
        """
        Extrai texto bruto de um DOCX usando Docling.

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
            conv_result = self.converter.convert(str(file_path))
            text = ("\n").join(t.text for t in conv_result.document.texts)
            return text

        except Exception as e:
            logger.error("Erro na extração: {}", str(e))
            raise DocumentExtractionException(
                f"Erro ao extrair dados do DOCX: {str(e)}"
            )

    def extract_to_markdown(self, file_path: Path) -> str:
        """
        Extrai e converte DOCX para markdown usando Docling.

        Args:
            file_path (Path): Caminho para o arquivo DOCX

        Returns:
            str: Conteúdo do DOCX convertido para markdown

        Raises:
            FileNotFoundException: Se o arquivo não for encontrado
            DocumentExtractionException: Se houver erro na extração
        """
        if not file_path.exists():
            raise FileNotFoundException(f"Arquivo não encontrado: {file_path}")

        try:
            conv_result = self.converter.convert(str(file_path))
            markdown = conv_result.document.export_to_markdown()
            return markdown

        except Exception as e:
            logger.error("Erro na extração markdown: {}", str(e))
            raise DocumentExtractionException(
                f"Erro ao extrair dados do DOCX: {str(e)}"
            )

    def extract_image_data(self, file_path: Path) -> str:
        """
        Extrai texto de imagens em um DOCX usando Docling.

        Args:
            file_path (Path): Caminho para o arquivo DOCX

        Returns:
            str: Texto extraído das imagens do DOCX

        Raises:
            FileNotFoundException: Se o arquivo não for encontrado
            DocumentExtractionException: Se houver erro na extração
        """
        try:
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.document_converter import DocumentConverter, PdfFormatOption
            from docling_core.types.doc import TextItem

            if not file_path.exists():
                raise FileNotFoundException(f"Arquivo não encontrado: {file_path}")

            pipeline_options = PdfPipelineOptions()
            pipeline_options.images_scale = 2
            pipeline_options.generate_page_images = True

            doc_converter = DocumentConverter(
                format_options={
                    InputFormat.DOCX: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
            conv_res = doc_converter.convert(str(file_path))
            doc = conv_res.document

            text = []
            for picture in getattr(doc, "pictures", []):
                for item, level in doc.iterate_items(
                    root=picture, traverse_pictures=True
                ):
                    if isinstance(item, TextItem):
                        text.append(item.text)

            extracted_text = "\n".join(text)
            return extracted_text

        except Exception as e:
            logger.error("Erro na extração de imagens: {}", str(e))
            raise DocumentExtractionException(
                f"Erro ao extrair dados de imagens do DOCX: {str(e)}"
            )
