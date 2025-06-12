from pydantic import BaseModel as Schema

from .model import Medida


class MedidaSchema(Schema):
    id: int
    nome: str
    descricao: str | None
    abreviacao: str | None

    @staticmethod
    def from_model(model: Medida) -> "MedidaSchema":
        return MedidaSchema(
            id=model.id,
            nome=model.nome,
            descricao=model.descricao,
            abreviacao=model.abreviacao,
        )
