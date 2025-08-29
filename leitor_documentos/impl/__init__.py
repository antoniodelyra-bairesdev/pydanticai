# Import extractors to register them with autoregistry
from .docling import DOCXDoclingExtractor, PDFDoclingExtractor
from .docx2txt import DOCXDocx2TxtExtractor
from .llmwhisperer import DOCXLLMWhispererExtractor, PDFLLMWhispererExtractor
from .pypdf import PDFPypdfExtractor

__all__ = [
    "PDFDoclingExtractor",
    "DOCXDoclingExtractor",
    "PDFPypdfExtractor",
    "DOCXDocx2TxtExtractor",
    "PDFLLMWhispererExtractor",
    "DOCXLLMWhispererExtractor",
]
