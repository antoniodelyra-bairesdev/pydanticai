from collections import UserList
from datetime import date
from decimal import Decimal
from sqlalchemy import INTEGER, BIGINT, NUMERIC, DATE, TEXT, VARCHAR, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Model, SchemaIcatu
from modules.fontes_dados.model import FonteDados


class Moeda(Model, SchemaIcatu):
    __tablename__ = "moedas"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    nome: Mapped[str] = mapped_column(TEXT, nullable=False)
    codigo: Mapped[str] = mapped_column(VARCHAR(3), nullable=True)
    simbolo: Mapped[str] = mapped_column(TEXT, nullable=False)


class MoedaCollection(UserList[Moeda]):
    def get_by_codigo(self, codigo: str) -> Moeda | None:
        for moeda in self.data:
            if moeda.codigo == codigo:
                return moeda

        return None


class MoedaCotacao(Model, SchemaIcatu):
    __tablename__ = "moedas_cotacoes"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, nullable=False)
    data_referente: Mapped[date] = mapped_column(DATE, nullable=False)
    cotacao: Mapped[Decimal] = mapped_column(NUMERIC, nullable=False)

    moeda_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("icatu.moedas.id"))
    moeda: Mapped[Moeda] = relationship()

    fonte_dado_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.fontes_dados.id")
    )
    fonte_dado: Mapped[FonteDados] = relationship()
