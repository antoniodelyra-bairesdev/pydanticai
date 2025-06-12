from pydantic import BaseModel as Schema

from .model import Fornecedor


class FornecedorSchema(Schema):
    id: int
    nome: str

    @staticmethod
    def from_model(model: Fornecedor) -> "FornecedorSchema":
        return FornecedorSchema(id=model.id, nome=model.nome)
