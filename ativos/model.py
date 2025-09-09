from datetime import date, datetime
from enum import IntEnum
from config.database import Model, SchemaIcatu, SchemaSistema
from sqlalchemy.orm import Mapped

from modules.auth.model import Usuario
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint
from sqlalchemy import (
    SmallInteger,
    Text,
    VARCHAR,
    Double,
    Date,
    DateTime,
    Boolean,
    CHAR,
    Integer,
)


class Ativo(Model, SchemaIcatu):
    __tablename__ = "ativos"

    codigo: Mapped[str] = mapped_column(VARCHAR(11), primary_key=True, nullable=False)
    valor_emissao: Mapped[float] = mapped_column(Double, nullable=False)
    data_emissao: Mapped[date] = mapped_column(Date, nullable=False)
    inicio_rentabilidade: Mapped[date] = mapped_column(Date, nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False)
    taxa: Mapped[float] = mapped_column(Double, nullable=False)
    atualizacao: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    cadastro_manual: Mapped[bool] = mapped_column(Boolean, nullable=False)

    emissor_id: Mapped[str] = mapped_column(
        SmallInteger, ForeignKey("icatu.emissores.id"), nullable=False
    )
    emissor: Mapped["Emissor"] = relationship(back_populates="ativos")
    tipo_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("icatu.ativo_tipos.id"), nullable=False
    )
    tipo: Mapped["AtivoTipo"] = relationship(back_populates="ativos")
    indice_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("icatu.ativo_indices.id"), nullable=False
    )
    indice: Mapped["AtivoIndice"] = relationship(back_populates="ativos")

    apelido: Mapped[str | None] = mapped_column(Text, nullable=True)
    isin: Mapped[str | None] = mapped_column(VARCHAR(12), nullable=True)
    serie: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    emissao: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    ativo_ipca: Mapped["AtivoIPCA | None"] = relationship(back_populates="ativo")
    fluxos: Mapped[list["AtivoFluxo"]] = relationship(back_populates="ativo")


class AtivoIndice(Model, SchemaIcatu):
    __tablename__ = "ativo_indices"

    IGPM_M = 1
    IPCA_M = 2
    CDI_M = 3
    P_CDI = 4
    PRÉ = 5

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, nullable=False)
    nome: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    ativos: Mapped[list[Ativo]] = relationship(back_populates="indice")


class Emissor(Model, SchemaIcatu):
    __tablename__ = "emissores"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    cnpj: Mapped[str] = mapped_column(CHAR(14), nullable=False)
    nome: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    grupo_id: Mapped[int | None] = mapped_column(
        SmallInteger, ForeignKey("icatu.emissor_grupos.id"), nullable=True
    )
    grupo: Mapped["EmissorGrupo | None"] = relationship(back_populates="emissores")
    setor_id: Mapped[int | None] = mapped_column(
        SmallInteger, ForeignKey("icatu.emissor_setores.id"), nullable=True
    )
    setor: Mapped["EmissorSetor | None"] = relationship(back_populates="emissores")
    analista_credito_id: Mapped[int | None] = mapped_column(
        SmallInteger, ForeignKey("icatu.analistas_credito.id"), nullable=True
    )
    analista_credito: Mapped["AnalistaCredito | None"] = relationship(
        back_populates="emissores"
    )

    ativos: Mapped[list[Ativo]] = relationship(back_populates="emissor")

    codigo_cvm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tier: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)


class EmissorGrupo(Model, SchemaIcatu):
    __tablename__ = "emissor_grupos"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, nullable=False)
    nome: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    emissores: Mapped[list[Emissor]] = relationship(back_populates="grupo")


class EmissorSetorIcone(Model, SchemaSistema):
    __tablename__ = "emissor_setor_icone"

    setor_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("icatu.emissor_setores.id"),
        primary_key=True,
        unique=True,
    )
    setor: Mapped["EmissorSetor"] = relationship(
        back_populates="icone", single_parent=True
    )
    icone: Mapped[str] = mapped_column(Text, nullable=False)


class EmissorSetor(Model, SchemaIcatu):
    __tablename__ = "emissor_setores"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, nullable=False)
    nome: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    emissores: Mapped[list[Emissor]] = relationship(back_populates="setor")

    icone: Mapped[EmissorSetorIcone | None] = relationship(
        back_populates="setor", uselist=False
    )


class AnalistaCredito(Model, SchemaIcatu):
    __tablename__ = "analistas_credito"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, nullable=False)

    user_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("auth.usuarios.id"), unique=True, nullable=True
    )
    user: Mapped[Usuario] = relationship()

    emissores: Mapped[list[Emissor]] = relationship(back_populates="analista_credito")


class AtivoTipo(Model, SchemaIcatu):
    __tablename__ = "ativo_tipos"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, nullable=False)
    nome: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    ativos: Mapped[list[Ativo]] = relationship(back_populates="tipo")


class AtivoIPCA(Model, SchemaIcatu):
    __tablename__ = "ativos_ipca"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    mesversario: Mapped[int] = mapped_column(Integer, nullable=False)
    ipca_negativo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ipca_2_meses: Mapped[bool] = mapped_column(Boolean, nullable=False)

    ativo_codigo: Mapped[str] = mapped_column(
        VARCHAR(11),
        ForeignKey("icatu.ativos.codigo", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
    )
    ativo: Mapped[Ativo] = relationship()


class AtivoFluxo(Model, SchemaIcatu):
    __tablename__ = "ativo_fluxos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)

    ativo_codigo: Mapped[str] = mapped_column(
        VARCHAR(11),
        ForeignKey("icatu.ativos.codigo", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    data_pagamento: Mapped[date] = mapped_column(Date, nullable=False)
    ativo_fluxo_tipo_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("icatu.ativo_fluxo_tipos.id"), nullable=False
    )

    data_evento: Mapped[date] = mapped_column(Date, nullable=True)
    percentual: Mapped[float] = mapped_column(Double, nullable=True)
    pu_evento: Mapped[float] = mapped_column(Double, nullable=True)
    pu_calculado: Mapped[float] = mapped_column(Double, nullable=True)

    tipo: Mapped["AtivoFluxoTipo"] = relationship(back_populates="fluxos")
    ativo: Mapped[Ativo] = relationship(back_populates="fluxos")


class AtivoFluxoTipo(Model, SchemaIcatu):
    __tablename__ = "ativo_fluxo_tipos"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, nullable=False)
    nome: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    tokens: Mapped[str] = mapped_column(Text, nullable=False)

    fluxos: Mapped[list[AtivoFluxo]] = relationship(back_populates="tipo")


class AgenciaRating(Model, SchemaIcatu):
    __tablename__ = "agencias_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(Text)

    agencia: Mapped["Rating"] = relationship(back_populates="agencia_ratings")


class Rating(Model, SchemaIcatu):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agencia_ratings_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("icatu.agencias_ratings.id")
    )
    rating: Mapped[str] = mapped_column(Text)
    ordenacao: Mapped[int] = mapped_column(Integer)

    agencia_ratings: Mapped[AgenciaRating] = relationship(back_populates="agencia")


class CategoriaAtivo(Model, SchemaIcatu):
    __tablename__ = "categorias_ativo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(Text)


class TipoAtivo(Model, SchemaIcatu):
    __tablename__ = "tipos_ativo"

    class ID(IntEnum):
        BOND = 1
        CDB = 2
        CRA = 3
        CRI = 4
        Debênture = 5
        DPGE = 6
        FIDC = 7
        FII = 8
        LF = 9
        LFS = 10
        LFSC = 11
        LFSN = 12
        NC = 13
        RDB = 14
        FIAGRO = 15

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(Text)

    categoria_ativo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("icatu.categorias_ativo.id")
    )
    categoria_ativo: Mapped[CategoriaAtivo] = relationship()
