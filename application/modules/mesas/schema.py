from pydantic import BaseModel as Schema

from .model import Mesa

from modules.fundos.schema import FundoInformacoesPublicasSchema


class MesaSchema(Schema):
    id: int
    nome: str
    sobre: str
    ordenacao: int

    fundos_responsavel: list[FundoInformacoesPublicasSchema] = []
    fundos_contribuidora: list[FundoInformacoesPublicasSchema] = []

    @staticmethod
    def a_partir_de_resultado_geral(mesas: list[Mesa]):
        return [
            MesaSchema(
                id=mesa.id,
                nome=mesa.nome,
                sobre=mesa.sobre or "",
                ordenacao=mesa.ordenacao,
                fundos_responsavel=[
                    FundoInformacoesPublicasSchema(
                        id=associacao.fundo.id,
                        nome=associacao.fundo.nome,
                    )
                    for associacao in mesa.fundos
                    if associacao.responsavel
                ],
                fundos_contribuidora=[
                    FundoInformacoesPublicasSchema(
                        id=associacao.fundo.id, nome=associacao.fundo.nome
                    )
                    for associacao in mesa.fundos
                    if not associacao.responsavel
                ],
            )
            for mesa in mesas
        ]
