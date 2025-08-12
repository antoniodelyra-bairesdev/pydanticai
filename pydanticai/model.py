from datetime import datetime
from typing import Optional

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    Float,
    Integer,
    Boolean,
    UniqueConstraint,
    TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from config.database import Model, SchemaIcatu


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
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    custo: Mapped[Optional[str]] = mapped_column(Text)
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
    model_schema: Mapped[Optional[dict]] = mapped_column(JSONB)

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
    client_model_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("icatu.client_model_tb.client_model_id")
    )

    mesa_id: Mapped[Optional[int]] = mapped_column(ForeignKey("icatu.mesas.id"))
    codigo_ativo: Mapped[Optional[str]] = mapped_column(
        String(11), ForeignKey("icatu.ativos.codigo")
    )

    temperatura: Mapped[Optional[float]] = mapped_column(Float)
    max_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    prompt_sistema: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_usuario: Mapped[str] = mapped_column(Text, nullable=False)
    model_schema_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("icatu.model_schema_tb.model_schema_id")
    )
    data_criacao: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=False), default=datetime.now
    )
    is_image: Mapped[bool] = mapped_column(Boolean, server_default="FALSE")
    ativo: Mapped[bool] = mapped_column(Boolean, server_default="TRUE")
    descricao: Mapped[Optional[str]] = mapped_column(Text)

    # Relacionamento: Vários Prompts podem usar o mesmo Modelo (ClientModel).
    client_model: Mapped["ClientModel"] = relationship(back_populates="prompts")

    model_schema: Mapped["ModelSchema"] = relationship(back_populates="prompts", lazy="joined")

    # Define a restrição de unicidade composta.
    __table_args__ = (
        UniqueConstraint("client_model_id", "codigo_ativo", "data_criacao", name="prompt_un"),
    )


# --- Model Definition for 'indicador_fidc_tb' ---
class IndicadorFIDC(Model, SchemaIcatu):
    """
    Mapeia a tabela 'indicador_fidc_tb'.

    Armazena os indicadores de um determinado ativo.
    """

    __tablename__ = "indicador_fidc_tb"

    indicador_fidc_id: Mapped[int] = mapped_column(primary_key=True)
    indicador_fidc_nm: Mapped[str] = mapped_column(String(200), unique=True)
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    categoria: Mapped[Optional[str]] = mapped_column(String(50))
    tipo_dado: Mapped[Optional[str]] = mapped_column(
        String(50)
    )  # 'float', 'string', 'date', 'int'
    unidade: Mapped[Optional[str]] = mapped_column(String(50))  # 'R$', '%', 'dias', 'meses'

    valores: Mapped[list["IndicadorFIDCValor"]] = relationship(back_populates="indicador")
    dados_cadastrais: Mapped[list["FIDCDadosCadastrais"]] = relationship(back_populates="indicador")


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
    valor: Mapped[Optional[float]] = mapped_column(Float)
    limite: Mapped[Optional[str]] = mapped_column(String(100))
    limite_superior: Mapped[Optional[bool]] = mapped_column(Boolean)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSONB)  # Para dados estruturados
    mes: Mapped[str] = mapped_column(String(10))
    ano: Mapped[int] = mapped_column(Integer)
    data_captura: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)

    indicador: Mapped["IndicadorFIDC"] = relationship(back_populates="valores")

    __table_args__ = (
        UniqueConstraint(
            "ativo_codigo", "indicador_fidc_id", "mes", "ano", name="indicador_fidc_valor_un"
        ),
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
        UniqueConstraint(
            "ativo_codigo", "indicador_fidc_id", name="fidc_dados_cadastrais_un"
        ),
    )
