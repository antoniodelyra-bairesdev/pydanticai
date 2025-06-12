from collections import UserList
from sqlalchemy import INTEGER, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey

from config.database import Model, SchemaIcatu
from modules.fornecedores.model import Fornecedor


class FonteDados(Model, SchemaIcatu):
    __tablename__ = "fontes_dados"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    nome: Mapped[str] = mapped_column(TEXT, nullable=False)

    fornecedor_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.fornecedores.id"), nullable=False
    )
    fornecedor: Mapped[Fornecedor] = relationship(lazy="joined")

    def get_nome_completo_fonte_dados(self) -> str:
        return f"{self.fornecedor.nome}{self.nome}"

    def get_nome_fornecedor(self) -> str:
        return self.fornecedor.nome


class FonteDadosCollection(UserList[FonteDados]):
    def get_by_nome_completo(self, nome: str) -> FonteDados | None:
        for fonte_dados in self.data:
            if fonte_dados.get_nome_completo_fonte_dados() == nome:
                return fonte_dados

        return None
