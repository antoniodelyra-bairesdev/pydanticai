from datetime import date, datetime
from typing import Literal, Optional
from pydantic import BaseModel as Schema

from modules.arquivos.schema import ArquivoSchema, ArquivoSemIDSchema
from pydantic.fields import PrivateAttr

from .model import (
    Fundo,
    FundoAdministrador,
    FundoControlador,
    FundoCustodiante,
    FundoDocumento,
    FundoSiteInstitucional,
    InstituicaoFinanceira,
)

TipoIdentificadorFundo = Literal["CNPJ", "CETIP", "SELIC", "ID_VANGUARDA"]


class IdentificadorFundo(Schema):
    tipo: TipoIdentificadorFundo
    valor: str


class BaseFundoSchema(Schema):
    isin: str | None = None
    mnemonico: str | None = None
    cnpj: str
    nome: str
    aberto_para_captacao: bool
    codigo_brit: int | None = None
    codigo_carteira: str | None = None
    conta_cetip: str | None = None
    conta_selic: str | None = None
    fundo_disponibilidade_id: int | None = None
    ticker_b3: str | None = None
    fundo_administrador_id: int | None = None
    codigo_carteira_administrador: str | None = None
    fundo_controlador_id: int | None = None
    agencia_bancaria_custodia: str | None = None
    conta_aplicacao: str | None = None
    conta_resgate: str | None = None
    conta_movimentacao: str | None = None
    conta_tributada: str | None = None
    minimo_aplicacao: float | None = None
    minimo_movimentacao: float | None = None
    minimo_saldo: float | None = None
    cotizacao_aplicacao: int | None = None
    cotizacao_aplicacao_sao_dias_uteis: bool | None = None
    cotizacao_aplicacao_detalhes: str | None = None
    cotizacao_resgate: int | None = None
    cotizacao_resgate_sao_dias_uteis: bool | None = None
    cotizacao_resgate_detalhes: str | None = None
    financeiro_aplicacao: int | None = None
    financeiro_aplicacao_sao_dias_uteis: bool | None = None
    financeiro_aplicacao_detalhes: str | None = None
    financeiro_resgate: int | None = None
    financeiro_resgate_sao_dias_uteis: bool | None = None
    financeiro_resgate_detalhes: str | None = None
    publico_alvo_id: int | None = None
    benchmark: str | None = None
    taxa_performance: str | None = None
    taxa_administracao: str | None = None
    taxa_administracao_maxima: str | None = None
    resumo_estrategias: str | None = None
    data_inicio: date | None = None
    fundo_custodiante_id: int | None = None


class CreateFundoSchema(BaseFundoSchema):
    indice_id: int
    tipo_id: int
    risco_id: int
    classificacao_id: int
    custodiante_id: int


class InstituicaoFinanceiraSchema(Schema):
    id: int
    nome: str

    @staticmethod
    def from_model(custodiante: InstituicaoFinanceira):
        return InstituicaoFinanceiraSchema(id=custodiante.id, nome=custodiante.nome)


class FundoCustodianteSchema(Schema):
    id: int
    nome: str

    @staticmethod
    def from_model(custodiante: FundoCustodiante):
        return FundoCustodianteSchema(id=custodiante.id, nome=custodiante.nome)


class FundoControladorSchema(Schema):
    id: int
    nome: str

    @staticmethod
    def from_model(custodiante: FundoControlador):
        return FundoControladorSchema(id=custodiante.id, nome=custodiante.nome)


class FundoAdministradorSchema(Schema):
    id: int
    nome: str

    @staticmethod
    def from_model(custodiante: FundoAdministrador):
        return FundoAdministradorSchema(id=custodiante.id, nome=custodiante.nome)


class LaminaEnviadaSchema(Schema):
    data_referencia: date
    posicao_arquivo: int


class AtualizarLaminasRequestSchema(Schema):
    fundo_id: int
    enviados: list[LaminaEnviadaSchema]
    removidos: list[int]


class LaminaSchema(Schema):
    id: int
    fundo_id: int
    arquivo_id: str
    data_referencia: date
    criado_em: datetime
    arquivo: ArquivoSchema


class FundoCategoriaDocumentoSchema(Schema):
    id: int
    nome: str


class FundoDocumentoSchema(Schema):
    id: int
    criado_em: datetime
    data_referencia: date
    arquivo: ArquivoSchema | ArquivoSemIDSchema
    titulo: str | None = None


class FundoClassificacaoDocumentosSchema(Schema):
    id: int
    nome: str


class DocumentosDoFundoSchema(Schema):
    classificacao: FundoClassificacaoDocumentosSchema
    arquivos: list[FundoDocumentoSchema]

    @staticmethod
    def agrupar(documentos: list[FundoDocumento], *, transmitir_id_arquivos=False):
        documentos_agrupados: dict[int, DocumentosDoFundoSchema] = {}

        for documento in documentos:
            categoria = documento.fundo_categoria_documento
            if categoria.id not in documentos_agrupados:
                documentos_agrupados[categoria.id] = DocumentosDoFundoSchema(
                    classificacao=FundoClassificacaoDocumentosSchema(
                        id=categoria.id, nome=categoria.nome
                    ),
                    arquivos=[],
                )
            documentos_agrupados[categoria.id].arquivos.append(
                FundoDocumentoSchema(
                    id=documento.id,
                    criado_em=documento.criado_em,
                    data_referencia=documento.data_referencia,
                    arquivo=(
                        ArquivoSchema.from_model(documento.arquivo)
                        if transmitir_id_arquivos
                        else ArquivoSemIDSchema.from_model(documento.arquivo)
                    ),
                    titulo=documento.titulo,
                )
            )

        listagem = [*documentos_agrupados.values()]
        listagem.sort(key=lambda docs: docs.classificacao.nome)
        return listagem


class IndicesBenchmarkSchema(Schema):
    id: int
    nome: str
    ordenacao: int


class FundoDistribuidorSchema(Schema):
    id: int
    nome: str
    link: str | None


class FundoSchema(BaseFundoSchema):
    _fundo: Fundo = PrivateAttr()

    id: int
    custodiante: FundoCustodianteSchema | None = None
    publicado: bool = False
    indices: list[IndicesBenchmarkSchema] = []
    documentos: list[DocumentosDoFundoSchema] = []
    mesa_responsavel: "MesaSchema | None" = None
    mesas_contribuidoras: list["MesaSchema"] = []
    caracteristicas_extras: list["FundoCaracteristicaExtraSchema"] = []
    detalhes_infos_publicas: "FundoDetalhesInformacoesPublicasSchema | None" = None
    distribuidores: list[FundoDistribuidorSchema] = []

    @staticmethod
    def from_model(fundo: Fundo):
        schema = FundoSchema(
            id=fundo.id,
            isin=fundo.isin,
            mnemonico=fundo.mnemonico,
            cnpj=fundo.cnpj,
            nome=fundo.nome,
            codigo_brit=fundo.codigo_brit,
            codigo_carteira=fundo.codigo_carteira,
            conta_cetip=fundo.conta_cetip,
            conta_selic=fundo.conta_selic,
            aberto_para_captacao=fundo.aberto_para_captacao,
            fundo_disponibilidade_id=fundo.fundo_disponibilidade_id,
            ticker_b3=fundo.ticker_b3,
            fundo_administrador_id=fundo.fundo_administrador_id,
            codigo_carteira_administrador=fundo.codigo_carteira_administrador,
            fundo_controlador_id=fundo.fundo_controlador_id,
            agencia_bancaria_custodia=fundo.agencia_bancaria_custodia,
            conta_aplicacao=fundo.conta_aplicacao,
            conta_resgate=fundo.conta_resgate,
            conta_movimentacao=fundo.conta_movimentacao,
            conta_tributada=fundo.conta_tributada,
            minimo_aplicacao=fundo.minimo_aplicacao,
            minimo_movimentacao=fundo.minimo_movimentacao,
            minimo_saldo=fundo.minimo_saldo,
            cotizacao_aplicacao=fundo.cotizacao_aplicacao,
            cotizacao_aplicacao_sao_dias_uteis=fundo.cotizacao_aplicacao_sao_dias_uteis,
            cotizacao_aplicacao_detalhes=fundo.cotizacao_aplicacao_detalhes,
            cotizacao_resgate=fundo.cotizacao_resgate,
            cotizacao_resgate_sao_dias_uteis=fundo.cotizacao_resgate_sao_dias_uteis,
            cotizacao_resgate_detalhes=fundo.cotizacao_resgate_detalhes,
            financeiro_aplicacao=fundo.financeiro_aplicacao,
            financeiro_aplicacao_sao_dias_uteis=fundo.financeiro_aplicacao_sao_dias_uteis,
            financeiro_aplicacao_detalhes=fundo.financeiro_aplicacao_detalhes,
            financeiro_resgate=fundo.financeiro_resgate,
            financeiro_resgate_sao_dias_uteis=fundo.financeiro_resgate_sao_dias_uteis,
            financeiro_resgate_detalhes=fundo.financeiro_resgate_detalhes,
            publico_alvo_id=fundo.publico_alvo_id,
            benchmark=fundo.benchmark,
            taxa_performance=fundo.taxa_performance,
            taxa_administracao=fundo.taxa_administracao,
            taxa_administracao_maxima=fundo.taxa_administracao_maxima,
            resumo_estrategias=fundo.resumo_estrategias,
            data_inicio=fundo.data_inicio,
            publicado=False,
            fundo_custodiante_id=fundo.fundo_custodiante_id,
            custodiante=(
                FundoCustodianteSchema.from_model(fundo.custodiante)
                if fundo.custodiante
                else None
            ),
            indices=[],
            documentos=[],
            mesa_responsavel=None,
            mesas_contribuidoras=[],
            caracteristicas_extras=[],
            distribuidores=[],
        )
        schema._fundo = fundo
        return schema

    def com_publicacao(self):
        self.publicado = self._fundo.fundo_site_institucional != None
        return self

    def com_documentos(self):
        self.documentos = DocumentosDoFundoSchema.agrupar(
            self._fundo.documentos, transmitir_id_arquivos=True
        )
        return self

    def com_indices(self):
        self.indices = [
            IndicesBenchmarkSchema(
                id=relacionamento.indice_benchmark.id,
                nome=relacionamento.indice_benchmark.nome,
                ordenacao=relacionamento.ordenacao,
            )
            for relacionamento in self._fundo.indices_benchmark
        ]
        return self

    def com_mesas(self):
        responsaveis = [mesa for mesa in self._fundo.mesas if mesa.responsavel]
        responsavel = responsaveis[0].mesa if len(responsaveis) > 0 else None
        contribuidoras = [mesa for mesa in self._fundo.mesas if not mesa.responsavel]
        self.mesa_responsavel = (
            MesaSchema(
                id=responsavel.id,
                nome=responsavel.nome,
                sobre=responsavel.sobre or "",
                ordenacao=responsavel.ordenacao,
            )
            if responsavel
            else None
        )
        self.mesas_contribuidoras = [
            MesaSchema(
                id=relacionamento.mesa.id,
                nome=relacionamento.mesa.nome,
                sobre=relacionamento.mesa.sobre or "",
                ordenacao=relacionamento.mesa.ordenacao,
            )
            for relacionamento in contribuidoras
        ]
        return self

    def com_caracteristicas_extras(self):
        self.caracteristicas_extras = [
            FundoCaracteristicaExtraSchema(
                id=relacionamento.caracteristica_extra.id,
                nome=relacionamento.caracteristica_extra.nome,
            )
            for relacionamento in self._fundo.caracteristicas_extras
        ]
        return self

    def com_detalhes_publicacao(self):
        self.detalhes_infos_publicas = (
            FundoDetalhesInformacoesPublicasSchema.from_model(
                self._fundo.fundo_site_institucional, com_documentos=True
            )
            if self._fundo.fundo_site_institucional
            else None
        )
        return self

    def com_distribuidores(self):
        self.distribuidores = [
            FundoDistribuidorSchema(
                id=distribuidor.distribuidor.id,
                nome=distribuidor.distribuidor.nome,
                link=distribuidor.distribuidor.link,
            )
            for distribuidor in self._fundo.distribuidores
        ]
        return self


class FundoIndiceBenchmarkSchema(Schema):
    nome: str
    ordenacao: int


class FundoCotaRentabilidadeSchema(Schema):
    fundo_id: int
    data_posicao: date
    preco_cota: float
    rentabilidade_dia: float
    rentabilidade_mes: float
    rentabilidade_ano: float
    rentabilidade_12meses: float
    rentabilidade_24meses: float
    rentabilidade_36meses: float


class FundoPatrimonioLiquidoRentabilidadeSchema(Schema):
    fundo_id: int
    data_posicao: date
    patrimonio_liquido: float
    media_12meses: float
    media_24meses: float
    media_36meses: float


class UpdateFundo(BaseFundoSchema):
    indices: list[FundoIndiceBenchmarkSchema] = []
    mesa_responsavel: int | None = None
    mesas_contribuidoras: list[int] = []
    caracteristicas_extras: list[int] = []
    remover_documentos: list[int]


class MetadadosDocumentosFundoSchema(Schema):
    posicao_arquivo: int
    titulo: str
    data_referencia: date
    fundo_categoria_id: int


class AtualizacaoInternaFundosSchema(Schema):
    metadados_documentos: list[MetadadosDocumentosFundoSchema]
    atualizacao_fundo: UpdateFundo


class CreateFundoResponse(Schema):
    id: int


UpdateFundoResponse = CreateFundoResponse


class FundoInstitucionalClassificacaoSchema(Schema):
    id: int
    nome: str


class FundoInstitucionalTipoSchema(Schema):
    id: int
    nome: str


class FundoInstitucionalSchema(Schema):
    id: int
    fundo_id: int
    nome: str
    apelido: str = ""
    classificacao: FundoInstitucionalClassificacaoSchema
    tipo: FundoInstitucionalTipoSchema

    @staticmethod
    def from_model(fundo: FundoSiteInstitucional):
        clsf = fundo.classificacao
        tipo = fundo.tipo
        return FundoInstitucionalSchema(
            id=fundo.id,
            fundo_id=fundo.id,
            nome=fundo.nome,
            classificacao=FundoInstitucionalClassificacaoSchema(
                id=clsf.id,
                nome=clsf.nome,
            ),
            tipo=FundoInstitucionalTipoSchema(
                id=tipo.id,
                nome=tipo.nome,
            ),
        )


class InsertFundoInstitucionalSchema(Schema):
    fundo_id: int
    classificacao_id: int
    tipo_id: int
    apelido: str = ""


class UpdateFundoInstitucionalSchema(InsertFundoInstitucionalSchema):
    id: int


class FundosSiteInstitucionalTransacaoSchema(Schema):
    deletados: list[int]
    alterados: list[UpdateFundoInstitucionalSchema]
    inseridos: list[InsertFundoInstitucionalSchema]


class FundoInformacoesPublicasSchema(Schema):
    id: int
    nome: str


class FundoDetalhesInformacoesPublicasSchema(Schema):
    _fundo_site_institucional: FundoSiteInstitucional = PrivateAttr()

    id: int
    ordenacao: int
    fundo_id: int
    nome: str
    cnpj: str
    aberto_para_captacao: bool
    ticker_b3: str | None = None
    cotizacao_resgate: int | None = None
    cotizacao_resgate_sao_dias_uteis: bool | None = None
    cotizacao_resgate_detalhes: str | None = None
    financeiro_resgate: int | None = None
    financeiro_resgate_sao_dias_uteis: bool | None = None
    financeiro_resgate_detalhes: str | None = None
    publico_alvo_id: int | None = None
    benchmark: str | None = None
    taxa_performance: str | None = None
    taxa_administracao: str | None = None
    taxa_administracao_maxima: str | None = None
    resumo_estrategias: str | None = None
    mesa_id: int
    mesa: "MesaSchema"
    atualizado_em: datetime
    data_inicio: date | None = None

    classificacao: FundoInstitucionalClassificacaoSchema
    tipo: FundoInstitucionalTipoSchema
    indices_benchmark: list[IndicesBenchmarkSchema] = []
    caracteristicas_extras: list["FundoCaracteristicaExtraSchema"] = []
    documentos: list[DocumentosDoFundoSchema] = []
    distribuidores: list[FundoDistribuidorSchema] = []

    @staticmethod
    def from_model(fundo: FundoSiteInstitucional, *, com_documentos=False):
        classificacao = fundo.classificacao
        tipo = fundo.tipo
        indices_benchmark = fundo.indices_benchmark
        schema = FundoDetalhesInformacoesPublicasSchema(
            id=fundo.id,
            data_inicio=fundo.data_inicio,
            ordenacao=fundo.ordenacao,
            fundo_id=fundo.fundo_id,
            atualizado_em=fundo.atualizado_em,
            nome=fundo.nome,
            cnpj=fundo.cnpj,
            aberto_para_captacao=fundo.aberto_para_captacao,
            ticker_b3=fundo.ticker_b3,
            cotizacao_resgate=fundo.cotizacao_resgate,
            cotizacao_resgate_sao_dias_uteis=fundo.cotizacao_resgate_sao_dias_uteis,
            cotizacao_resgate_detalhes=fundo.cotizacao_resgate_detalhes,
            financeiro_resgate=fundo.financeiro_resgate,
            financeiro_resgate_sao_dias_uteis=fundo.financeiro_resgate_sao_dias_uteis,
            financeiro_resgate_detalhes=fundo.financeiro_resgate_detalhes,
            publico_alvo_id=fundo.publico_alvo_id,
            benchmark=fundo.benchmark,
            taxa_performance=fundo.taxa_performance,
            taxa_administracao=fundo.taxa_administracao,
            taxa_administracao_maxima=fundo.taxa_administracao_maxima,
            resumo_estrategias=fundo.resumo_estrategias,
            mesa_id=fundo.mesa_id,
            caracteristicas_extras=[
                FundoCaracteristicaExtraSchema(
                    id=relacionamento.caracteristica_extra.id,
                    nome=relacionamento.caracteristica_extra.nome,
                )
                for relacionamento in fundo.caracteristicas_extras
            ],
            indices_benchmark=[
                IndicesBenchmarkSchema(
                    id=indice.indice_benchmark.id,
                    nome=indice.indice_benchmark.nome,
                    ordenacao=indice.ordenacao,
                )
                for indice in indices_benchmark
            ],
            classificacao=FundoInstitucionalClassificacaoSchema(
                id=classificacao.id, nome=classificacao.nome
            ),
            tipo=FundoInstitucionalTipoSchema(id=tipo.id, nome=tipo.nome),
            documentos=(
                DocumentosDoFundoSchema.agrupar(
                    [
                        fundo_documento.fundo_documento
                        for fundo_documento in fundo.fundos_documentos
                    ]
                )
                if com_documentos
                else []
            ),
            mesa=MesaSchema(
                id=fundo.mesa.id,
                nome=fundo.mesa.nome,
                sobre="",
                ordenacao=fundo.mesa.ordenacao,
            ),
        )

        schema._fundo_site_institucional = fundo
        return schema

    def com_distribuidores(self):
        self.distribuidores = [
            FundoDistribuidorSchema(
                id=distribuidor.distribuidor.id,
                nome=distribuidor.distribuidor.nome,
                link=distribuidor.distribuidor.link,
            )
            for distribuidor in self._fundo_site_institucional.distribuidores
        ]
        return self


class FundoCaracteristicaExtraSchema(Schema):
    id: int
    nome: str


class PostDetalhesFundoSiteInstitucionalSchema(Schema):
    nome: str
    aberto_para_captacao: bool
    ticker_b3: str | None
    cotizacao_resgate: int | None
    cotizacao_resgate_sao_dias_uteis: bool | None
    cotizacao_resgate_detalhes: str | None
    financeiro_resgate: int | None
    financeiro_resgate_sao_dias_uteis: bool | None
    financeiro_resgate_detalhes: str | None
    publico_alvo_id: int
    taxa_performance: str | None
    taxa_administracao: str | None
    site_institucional_classificacao_id: int
    site_institucional_tipo_id: int
    mesa_id: int


class PatchDetalhesFundoSiteInstitucionalSchema(Schema):
    nome: Optional[str] = None
    aberto_para_captacao: Optional[bool] = None
    ticker_b3: Optional[str | None] = None
    cotizacao_resgate: Optional[int] = None
    cotizacao_resgate_sao_dias_uteis: Optional[bool] = None
    cotizacao_resgate_detalhes: Optional[str] = None
    financeiro_resgate: Optional[int] = None
    financeiro_resgate_sao_dias_uteis: Optional[bool] = None
    financeiro_resgate_detalhes: Optional[str] = None
    publico_alvo_id: Optional[int] = None
    benchmark: Optional[str | None] = None
    taxa_performance: Optional[str | None] = None
    taxa_administracao: Optional[str | None] = None
    taxa_administracao_maxima: Optional[str | None] = None
    resumo_estrategias: Optional[str | None] = None
    site_institucional_classificacao_id: Optional[int] = None
    site_institucional_tipo_id: Optional[int] = None
    mesa_id: Optional[int] = None


class IndiceBenchmarkSchema(Schema):
    indice_benchmark_id: int
    ordenacao: int


class PostFundoSiteInstitucionalSchema(Schema):
    fundo_id: int
    detalhes: PostDetalhesFundoSiteInstitucionalSchema
    caracteristicas_extras_ids: Optional[list[int]] = None
    documentos_ids: Optional[list[int]] = None
    indices_benchmark: Optional[list[IndiceBenchmarkSchema]] = None
    distribuidores_ids: Optional[list[int]] = None


class PatchFundoSiteInstitucionalSchema(Schema):
    detalhes: Optional[PatchDetalhesFundoSiteInstitucionalSchema] = None
    caracteristicas_extras_para_publicacao_ids: Optional[list[int]] = None
    caracteristicas_extras_para_despublicacao_ids: Optional[list[int]] = None
    documentos_para_publicacao_ids: Optional[list[int]] = None
    documentos_para_despublicacao_ids: Optional[list[int]] = None
    indices_benchmark_para_publicacao: Optional[list[IndiceBenchmarkSchema]] = None
    indices_benchmark_para_despublicacao: Optional[list[IndiceBenchmarkSchema]] = None
    distribuidores_para_publicacao_ids: Optional[list[int]] = None
    distribuidores_para_despublicacao_ids: Optional[list[int]] = None


class PublicarDetalhesResponseSchema(Schema):
    message: str


class InformacaoMaterialSchema(Schema):
    fundo_id: int
    data_referencia: date
    titulo_material: str
    posicao_arquivo: int


class PublicacaoMateriaisMassaSchema(Schema):
    informacoes: list[InformacaoMaterialSchema]


# Resolvendo dependências circulares
from modules.mesas.schema import MesaSchema

FundoSchema.model_rebuild()
