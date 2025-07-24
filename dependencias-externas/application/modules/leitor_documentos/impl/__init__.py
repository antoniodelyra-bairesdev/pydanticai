# Import extractors to register them with autoregistry
from .docling import PDFDoclingExtractor, DOCXDoclingExtractor
from .pypdf import PDFPypdfExtractor
from .docx2txt import DOCXDocx2TxtExtractor

__all__ = [
    "PDFDoclingExtractor",
    "DOCXDoclingExtractor", 
    "PDFPypdfExtractor",
    "DOCXDocx2TxtExtractor"
]
