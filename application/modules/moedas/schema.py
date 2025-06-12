from datetime import date
from decimal import Decimal
from pydantic import BaseModel as Schema

from .model import Moeda, MoedaCotacao
from modules.fontes_dados.schema import FonteDadosSchema


class MoedaSchema(Schema):
    id: int
    nome: str
    codigo: str
    simbolo: str

    @staticmethod
    def from_model(model: Moeda) -> "MoedaSchema":
        return MoedaSchema(
            id=model.id,
            nome=model.nome,
            codigo=model.codigo,
            simbolo=model.simbolo,
        )


class MoedaCotacaoSchema(Schema):
    id: int
    data_referente: date
    cotacao: Decimal

    moeda: MoedaSchema
    fonte_dado: FonteDadosSchema

    @staticmethod
    def from_model(model: MoedaCotacao) -> "MoedaCotacaoSchema":
        return MoedaCotacaoSchema(
            id=model.id,
            data_referente=model.data_referente,
            cotacao=model.cotacao,
            moeda=MoedaSchema.from_model(model.moeda),
            fonte_dado=FonteDadosSchema.from_model(model.fonte_dado),
        )
