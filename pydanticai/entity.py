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


# --- Model Definition for 'client_ia_tb' ---
class ClientIa(Model, SchemaIcatu):
    """
    Mapeia a tabela 'client_ia_tb'.

    Armazena informações sobre os clientes de IA (ex: OpenAI, Geimini, etc.).
    """

    __tablename__ = "client_ia_tb"

    client_id: Mapped[int] = mapped_column(primary_key=True)
    client_nm: Mapped[str] = mapped_column(String(50), unique=True)
    client_abrev: Mapped[str] = mapped_column(String(10), unique=True)

    models: Mapped[list["ClientModel"]] = relationship(back_populates="client_ia")


# --- Model Definition for 'client_model_tb' ---
class ClientModel(Model, SchemaIcatu):
    """
    Mapeia a tabela 'client_model_tb'.

    Armazena os diferentes modelos de um determinado cliente de IA.
    """

    __tablename__ = "client_model_tb"

    client_model_id: Mapped[int] = mapped_column(primary_key=True)

    client_id: Mapped[int] = mapped_column(ForeignKey("icatu.client_ia_tb.client_id"))

    model_nm: Mapped[str] = mapped_column(String(200), unique=True)
    descricao: Mapped[str | None] = mapped_column(Text)
    custo: Mapped[str | None] = mapped_column(Text)
    ordenacao: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    # Relacionamento: Vários Modelos (ClientModel) pertencem a um Cliente de IA (ClientIa).
    client_ia: Mapped["ClientIa"] = relationship(back_populates="models", lazy="joined")

    # Relacionamento: Um Modelo (ClientModel) pode ser usado em vários Prompts.
    prompts: Mapped[list["Prompt"]] = relationship(back_populates="client_model")


class ModelSchema(Model, SchemaIcatu):
    """
    Mapeia a tabela 'model_schema_tb'.
    """

    __tablename__ = "model_schema_tb"

    model_schema_id: Mapped[int] = mapped_column(primary_key=True)
    model_nm: Mapped[str] = mapped_column(String(200), unique=True)
    model_schema: Mapped[dict | None] = mapped_column(JSONB)

    prompts: Mapped[list["Prompt"]] = relationship(back_populates="model_schema")


# --- Model Definition for 'prompt_tb' ---
class Prompt(Model, SchemaIcatu):
    """
    Mapeia a tabela 'prompt_tb'.

    Armazena os prompts enviados, associando-os a um modelo, mesa e ativo.
    """

    __tablename__ = "prompt_tb"

    prompt_id: Mapped[int] = mapped_column(primary_key=True)

    # Corrigindo o nome da coluna de 'client_model_id ' para 'client_model_id'
    client_model_id: Mapped[int] = mapped_column(
        ForeignKey("icatu.client_model_tb.client_model_id")
    )

    mesa_id: Mapped[int] = mapped_column(ForeignKey("icatu.mesas.id"))
    codigo_ativo: Mapped[str] = mapped_column(
        String(11), ForeignKey("icatu.ativos.codigo")
    )

    temperatura: Mapped[float] = mapped_column(Float)
    max_tokens: Mapped[int] = mapped_column(Integer)
    prompt_sistema: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_usuario: Mapped[str] = mapped_column(Text, nullable=False)
    model_schema_id: Mapped[int | None] = mapped_column(
        ForeignKey("icatu.model_schema_tb.model_schema_id")
    )
    data_criacao: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=False), default=datetime.now
    )
    is_image: Mapped[bool] = mapped_column(Boolean, server_default="FALSE")
    ativo: Mapped[bool] = mapped_column(Boolean, server_default="TRUE")
    descricao: Mapped[str | None] = mapped_column(Text)

    # Relacionamento: Vários Prompts podem usar o mesmo Modelo (ClientModel).
    client_model: Mapped["ClientModel"] = relationship(back_populates="prompts")

    model_schema: Mapped["ModelSchema"] = relationship(back_populates="prompts", lazy="joined")

    # Define a restrição de unicidade composta.
    __table_args__ = (
        UniqueConstraint("client_model_id", "codigo_ativo", "data_criacao", name="prompt_un"),
        {"schema": "icatu", "extend_existing": True},
    )



