from enum import Enum


class FontesDadosEnum(Enum):
    COMDINHEIRO_API = "ComDinheiroAPI"
    DEPENDENCIAS_EXTERNAS = "DependenciasExternas"


class FerramentaExtracaoEnum(Enum):
    DOCLING = "docling"
    PYPDF = "pypdf"
    DOCX2TXT = "docx2txt"
    LLMWHISPERER = "llmwhisperer"


class TipoExtracaoEnum(Enum):
    MARKDOWN = "markdown"
    DADOS_BRUTOS = "dados-brutos"
    IMAGENS = "imagens"
