import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

from modules.leitor_documentos.impl.docling import (
    DOCXDoclingExtractor,
    PDFDoclingExtractor,
)
from modules.leitor_documentos.impl.docx2txt import DOCXDocx2TxtExtractor
from modules.leitor_documentos.impl.pypdf import PDFPypdfExtractor


class TestDocumentExtractorRegistry:
    """Testes unitários isolados do sistema de registry de extractors"""

    def test_extractor_properties(self):
        """Testa propriedades básicas dos extractors registrados"""
        # PDF Docling
        pdf_docling = PDFDoclingExtractor()
        assert pdf_docling.name == "docling_pdf"
        assert "pdf" in pdf_docling.supported_extensions

        # DOCX Docling
        docx_docling = DOCXDoclingExtractor()
        assert docx_docling.name == "docling_docx"
        assert "docx" in docx_docling.supported_extensions

        # PDF pypdf
        pdf_pypdf = PDFPypdfExtractor()
        assert pdf_pypdf.name == "pypdf"
        assert "pdf" in pdf_pypdf.supported_extensions

        # DOCX docx2txt
        docx_docx2txt = DOCXDocx2TxtExtractor()
        assert docx_docx2txt.name == "docx2txt"
        assert "docx" in docx_docx2txt.supported_extensions
