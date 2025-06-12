from sqlalchemy import INTEGER, TEXT
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Model, SchemaIcatu


class Medida(Model, SchemaIcatu):
    __tablename__ = "medidas"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    nome: Mapped[str] = mapped_column(TEXT, nullable=False)
    descricao: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    abreviacao: Mapped[str | None] = mapped_column(TEXT, nullable=True)
