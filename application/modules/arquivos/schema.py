from pydantic import BaseModel as Schema

from .model import Arquivo


class ArquivoSchema(Schema):
    id: str
    nome: str
    extensao: str

    @staticmethod
    def from_model(model: Arquivo):
        return ArquivoSchema(id=model.id, nome=model.nome, extensao=model.extensao)


class ArquivoSemIDSchema(Schema):
    nome: str
    extensao: str

    @staticmethod
    def from_model(model: Arquivo):
        return ArquivoSemIDSchema(nome=model.nome, extensao=model.extensao)
