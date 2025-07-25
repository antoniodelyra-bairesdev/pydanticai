from collections import UserList
from datetime import date
from decimal import Decimal
from pydantic import BaseModel as Schema


class ColetaIndiceSchema(Schema):
    fonte: str
    moeda: str
    indice: str


class ColetaIndiceCotacaoSchema(Schema):
    data_referente: date
    nome_indice: str
    cotacao: Decimal
    moeda: str
    fonte_dado: str


class ColetaIndiceCotacaoSchemaCollection(UserList[ColetaIndiceCotacaoSchema]):
    def get_indice_ultima_cotacao(
        self, nome_indice: str
    ) -> ColetaIndiceCotacaoSchema | None:
        for cotacao in reversed(self.data):
            if cotacao.nome_indice == nome_indice:
                return cotacao

        return None


class AvisoSchema(Schema):
    mensagem: str
    indices_afetados: list[str]


class ResponseSchema(Schema):
    avisos: list[AvisoSchema]
    cotacoes: list[ColetaIndiceCotacaoSchema]
