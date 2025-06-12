from datetime import datetime
from sqlalchemy import TIMESTAMP, CHAR, TEXT, SmallInteger, Table, Column
from sqlalchemy.orm import mapped_column, relationship, Mapped

from config.database import Model, SchemaAuth
from sqlalchemy.sql.schema import ForeignKey

SENHA_PADRAO = "$argon2id$v=19$m=65536,t=3,p=4$b7wXYBsd7CcXxmyVOLlYQQ$3ydt9HCd38DTdOtziaDL77cMllCZ19BnI97rWfmiOwM"

usuarios_funcoes_table = Table(
    "usuarios_funcoes",
    Model.metadata,
    Column(
        "usuario_id", SmallInteger, ForeignKey("auth.usuarios.id"), primary_key=True
    ),
    Column("funcao_id", SmallInteger, ForeignKey("auth.funcoes.id"), primary_key=True),
    schema="auth",
    extend_existing=True,
)


class Usuario(Model, SchemaAuth):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(TEXT, nullable=False)
    email: Mapped[str] = mapped_column(TEXT, nullable=False, unique=True)
    senha: Mapped[str] = mapped_column(
        TEXT,
        server_default=SENHA_PADRAO,
        default=SENHA_PADRAO,
        nullable=False,
    )

    dispositivos: Mapped[list["Dispositivo"]] = relationship(back_populates="usuario")
    funcoes: Mapped[list["Funcao"]] = relationship(
        "Funcao", secondary=usuarios_funcoes_table, back_populates="usuarios"
    )


class Funcao(Model, SchemaAuth):
    __tablename__ = "funcoes"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(TEXT, nullable=False, unique=True)

    funcao_acima_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("auth.funcoes.id"), nullable=True
    )
    funcao_acima: Mapped["Funcao"] = relationship(
        "Funcao", back_populates="funcoes_abaixo", remote_side=[id]
    )
    funcoes_abaixo: Mapped[list["Funcao"]] = relationship(
        "Funcao", back_populates="funcao_acima"
    )

    usuarios: Mapped[list["Usuario"]] = relationship(
        secondary=usuarios_funcoes_table, back_populates="funcoes"
    )


class Dispositivo(Model, SchemaAuth):
    __tablename__ = "dispositivos"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    agente: Mapped[str] = mapped_column(TEXT, nullable=False)
    endereco: Mapped[str] = mapped_column(TEXT, nullable=False)
    ultima_atividade: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    data_login: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    token: Mapped[str] = mapped_column(CHAR(64), nullable=False, unique=True)
    localizacao: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    usuario_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("auth.usuarios.id"), nullable=False
    )
    usuario: Mapped["Usuario"] = relationship(Usuario, back_populates="dispositivos")
