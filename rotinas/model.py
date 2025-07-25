from datetime import date, datetime
from sqlalchemy import Date, Integer, Text, TIMESTAMP
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List

from config.database import Model, SchemaIcatu
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint

CURVA_DI = 1
CURVA_NTNB = 2
DAP = 3


class Rotina(Model, SchemaIcatu):
    __tablename__ = "rotina"

    id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        primary_key=True,
    )
    nome: Mapped[str] = mapped_column(Text, nullable=False)

    atualizacoes: Mapped[list["AtualizacaoRotina"]] = relationship(
        back_populates="rotina"
    )


class AtualizacaoRotina(Model, SchemaIcatu):
    __tablename__ = "atualizacao_rotina"

    id_rotina: Mapped[int] = mapped_column(
        Integer, ForeignKey("icatu.rotina.id"), primary_key=True
    )
    data: Mapped[date] = mapped_column(Date, nullable=False, primary_key=True)
    atualizacao: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

    rotina: Mapped[Rotina] = relationship(back_populates="atualizacoes")
