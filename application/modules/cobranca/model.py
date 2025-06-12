from datetime import date, datetime
from config.database import Model, SchemaFinanceiro
from sqlalchemy import CHAR, DATE, DOUBLE, INTEGER, TEXT, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.auth.model import Usuario

class TipoExecucaoDaycoval(Model, SchemaFinanceiro):
    __tablename__ = "tipos_execucao_daycoval"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)


class ExecucaoDaycoval(Model, SchemaFinanceiro):
    __tablename__ = "execucao_daycoval"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)

    inicio: Mapped[datetime] = mapped_column(TIMESTAMP)
    fim: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)
    erro: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    tipo_execucao_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("financeiro.tipos_execucao_daycoval.id"))
    tipo_execucao: Mapped[TipoExecucaoDaycoval] = relationship()

    usuario_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("auth.usuarios.id"))
    usuario: Mapped[Usuario] = relationship()

    passos: Mapped[list['PassoExecucaoDaycoval']] = relationship()
    dados: Mapped[list['DadosExecucaoDaycoval']] = relationship()


class PassoExecucaoDaycoval(Model, SchemaFinanceiro):
    __tablename__ = "passo_execucao_daycoval"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)
    inicio: Mapped[datetime] = mapped_column(TIMESTAMP)
    fim: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)
    erro: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    execucao_daycoval_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("financeiro.execucao_daycoval.id"))
    execucao: Mapped[ExecucaoDaycoval] = relationship()


class DadosExecucaoDaycoval(Model, SchemaFinanceiro):
    __tablename__ = "dados_execucao_daycoval"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)

    identificador_titulo: Mapped[str] = mapped_column(TEXT)
    identificador_documento_cobranca: Mapped[str] = mapped_column(TEXT)

    vencimento: Mapped[date] = mapped_column(DATE)
    valor: Mapped[float] = mapped_column(DOUBLE)

    percentual_juros_mora_ao_mes: Mapped[float] = mapped_column(DOUBLE)
    percentual_sobre_valor_multa_mora: Mapped[float] = mapped_column(DOUBLE)
    
    conteudo_arquivo_remessa: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    nome_arquivo_remessa: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    nome_arquivo_retorno: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    arquivo_id_boleto_parcial_pdf: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    conteudo_arquivo_retorno: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    arquivo_id_boleto_completo_pdf: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    execucao_daycoval_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("financeiro.execucao_daycoval.id")
    )
    execucao: Mapped[ExecucaoDaycoval] = relationship()
    contrato_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("financeiro.contratos_locacao.id")
    )
    contrato: Mapped['ContratoLocacao'] = relationship()

class Inquilino(SchemaFinanceiro, Model):
    __tablename__ = "inquilinos"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    razao_social: Mapped[str] = mapped_column(TEXT)
    cnpj: Mapped[str] = mapped_column(CHAR(14))
    cep: Mapped[str] = mapped_column(CHAR(8))
    logradouro: Mapped[str] = mapped_column(TEXT)
    bairro: Mapped[str] = mapped_column(TEXT)
    cidade: Mapped[str] = mapped_column(TEXT)
    estado: Mapped[str] = mapped_column(CHAR(2))

    contratos: Mapped[list["ContratoLocacao"]] = relationship()


class ContratoLocacao(SchemaFinanceiro, Model):
    __tablename__ = "contratos_locacao"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    fundo_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("icatu.fundos.id"))
    inquilino_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("financeiro.inquilinos.id")
    )

    dia_vencimento: Mapped[int] = mapped_column(INTEGER)
    percentual_juros_mora_ao_mes: Mapped[float] = mapped_column(DOUBLE)

    faixas_cobranca_multa_mora: Mapped[list["FaixaMultaMora"]] = relationship()
    inquilino: Mapped[Inquilino] = relationship()


class FaixaMultaMora(SchemaFinanceiro, Model):
    __tablename__ = "multa_mora"

    contrato_locacao_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("financeiro.contratos_locacao.id"), primary_key=True
    )
    dias_a_partir_vencimento: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    percentual_sobre_valor: Mapped[float] = mapped_column(DOUBLE)
