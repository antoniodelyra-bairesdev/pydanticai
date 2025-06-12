from datetime import date, datetime
from decimal import Decimal
from modules.fundos.model import IndiceBenchmark
from sqlalchemy import (
    Date,
    Integer,
    Numeric,
    UniqueConstraint,
    TIMESTAMP,
    Boolean,
    DOUBLE_PRECISION,
)
from sqlalchemy.orm import mapped_column, Mapped, relationship

from config.database import Model, SchemaIcatu
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DATE, FLOAT


class TaxaDI(Model, SchemaIcatu):
    __tablename__ = "taxas_di"

    data: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
        nullable=False,
    )
    dias_corridos: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False
    )
    taxa: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)


class TaxaNTNB(Model, SchemaIcatu):
    __tablename__ = "taxas_ntnb"

    data_referencia: Mapped[date] = mapped_column(
        Date, primary_key=True, nullable=False
    )
    data_vencimento: Mapped[date] = mapped_column(
        Date, primary_key=True, nullable=False
    )
    taxa: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    duration: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)


class TaxasDAP(Model, SchemaIcatu):
    __tablename__ = "taxas_dap"

    data_referencia: Mapped[date] = mapped_column(
        Date, primary_key=True, nullable=False
    )
    data_vencimento: Mapped[date] = mapped_column(
        Date, primary_key=True, nullable=False
    )
    taxa: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)


class HistoricoCDI(Model, SchemaIcatu):
    __tablename__ = "historico_cdi"

    data: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
        nullable=False,
    )
    taxa: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    indice_acumulado: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    atualizacao: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)


class HistoricoIGPM(Model, SchemaIcatu):
    __tablename__ = "historico_igpm"

    data: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
        nullable=False,
    )
    indice_acumulado: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    atualizacao: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)


class HistoricoIPCA(Model, SchemaIcatu):
    __tablename__ = "historico_ipca"

    data: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
        nullable=False,
    )
    indice_acumulado: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    atualizacao: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)


class IGPMProj(Model, SchemaIcatu):
    __tablename__ = "igpm_proj"

    data: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
        nullable=False,
    )
    projetado: Mapped[bool] = mapped_column(Boolean, nullable=False)
    taxa: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    atualizacao: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)


class IPCAProj(Model, SchemaIcatu):
    __tablename__ = "ipca_proj"

    data: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
        nullable=False,
    )
    projetado: Mapped[bool] = mapped_column(Boolean, nullable=False)
    taxa: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    atualizacao: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)


class IndiceBenchmarkRentabilidade(Model, SchemaIcatu):
    __tablename__ = "indice_benchmark_rentabilidades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    indice_benchmark_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("icatu.indices_benchmark.id"), nullable=False
    )
    indice_benchmark: Mapped[IndiceBenchmark] = relationship()

    data_posicao: Mapped[date] = mapped_column(DATE, nullable=False)
    rentabilidade_dia: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    rentabilidade_mes: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    rentabilidade_ano: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    rentabilidade_12meses: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    rentabilidade_24meses: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    rentabilidade_36meses: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
