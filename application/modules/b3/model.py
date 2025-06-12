from datetime import date, datetime
from decimal import Decimal
from config.database import Model, SchemaOperacoes
from sqlalchemy import BOOLEAN, DATE, DECIMAL, INTEGER, TEXT, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.operacoes.model import AlocacaoInterna, B3Corretora, B3Mesa


class B3Voice(Model, SchemaOperacoes):
    __tablename__ = "b3_voices"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    id_ordem: Mapped[str] = mapped_column(TEXT)
    id_ordem_secundario: Mapped[str] = mapped_column(TEXT)
    id_trader: Mapped[str] = mapped_column(TEXT)

    id_execucao: Mapped[str] = mapped_column(TEXT)

    codigo_ativo: Mapped[str] = mapped_column(TEXT)

    id_instrumento: Mapped[str | None] = mapped_column(TEXT)
    id_instrumento_subjacente: Mapped[str | None] = mapped_column(TEXT)

    vanguarda_compra: Mapped[bool] = mapped_column(BOOLEAN)
    preco_unitario: Mapped[Decimal] = mapped_column(DECIMAL)
    quantidade: Mapped[Decimal] = mapped_column(DECIMAL)
    data_negociacao: Mapped[date] = mapped_column(DATE)
    data_liquidacao: Mapped[date] = mapped_column(DATE)

    contraparte_b3_mesa_id: Mapped[int | None] = mapped_column(INTEGER)
    b3_mesa_order_entry: Mapped[B3Mesa | None] = relationship(
        primaryjoin="B3Voice.contraparte_b3_mesa_id == B3Mesa.id_b3",
        foreign_keys=contraparte_b3_mesa_id,
    )

    contraparte_b3_corretora_nome: Mapped[str | None] = mapped_column(TEXT)
    b3_corretora_post_trade: Mapped[B3Corretora | None] = relationship(
        primaryjoin="B3Voice.contraparte_b3_corretora_nome == B3Corretora.nome",
        foreign_keys=contraparte_b3_corretora_nome,
    )

    horario_recebimento_order_entry: Mapped[datetime | None] = mapped_column(TIMESTAMP)
    horario_recebimento_post_trade: Mapped[datetime | None] = mapped_column(TIMESTAMP)

    aprovado_em: Mapped[datetime | None] = mapped_column(TIMESTAMP)
    cancelado_em: Mapped[datetime | None] = mapped_column(TIMESTAMP)

    casamento: Mapped["CasamentoAlocacaoB3Voice | None"] = relationship(uselist=False)
    envios_pre_trade: Mapped[list["EnvioDecisaoB3Voice"]] = relationship()
    envios_post_trade: Mapped[list["EnvioAlocacaoB3Voice"]] = relationship()


class EnvioDecisaoB3Voice(Model, SchemaOperacoes):
    __tablename__ = "envios_decisao_b3_voice"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    voice_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("operacoes.b3_voices.id"))
    decisao: Mapped[str] = mapped_column(TEXT)

    sequencia_fix: Mapped[int] = mapped_column(INTEGER)

    enviado_em: Mapped[datetime] = mapped_column(TIMESTAMP)
    erro_em: Mapped[datetime | None] = mapped_column(TIMESTAMP)
    detalhes_erro: Mapped[str | None] = mapped_column(TEXT)

    usuario_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("auth.usuarios.id"))


class CasamentoAlocacaoB3Voice(Model, SchemaOperacoes):
    __tablename__ = "casamento_alocacoes_b3_voice"

    voice_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("operacoes.b3_voices.id"), primary_key=True
    )
    casado_em: Mapped[datetime] = mapped_column(TIMESTAMP)
    usuario_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("auth.usuarios.id"))

    voice: Mapped[B3Voice] = relationship()
    pivot_alocacoes: Mapped[list["AlocacoesInternasCasamentos"]] = relationship()


class AlocacoesInternasCasamentos(Model, SchemaOperacoes):
    __tablename__ = "alocacoes_casamentos"

    alocacao_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("operacoes.alocacoes.id"), primary_key=True
    )
    casamento_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("operacoes.casamento_alocacoes_b3_voice.voice_id")
    )
    alocacao: Mapped[AlocacaoInterna] = relationship()
    casamento: Mapped[CasamentoAlocacaoB3Voice] = relationship()


class B3RegistroNoMe(Model, SchemaOperacoes):
    __tablename__ = "b3_registros_nome"

    alocacao_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("operacoes.alocacoes.id"), primary_key=True
    )
    numero_controle: Mapped[str] = mapped_column(TEXT)
    data: Mapped[date] = mapped_column(DATE)
    recebido_em: Mapped[datetime] = mapped_column(TIMESTAMP)
    posicao_custodia: Mapped[bool | None] = mapped_column(BOOLEAN)
    posicao_custodia_em: Mapped[datetime | None] = mapped_column(TIMESTAMP)
    posicao_custodia_contraparte: Mapped[bool | None] = mapped_column(BOOLEAN)
    posicao_custodia_contraparte_em: Mapped[datetime | None] = mapped_column(TIMESTAMP)

    alocacao: Mapped[AlocacaoInterna] = relationship()


class EnvioAlocacaoB3Voice(Model, SchemaOperacoes):
    __tablename__ = "envios_alocacao_b3_voice"

    id: Mapped[str] = mapped_column(TEXT, primary_key=True)
    voice_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("operacoes.b3_voices.id"))

    enviado_em: Mapped[datetime] = mapped_column(TIMESTAMP)
    erro_em: Mapped[datetime | None] = mapped_column(TIMESTAMP)
    detalhes_erro: Mapped[str | None] = mapped_column(TEXT)
    sucesso_em: Mapped[datetime | None] = mapped_column(TIMESTAMP)

    usuario_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("auth.usuarios.id"))

    conteudo: Mapped[str] = mapped_column(TEXT)
