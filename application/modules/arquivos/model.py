from typing import Literal
from sqlalchemy import TEXT
from config.database import Model, SchemaSistema
from sqlalchemy.orm import Mapped, mapped_column


class Arquivo(Model, SchemaSistema):
    __tablename__ = "arquivos"

    id: Mapped[str] = mapped_column(TEXT, primary_key=True)
    provedor: Mapped[Literal["base64", "filesystem", "azure-blob-storage"]] = (
        mapped_column(TEXT)
    )
    conteudo: Mapped[str] = mapped_column(TEXT)
    nome: Mapped[str] = mapped_column(TEXT)
    extensao: Mapped[str] = mapped_column(TEXT)
