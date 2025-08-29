"""
Entidades SQLAlchemy para o módulo FIDCS.

Define os modelos de dados para indicadores FIDC e valores associados.
"""

from datetime import datetime

from config.database import Model, SchemaIcatu
from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship


class IndicadorFIDC(Model, SchemaIcatu):
    """
    Mapeia a tabela 'indicador_fidc_tb'.

    Armazena os indicadores de um determinado ativo.
    """

    __tablename__ = "indicador_fidc_tb"

    indicador_fidc_id: Mapped[int] = mapped_column(primary_key=True)
    indicador_fidc_nm: Mapped[str] = mapped_column(String(200), unique=True)
    descricao: Mapped[str | None] = mapped_column(Text)
    categoria: Mapped[str | None] = mapped_column(String(50))
    tipo_dado: Mapped[str | None] = mapped_column(
        String(50)
    )  # 'float', 'string', 'date', 'int'
    unidade: Mapped[str | None] = mapped_column(String(50))  # 'R$', '%', 'dias', 'meses'

    valores: Mapped[list["IndicadorFIDCValor"]] = relationship(back_populates="indicador")
    dados_cadastrais: Mapped[list["FIDCDadosCadastrais"]] = relationship(
        back_populates="indicador"
    )


class IndicadorFIDCValor(Model, SchemaIcatu):
    """
    Mapeia a tabela 'indicador_fidc_valor_tb'.

    Armazena os valores de um determinado indicador.
    """

    __tablename__ = "indicador_fidc_valor_tb"

    indicador_fidc_valor_id: Mapped[int] = mapped_column(primary_key=True)
    ativo_codigo: Mapped[str] = mapped_column(
        String(11), ForeignKey("icatu.ativos.codigo"), nullable=False
    )
    indicador_fidc_id: Mapped[int] = mapped_column(
        ForeignKey("icatu.indicador_fidc_tb.indicador_fidc_id")
    )
    valor: Mapped[float | None] = mapped_column(Float)
    limite: Mapped[str | None] = mapped_column(String(100))
    limite_superior: Mapped[bool | None] = mapped_column(Boolean)
    extra_data: Mapped[dict | None] = mapped_column(JSONB)  # Para dados estruturados
    mes: Mapped[str] = mapped_column(String(10))
    ano: Mapped[int] = mapped_column(Integer)
    data_captura: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)

    indicador: Mapped["IndicadorFIDC"] = relationship(back_populates="valores")

    __table_args__ = (
        UniqueConstraint(
            "ativo_codigo", "indicador_fidc_id", "mes", "ano", name="indicador_fidc_valor_un"
        ),
        {"schema": "icatu", "extend_existing": True},
    )


class FIDCDadosCadastrais(Model, SchemaIcatu):
    """
    Mapeia a tabela 'fidc_dados_cadastrais_tb'.

    Armazena os dados cadastrais de um determinado indicador.
    """

    __tablename__ = "fidc_dados_cadastrais_tb"

    fidc_dados_cadastrais_id: Mapped[int] = mapped_column(primary_key=True)
    ativo_codigo: Mapped[str] = mapped_column(
        String(11), ForeignKey("icatu.ativos.codigo"), nullable=False
    )
    indicador_fidc_id: Mapped[int] = mapped_column(
        ForeignKey("icatu.indicador_fidc_tb.indicador_fidc_id"), nullable=False
    )
    valor: Mapped[str] = mapped_column(Text)

    indicador: Mapped["IndicadorFIDC"] = relationship(back_populates="dados_cadastrais")

    __table_args__ = (
        UniqueConstraint("ativo_codigo", "indicador_fidc_id", name="fidc_dados_cadastrais_un"),
        {"schema": "icatu", "extend_existing": True},
    )
