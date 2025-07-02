from datetime import date
from decimal import Decimal
from pydantic import BaseModel as Schema

from .model import Indice, IndiceIdentificador, IndiceCotacao
from modules.medidas.schema import MedidaSchema
from modules.moedas.schema import MoedaSchema
from modules.fontes_dados.schema import FonteDadosSchema
from modules.rotinas.indices.coleta.schema import ColetaIndiceCotacaoSchema


class IndiceSchema(Schema):
    id: int
    nome: str
    descricao: str | None
    is_sintetico: bool
    data_inicio_coleta: date
    atraso_coleta_dias: int

    moeda: MoedaSchema
    fonte_dados: FonteDadosSchema
    medida: MedidaSchema
    identificadores: list["IndiceIdentificadorSchema"]

    @staticmethod
    def from_model(model: Indice) -> "IndiceSchema":
        identificadores_schema = []
        for identificador in model.get_identificadores_collection():
            identificadores_schema.append(
                IndiceIdentificadorSchema.from_model(identificador)
            )

        return IndiceSchema(
            id=model.id,
            nome=model.nome,
            descricao=model.descricao,
            is_sintetico=model.is_sintetico,
            data_inicio_coleta=model.data_inicio_coleta,
            atraso_coleta_dias=model.atraso_coleta_dias,
            moeda=MoedaSchema.from_model(model.moeda),
            fonte_dados=FonteDadosSchema.from_model(model.fonte_dado),
            medida=MedidaSchema.from_model(model.medida),
            identificadores=identificadores_schema,
        )


class IndiceIdentificadorSchema(Schema):
    id: int
    codigo: str
    descricao: str | None

    fonte_dado: FonteDadosSchema

    @staticmethod
    def from_model(model: IndiceIdentificador) -> "IndiceIdentificadorSchema":
        return IndiceIdentificadorSchema(
            id=model.id,
            codigo=model.codigo,
            descricao=model.descricao,
            fonte_dado=FonteDadosSchema.from_model(model.fonte_dado),
        )


class IndiceCotacaoSchema(Schema):
    id: int | None
    data_referente: date
    cotacao: Decimal

    indice_id: int
    indice: str
    fonte_dado_id: int
    fonte_dado: str
    moeda_id: int
    moeda: str

    @staticmethod
    def from_model(model: IndiceCotacao) -> "IndiceCotacaoSchema":
        return IndiceCotacaoSchema(
            id=model.id,
            data_referente=model.data_referente,
            cotacao=model.cotacao,
            indice_id=model.indice_id,
            indice=model.indice.nome,
            fonte_dado_id=model.fonte_dado_id,
            fonte_dado=model.fonte_dados.get_nome_completo_fonte_dados(),
            moeda_id=model.moeda_id,
            moeda=model.moeda.codigo,
        )


class PostCotacoesAvisoSchema(Schema):
    mensagem: str
    indice_cotacao_afetada: ColetaIndiceCotacaoSchema


class PostCotacoesBodySchema(Schema):
    cotacoes: list[ColetaIndiceCotacaoSchema]


class PostCotacoesResponseSchema(Schema):
    cotacoes_nao_inseridas: list[ColetaIndiceCotacaoSchema]
    avisos: list[PostCotacoesAvisoSchema]
    cotacoes_inseridas: list[IndiceCotacaoSchema]


class PostCotacoesSinteticosBaseAvisoSchema(Schema):
    mensagem: str
    indice_afetado: str


class PostCotacoesSinteticosBaseResponseSchema(Schema):
    avisos: list[PostCotacoesSinteticosBaseAvisoSchema]
    cotacoes_inseridas: list[IndiceCotacaoSchema]
