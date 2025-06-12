from pydantic import BaseModel as Schema

from .model import FonteDados
from modules.fornecedores.schema import FornecedorSchema


class FonteDadosSchema(Schema):
    id: int
    nome: str
    fornecedor: FornecedorSchema

    @staticmethod
    def from_model(model: FonteDados) -> "FonteDadosSchema":
        return FonteDadosSchema(
            id=model.id,
            nome=model.nome,
            fornecedor=FornecedorSchema.from_model(model.fornecedor),
        )
