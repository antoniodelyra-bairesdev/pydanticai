from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.b3.model import AlocacoesInternasCasamentos, B3RegistroNoMe

from datetime import date, datetime
from decimal import Decimal
from enum import IntEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DATE, TIMESTAMP, INTEGER, TEXT, DECIMAL, BOOLEAN, ForeignKey

from config.database import Model, SchemaIcatu, SchemaOperacoes

from modules.fundos.model import Fundo
from modules.auth.model import Usuario


class Corretora(Model, SchemaIcatu):
    __tablename__ = "corretoras"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)

    b3_corretora: Mapped["B3Corretora"] = relationship(uselist=False)


class B3Corretora(Model, SchemaOperacoes):
    __tablename__ = "b3_corretoras"

    id_b3: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)
    razao_social: Mapped[str] = mapped_column(TEXT)

    corretora_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.corretoras.id")
    )
    corretora: Mapped[Corretora] = relationship()

    b3_mesas: Mapped[list["B3Mesa"]] = relationship()


class B3Mesa(Model, SchemaOperacoes):
    __tablename__ = "b3_mesas"

    id_b3: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)

    b3_corretora_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("operacoes.b3_corretoras.id_b3")
    )
    b3_corretora: Mapped[B3Corretora] = relationship()

    b3_usuarios: Mapped[list["B3Usuarios"]] = relationship()


class B3Usuarios(Model, SchemaOperacoes):
    __tablename__ = "b3_usuarios"

    id_b3: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)

    b3_mesa_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("operacoes.b3_mesas.id_b3")
    )
    b3_mesa: Mapped[B3Mesa] = relationship()


class NaturezaOperacao(Model, SchemaOperacoes):
    __tablename__ = "natureza_operacao"

    class ID(IntEnum):
        EXTERNA = 1
        INTERNA = 2

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)


class MercadoNegociado(Model, SchemaOperacoes):
    __tablename__ = "mercado_negociado"

    class ID(IntEnum):
        PRIMARIO = 1
        SECUNDARIO = 2

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)


class Boleta(Model, SchemaOperacoes):
    __tablename__ = "boletas"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    data_negociacao: Mapped[date] = mapped_column(DATE)
    data_liquidacao: Mapped[date] = mapped_column(DATE)

    tipo_ativo_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.tipos_ativo.id")
    )
    natureza_operacao_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("operacoes.natureza_operacao.id")
    )
    mercado_negociado_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("operacoes.mercado_negociado.id")
    )

    corretora_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.corretoras.id")
    )
    corretora: Mapped[Corretora] = relationship()

    alocacoes: Mapped[list["AlocacaoInterna"]] = relationship()


class AlocacaoInterna(Model, SchemaOperacoes):
    __tablename__ = "alocacoes"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    codigo_ativo: Mapped[str] = mapped_column(TEXT)
    vanguarda_compra: Mapped[bool] = mapped_column(BOOLEAN)
    preco_unitario: Mapped[Decimal] = mapped_column(DECIMAL(20, 8))
    quantidade: Mapped[Decimal] = mapped_column(DECIMAL(20, 8))
    data_negociacao: Mapped[date] = mapped_column(DATE)
    data_liquidacao: Mapped[date] = mapped_column(DATE)
    alocado_em: Mapped[datetime] = mapped_column(TIMESTAMP)
    aprovado_em: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)

    corretora_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.corretoras.id")
    )
    corretora: Mapped[Corretora] = relationship()

    fundo_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("icatu.fundos.id"))
    fundo: Mapped[Fundo] = relationship()

    tipo_ativo_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.tipos_ativo.id")
    )

    boleta_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("operacoes.boletas.id"))
    boleta: Mapped[Boleta] = relationship()

    alocacao_usuario_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("auth.usuarios.id")
    )
    alocacao_usuario: Mapped[Usuario] = relationship(foreign_keys=[alocacao_usuario_id])

    aprovacao_usuario_id: Mapped[int | None] = mapped_column(
        INTEGER, ForeignKey("auth.usuarios.id"), nullable=True
    )
    aprovacao_usuario: Mapped[Usuario | None] = relationship(
        foreign_keys=[aprovacao_usuario_id]
    )

    alocacao_anterior_id: Mapped[int | None] = mapped_column(
        INTEGER, ForeignKey("operacoes.alocacoes.id"), nullable=True
    )
    alocacao_anterior: Mapped["AlocacaoInterna | None"] = relationship()

    alocacao_administrador: Mapped["AlocacaoAdministrador | None"] = relationship(
        uselist=False
    )
    cancelamento: Mapped["CancelamentoAlocacaoInterna | None"] = relationship(
        uselist=False
    )

    pivot_casamento_voice: Mapped["AlocacoesInternasCasamentos | None"] = relationship(
        uselist=False
    )

    registro_NoMe: Mapped["B3RegistroNoMe | None"] = relationship(uselist=False)
    quebras: Mapped[list["AlocacaoInterna"]] = relationship()


class CancelamentoAlocacaoInterna(Model, SchemaOperacoes):
    __tablename__ = "cancelamentos_alocacao"

    alocacao_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("operacoes.alocacoes.id"), primary_key=True
    )
    motivo: Mapped[str | None] = mapped_column(TEXT)
    cancelado_em: Mapped[datetime] = mapped_column(TIMESTAMP)
    usuario_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("auth.usuarios.id"))


class AlocacaoAdministrador(Model, SchemaOperacoes):
    __tablename__ = "alocacoes_administrador"

    alocacao_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("operacoes.alocacoes.id"), primary_key=True
    )
    codigo_administrador: Mapped[str | None] = mapped_column(TEXT)
    alocado_em: Mapped[datetime] = mapped_column(TIMESTAMP)
    alocacao_usuario_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("auth.usuarios.id")
    )
    cancelamento: Mapped["CancelamentoAlocacaoAdministrador | None"] = relationship(
        uselist=False
    )
    liquidacao: Mapped["LiquidacaoAlocacaoAdministrador | None"] = relationship(
        uselist=False
    )


class CancelamentoAlocacaoAdministrador(Model, SchemaOperacoes):
    __tablename__ = "cancelamentos_alocacao_administrador"

    alocacao_administrador_id: Mapped[int] = mapped_column(
        INTEGER,
        ForeignKey("operacoes.alocacoes_administrador.alocacao_id"),
        primary_key=True,
    )
    motivo: Mapped[str | None] = mapped_column(TEXT)
    cancelado_em: Mapped[datetime] = mapped_column(TIMESTAMP)
    usuario_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("auth.usuarios.id"))


class LiquidacaoAlocacaoAdministrador(Model, SchemaOperacoes):
    __tablename__ = "liquidacoes_alocacao_administrador"

    alocacao_administrador_id: Mapped[int] = mapped_column(
        INTEGER,
        ForeignKey("operacoes.alocacoes_administrador.alocacao_id"),
        primary_key=True,
    )
    liquidado_em: Mapped[datetime] = mapped_column(TIMESTAMP)
    usuario_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("auth.usuarios.id"))
