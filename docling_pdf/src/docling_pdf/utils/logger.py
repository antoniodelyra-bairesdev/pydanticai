import sys

from loguru import logger

from docling_pdf.config import settings

# Remove o handler padrão do loguru
logger.remove()

# Adiciona handler customizado baseado nas configurações
logger.add(
    sys.stdout,
    format=settings.log_format,
    level=settings.log_level,
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# Adiciona handler para arquivo
logger.add(
    "logs/app.log",
    format=settings.log_format,
    level=settings.log_level,
    rotation="10 MB",
    retention="7 days",
    compression="zip",
)


def get_logger(name: str | None = None):
    """Retorna um logger configurado com o nome do módulo"""
    if name:
        return logger.bind(name=name)
    return logger


# Logger padrão para este módulo
app_logger = get_logger("docling_pdf")
