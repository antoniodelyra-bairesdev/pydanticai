import sys
from pathlib import Path

from loguru import logger

# Configurações do logger
LOG_LEVEL = "INFO"
LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
)

# Remove o handler padrão do loguru
logger.remove()

# Adiciona handler customizado para console
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# Cria diretório de logs se não existir
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Adiciona handler para arquivo
logger.add(
    "logs/dependencias-externas.log",
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    encoding="utf-8",
)


def get_logger(name: str | None = None):
    """
    Retorna um logger configurado com o nome do módulo.

    Args:
        name (str | None): Nome do módulo para identificar no log

    Returns:
        Logger: Logger configurado com o nome do módulo
    """
    if name:
        return logger.bind(name=name)
    return logger


# Logger padrão para este módulo
app_logger = get_logger("dependencias-externas")

# Logger específico para o módulo leitor_documentos
leitor_logger = get_logger("leitor_documentos")
