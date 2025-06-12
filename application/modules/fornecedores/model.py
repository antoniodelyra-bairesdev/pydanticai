from config.database import Model, SchemaIcatu

from sqlalchemy import INTEGER, TEXT
from sqlalchemy.orm import Mapped, mapped_column


class Fornecedor(Model, SchemaIcatu):
    __tablename__ = "fornecedores"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    nome: Mapped[str] = mapped_column(TEXT, nullable=False)
