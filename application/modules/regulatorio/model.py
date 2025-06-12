from config.database import Model, SchemaIcatu

from sqlalchemy import INTEGER, TEXT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.arquivos.model import Arquivo


class CategoriaRelatorio(Model, SchemaIcatu):
    __tablename__ = "categoria_relatorio"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)
    ordem: Mapped[int] = mapped_column(INTEGER)

    plano_de_fundo_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.categoria_relatorio_planos_de_fundo.id")
    )

    plano_de_fundo: Mapped["PlanoDeFundo | None"] = relationship()
    documentos: Mapped[list["DocumentoRelatorio"]] = relationship(
        back_populates="categoria"
    )


class DocumentoRelatorio(Model, SchemaIcatu):
    __tablename__ = "documento_relatorio"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)
    categoria_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.categoria_relatorio.id")
    )
    arquivo_id: Mapped[str] = mapped_column(TEXT, ForeignKey("sistema.arquivos.id"))

    categoria: Mapped[CategoriaRelatorio] = relationship()
    arquivo: Mapped[Arquivo] = relationship()


class PlanoDeFundo(Model, SchemaIcatu):
    __tablename__ = "categoria_relatorio_planos_de_fundo"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    conteudo_b64: Mapped[str] = mapped_column(TEXT)
