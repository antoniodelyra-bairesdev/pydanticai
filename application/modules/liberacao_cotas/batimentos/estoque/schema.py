from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel as Schema, computed_field

from modules.util.api_warning import APIWarning


class AtivoCarteiraSchema(Schema):
    isin: str | None
    codigo: str
    quantidade: Decimal
    preco_unitario_posicao: Decimal
    tipo: Literal["RendaFixa", "RendaVariavel", "Futuro", "CotasFundos"]

    @computed_field
    @property
    def financeiro(self) -> Decimal:
        return self.quantidade * self.preco_unitario_posicao

    class Config:
        arbitrary_types_allowed = True


class ComparacaoEstoqueSchema(Schema):
    fundo_codigo_britech: str
    fundo_codigo_administrador: str
    fundo_cnpj: str
    fundo_nome: str
    data_referente: date
    ativo_xml: AtivoCarteiraSchema | None
    ativo_britech: AtivoCarteiraSchema | None
    tipo_ativo: Literal["RendaFixa", "RendaVariavel", "Futuro", "CotasFundos"]
    diferenca_pu: Decimal | None
    diferenca_quantidade: Decimal | None
    diferenca_financeiro: Decimal | None


class ResponseSchema(Schema):
    estoque: list[ComparacaoEstoqueSchema]
    warnings: list[APIWarning]
