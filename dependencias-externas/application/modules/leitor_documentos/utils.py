from pathlib import Path

# Constantes para formatação
KB_SIZE = 1024
MB_SIZE = 1024 * 1024
MINUTE_SECONDS = 60


def format_file_size(size_bytes: int) -> str:
    """
    Formata tamanho de arquivo em bytes para uma representação legível.

    Args:
        size_bytes (int): Tamanho do arquivo em bytes

    Returns:
        str: Tamanho formatado (ex: "1.5 MB", "256 KB", "512 B")
    """
    if size_bytes < KB_SIZE:
        return f"{size_bytes} B"
    elif size_bytes < MB_SIZE:
        return f"{size_bytes / KB_SIZE:.1f} KB"
    else:
        return f"{size_bytes / MB_SIZE:.1f} MB"


def format_duration(seconds: float) -> str:
    """
    Formata duração em segundos para uma representação legível.

    Args:
        seconds (float): Duração em segundos

    Returns:
        str: Duração formatada (ex: "150ms", "2.5s", "1m 30.5s")
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < MINUTE_SECONDS:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // MINUTE_SECONDS)
        remaining_seconds = seconds % MINUTE_SECONDS
        return f"{minutes}m {remaining_seconds:.1f}s"


def sanitize_filename(filename: str) -> str:
    """
    Remove caracteres perigosos do nome do arquivo para evitar path traversal.

    Args:
        filename (str): Nome do arquivo original

    Returns:
        str: Nome do arquivo sanitizado, seguro para uso em sistema de arquivos
    """
    return Path(filename).name.replace("..", "").replace("/", "_").replace("\\", "_")


def get_file_extension(filename: str) -> str:
    """
    Extrai a extensão do arquivo a partir do nome, convertendo para lowercase.

    Args:
        filename (str): Nome do arquivo (ex: "documento.PDF", "relatorio.docx")

    Returns:
        str: Extensão do arquivo sem o ponto (ex: "pdf", "docx")
    """
    return Path(filename).suffix.lower().lstrip(".")
