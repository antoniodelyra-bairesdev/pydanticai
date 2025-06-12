from datetime import date, datetime
from sqlalchemy import (
    BOOLEAN,
    DATE,
    DOUBLE,
    Integer,
    TIMESTAMP,
    CHAR,
    TEXT,
    SmallInteger,
)
from sqlalchemy.orm import mapped_column, relationship, Mapped

from config.database import Model, SchemaIcatu, SchemaSiteInstitucional
from sqlalchemy.sql.schema import ForeignKey

from modules.arquivos.model import Arquivo
from modules.mesas.model import FundoMesaAssociacao, Mesa
from sqlalchemy.sql.sqltypes import FLOAT


class PublicoAlvo(Model, SchemaIcatu):
    __tablename__ = "publicos_alvo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)


class IndiceBenchmark(Model, SchemaIcatu):
    __tablename__ = "indices_benchmark"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)


class FundoCaracteristicaExtra(Model, SchemaIcatu):
    __tablename__ = "fundo_caracteristicas_extras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)


class FundoClassificacaoSiteInstitucional(Model, SchemaSiteInstitucional):
    __tablename__ = "fundo_classificacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)


class FundoTipoSiteInstitucional(Model, SchemaSiteInstitucional):
    __tablename__ = "fundo_tipos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)


class FundoCaracteristicaExtraRelacionamentoSiteInstitucional(
    Model, SchemaSiteInstitucional
):
    __tablename__ = "fundos_fundo_caracteristicas_extras"

    site_institucional_fundo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("site_institucional.fundos.id"), primary_key=True
    )
    fundo_caracteristica_extra_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("icatu.fundo_caracteristicas_extras.id"), primary_key=True
    )

    fundo: Mapped["FundoSiteInstitucional"] = relationship()
    caracteristica_extra: Mapped[FundoCaracteristicaExtra] = relationship()


class FundoSiteInstitucional(Model, SchemaSiteInstitucional):
    __tablename__ = "fundos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fundo_id: Mapped[int] = mapped_column(Integer, ForeignKey("icatu.fundos.id"))
    nome: Mapped[str] = mapped_column(TEXT, nullable=False)
    cnpj: Mapped[str] = mapped_column(CHAR(14), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    aberto_para_captacao: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)
    fundo_disponibilidade_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ticker_b3: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    cotizacao_resgate: Mapped[int] = mapped_column(Integer, nullable=False)
    cotizacao_resgate_sao_dias_uteis: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=False
    )
    cotizacao_resgate_detalhes: Mapped[str] = mapped_column(TEXT, nullable=False)
    financeiro_resgate: Mapped[int] = mapped_column(Integer, nullable=False)
    financeiro_resgate_sao_dias_uteis: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=False
    )
    financeiro_resgate_detalhes: Mapped[str] = mapped_column(TEXT, nullable=False)
    publico_alvo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("icatu.publicos_alvo.id"), nullable=False
    )
    benchmark: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    taxa_performance: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    taxa_administracao: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    taxa_administracao_maxima: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    resumo_estrategias: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    site_institucional_classificacao_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("site_institucional.fundo_classificacoes.id")
    )
    site_institucional_tipo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("site_institucional.fundo_tipos.id")
    )
    mesa_id: Mapped[int] = mapped_column(Integer, ForeignKey("icatu.mesas.id"))
    ordenacao: Mapped[int] = mapped_column(Integer, nullable=False)
    data_inicio: Mapped[date | None] = mapped_column(DATE, nullable=True)

    classificacao: Mapped[FundoClassificacaoSiteInstitucional] = relationship()
    tipo: Mapped[FundoTipoSiteInstitucional] = relationship()
    publico_alvo: Mapped[PublicoAlvo] = relationship()
    fundos_documentos: Mapped[list["FundoDocumentoSiteInstitucional"]] = relationship()
    indices_benchmark: Mapped[list["FundoIndiceBenchmarkSiteInstitucional"]] = (
        relationship()
    )
    mesa: Mapped[Mesa] = relationship()
    caracteristicas_extras: Mapped[
        list[FundoCaracteristicaExtraRelacionamentoSiteInstitucional]
    ] = relationship()
    distribuidores: Mapped[list["FundoDistribuidorRelacionamentoSiteInstitucional"]] = (
        relationship()
    )


class FundoIndiceBenchmarkSiteInstitucional(Model, SchemaSiteInstitucional):
    __tablename__ = "fundos_indices_benchmark"

    site_institucional_fundo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("site_institucional.fundos.id"), primary_key=True
    )
    indice_benchmark_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("icatu.indices_benchmark.id"), primary_key=True
    )
    ordenacao: Mapped[int] = mapped_column(Integer)

    fundo: Mapped[FundoSiteInstitucional] = relationship()
    indice_benchmark: Mapped[IndiceBenchmark] = relationship()


class FundoCaracteristicaExtraRelacionamento(Model, SchemaIcatu):
    __tablename__ = "fundos_fundo_caracteristicas_extras"

    fundo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("icatu.fundos.id"), primary_key=True
    )
    fundo_caracteristica_extra_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("icatu.fundo_caracteristicas_extras.id"), primary_key=True
    )

    fundo: Mapped["Fundo"] = relationship()
    caracteristica_extra: Mapped[FundoCaracteristicaExtra] = relationship()


class Fundo(Model, SchemaIcatu):
    __tablename__ = "fundos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    isin: Mapped[str | None] = mapped_column(CHAR(12), unique=True, index=True)
    mnemonico: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    nome: Mapped[str] = mapped_column(TEXT, nullable=False)
    codigo_brit: Mapped[int | None] = mapped_column(
        Integer, unique=True, nullable=False
    )
    cnpj: Mapped[str] = mapped_column(CHAR(14), unique=True, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    conta_cetip: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    conta_selic: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    codigo_carteira: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    fundo_custodiante_id: Mapped[int | None] = mapped_column(
        SmallInteger, ForeignKey("icatu.fundo_custodiantes.id")
    )
    aberto_para_captacao: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)
    fundo_disponibilidade_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("icatu.fundo_disponibilidades.id")
    )
    ticker_b3: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    fundo_administrador_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("icatu.fundo_administradores.id")
    )
    codigo_carteira_administrador: Mapped[str | None] = mapped_column(
        TEXT, nullable=True
    )
    fundo_controlador_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("icatu.fundo_controladores.id")
    )
    agencia_bancaria_custodia: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    conta_aplicacao: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    conta_resgate: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    conta_movimentacao: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    conta_tributada: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    minimo_aplicacao: Mapped[float | None] = mapped_column(DOUBLE, nullable=True)
    minimo_movimentacao: Mapped[float | None] = mapped_column(DOUBLE, nullable=True)
    minimo_saldo: Mapped[float | None] = mapped_column(DOUBLE, nullable=True)

    cotizacao_aplicacao: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cotizacao_aplicacao_sao_dias_uteis: Mapped[bool | None] = mapped_column(
        BOOLEAN, nullable=True
    )
    cotizacao_aplicacao_detalhes: Mapped[str | None] = mapped_column(
        TEXT, nullable=True
    )

    cotizacao_resgate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cotizacao_resgate_sao_dias_uteis: Mapped[bool | None] = mapped_column(
        BOOLEAN, nullable=True
    )
    cotizacao_resgate_detalhes: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    financeiro_aplicacao: Mapped[int | None] = mapped_column(Integer, nullable=True)
    financeiro_aplicacao_sao_dias_uteis: Mapped[bool | None] = mapped_column(
        BOOLEAN, nullable=True
    )
    financeiro_aplicacao_detalhes: Mapped[str | None] = mapped_column(
        TEXT, nullable=True
    )

    financeiro_resgate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    financeiro_resgate_sao_dias_uteis: Mapped[bool | None] = mapped_column(
        BOOLEAN, nullable=True
    )
    financeiro_resgate_detalhes: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    publico_alvo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("icatu.publicos_alvo.id")
    )

    benchmark: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    taxa_performance: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    taxa_administracao: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    taxa_administracao_maxima: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    resumo_estrategias: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    data_inicio: Mapped[date | None] = mapped_column(TEXT, nullable=True)

    disponibilidade: Mapped["FundoDisponibilidade"] = relationship()
    custodiante: Mapped["FundoCustodiante | None"] = relationship()
    administrador: Mapped["FundoAdministrador | None"] = relationship()
    controlador: Mapped["FundoControlador"] = relationship()
    publico_alvo: Mapped[PublicoAlvo] = relationship()
    fundo_site_institucional: Mapped[FundoSiteInstitucional | None] = relationship()
    documentos: Mapped[list["FundoDocumento"]] = relationship()
    indices_benchmark: Mapped[list["FundoIndiceBenchmark"]] = relationship()
    mesas: Mapped[list[FundoMesaAssociacao]] = relationship()
    caracteristicas_extras: Mapped[list[FundoCaracteristicaExtraRelacionamento]] = (
        relationship()
    )
    distribuidores: Mapped[list["FundoDistribuidorRelacionamento"]] = relationship()


class FundoIndiceBenchmark(Model, SchemaIcatu):
    __tablename__ = "fundos_indices_benchmark"

    fundo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("icatu.fundos.id"), primary_key=True
    )
    indice_benchmark_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("icatu.indices_benchmark.id"), primary_key=True
    )
    ordenacao: Mapped[int] = mapped_column(Integer)

    fundo: Mapped[Fundo] = relationship()
    indice_benchmark: Mapped[IndiceBenchmark] = relationship()


class InstituicaoFinanceira(Model, SchemaIcatu):
    __tablename__ = "instituicoes_financeiras"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT, unique=True, nullable=False)


class FundoAdministrador(Model, SchemaIcatu):
    __tablename__ = "fundo_administradores"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT, unique=True, nullable=False)

    instituicao_financeira_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("icatu.instituicoes_financeiras.id")
    )
    instituicao_financeira: Mapped[InstituicaoFinanceira | None] = relationship()


class FundoControlador(Model, SchemaIcatu):
    __tablename__ = "fundo_controladores"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT, unique=True, nullable=False)

    instituicao_financeira_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("icatu.instituicoes_financeiras.id")
    )
    instituicao_financeira: Mapped[InstituicaoFinanceira | None] = relationship()


class FundoCustodiante(Model, SchemaIcatu):
    __tablename__ = "fundo_custodiantes"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT, unique=True, nullable=False)

    instituicao_financeira_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("icatu.instituicoes_financeiras.id")
    )
    instituicao_financeira: Mapped[InstituicaoFinanceira | None] = relationship()


class FundoCategoriaDocumento(Model, SchemaIcatu):
    __tablename__ = "fundo_categorias_documento"

    MATERIAL_PUBLICITARIO = 1
    PROSPECTOS = 2
    AVISOS_AO_MERCADO = 3
    FATOS_RELEVANTES = 4
    RELATORIOS_GERENCIAIS = 5
    COMUNICADOS_AO_MERCADO = 6
    REGULAMENTOS = 7
    LAMINA = 8

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)


class FundoDocumento(Model, SchemaIcatu):
    __tablename__ = "fundos_documentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fundo_id: Mapped[int] = mapped_column(Integer, ForeignKey("icatu.fundos.id"))
    arquivo_id: Mapped[str] = mapped_column(TEXT, ForeignKey("sistema.arquivos.id"))
    fundo_categoria_documento_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("icatu.fundo_categorias_documento.id")
    )
    titulo: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    criado_em: Mapped[datetime] = mapped_column(TIMESTAMP)
    data_referencia: Mapped[date] = mapped_column(DATE)

    fundo: Mapped[Fundo] = relationship()
    arquivo: Mapped[Arquivo] = relationship()
    fundo_categoria_documento: Mapped[FundoCategoriaDocumento] = relationship()


class FundoDisponibilidade(Model, SchemaIcatu):
    __tablename__ = "fundo_disponibilidades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT)


class FundoDocumentoSiteInstitucional(Model, SchemaSiteInstitucional):
    __tablename__ = "fundos_documentos"

    site_institucional_fundo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("site_institucional.fundos.id"), primary_key=True
    )
    fundos_documento_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("icatu.fundos_documentos.id"), primary_key=True
    )

    site_institucional_fundo: Mapped[FundoSiteInstitucional] = relationship()
    fundo_documento: Mapped[FundoDocumento] = relationship()


class FundoDistribuidor(Model, SchemaIcatu):
    __tablename__ = "fundo_distribuidores"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    nome: Mapped[str] = mapped_column(TEXT, unique=True, nullable=False)
    link: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    instituicao_financeira_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("icatu.instituicoes_financeiras.id")
    )
    instituicao_financeira: Mapped[InstituicaoFinanceira | None] = relationship()


class FundoDistribuidorRelacionamento(Model, SchemaIcatu):
    __tablename__ = "fundo_distribuidores_fundos"

    fundo_distribuidor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("icatu.fundo_distribuidores.id"),
        nullable=False,
        primary_key=True,
    )
    fundo_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("icatu.fundos.id"),
        nullable=False,
        primary_key=True,
    )

    distribuidor: Mapped[FundoDistribuidor] = relationship()
    fundo: Mapped[Fundo] = relationship()


class FundoDistribuidorRelacionamentoSiteInstitucional(Model, SchemaSiteInstitucional):
    __tablename__ = "fundo_distribuidores_fundos"

    fundo_distribuidor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("icatu.fundo_distribuidores.id"),
        nullable=False,
        primary_key=True,
    )
    site_institucional_fundo_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("site_institucional.fundos.id"),
        nullable=False,
        primary_key=True,
    )

    distribuidor: Mapped[FundoDistribuidor] = relationship()
    fundo: Mapped[FundoSiteInstitucional] = relationship()


class FundoCotaRentabilidade(Model, SchemaIcatu):
    __tablename__ = "fundo_cotas_rentabilidades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fundo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("icatu.fundos.id"), nullable=False
    )
    fundo: Mapped[Fundo] = relationship()

    data_posicao: Mapped[date] = mapped_column(DATE, nullable=False)
    preco_cota: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    rentabilidade_dia: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    rentabilidade_mes: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    rentabilidade_ano: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    rentabilidade_12meses: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    rentabilidade_24meses: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    rentabilidade_36meses: Mapped[float | None] = mapped_column(FLOAT, nullable=True)


class FundoPatrimonioLiquidoRentabilidade(Model, SchemaIcatu):
    __tablename__ = "fundo_patrimonio_liquido_rentabilidades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fundo_id: Mapped[int] = mapped_column(Integer, ForeignKey("icatu.fundos.id"))
    fundo: Mapped[Fundo] = relationship()

    data_posicao: Mapped[date] = mapped_column(DATE, nullable=False)
    patrimonio_liquido: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    media_12meses: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    media_24meses: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
    media_36meses: Mapped[float | None] = mapped_column(FLOAT, nullable=True)
