import time
import uuid
from pathlib import Path

from fastapi import UploadFile
from loguru import logger

from ..config import settings


class FileService:
    def __init__(self) -> None:
        self.temp_dir = Path(settings.temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload_file(self, file: UploadFile) -> str:
        """Salva arquivo temporariamente e retorna o caminho."""
        try:
            # Gerar nome único para o arquivo
            if not file.filename:
                raise ValueError("Nome do arquivo não fornecido")
            file_extension = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = self.temp_dir / unique_filename

            # Salvar arquivo
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)

            logger.info(f"Arquivo salvo temporariamente: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"Erro ao salvar arquivo: {e}")
            raise

    def cleanup_temp_file(self, file_path: str | Path) -> bool:
        """Remove arquivo temporário."""
        try:
            file_path = Path(file_path)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Arquivo temporário removido: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao remover arquivo temporário: {e}")
            return False

    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """Remove arquivos temporários antigos."""
        removed_count = 0
        current_time = time.time()

        try:
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (max_age_hours * 3600):
                        file_path.unlink()
                        removed_count += 1
                        logger.info(f"Arquivo antigo removido: {file_path}")

            return removed_count
        except Exception as e:
            logger.error(f"Erro na limpeza de arquivos: {e}")
            return 0
