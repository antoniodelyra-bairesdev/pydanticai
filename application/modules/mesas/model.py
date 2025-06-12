from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.fundos.model import Fundo

from sqlalchemy import BOOLEAN, INTEGER, TEXT, ForeignKey
from config.database import Model, SchemaIcatu
from sqlalchemy.orm import Mapped, mapped_column, relationship


class FundoMesaAssociacao(Model, SchemaIcatu):
    __tablename__ = "fundos_mesas"
    fundo_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.fundos.id"), primary_key=True
    )
    mesa_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.mesas.id"), primary_key=True
    )
    responsavel: Mapped[bool] = mapped_column(BOOLEAN)

    fundo: Mapped["Fundo"] = relationship()
    mesa: Mapped["Mesa"] = relationship()


class Mesa(Model, SchemaIcatu):
    __tablename__ = "mesas"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)
    sobre: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    ordenacao: Mapped[int] = mapped_column(INTEGER)

    fundos: Mapped[list[FundoMesaAssociacao]] = relationship()
