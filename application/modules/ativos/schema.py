from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import (
        AtivoIPCA,
        AtivoFluxo,
        Ativo,
        AtivoFluxoTipo,
        Emissor,
    )


from pydantic import BaseModel as Schema
from datetime import date


class TipoEventoSchema(Schema):
    id: int
    nome: str
    tokens: list[str]

    @staticmethod
    def from_model(model: AtivoFluxoTipo):
        return TipoEventoSchema(
            id=model.id, nome=model.nome, tokens=model.tokens.split(",")
        )


class TipoAtivosSchema(Schema):
    id: int
    nome: str


class IndiceAtivosSchema(Schema):
    id: int
    nome: str


class AtivoIPCASchema(Schema):
    ipca_2_meses: bool
    ipca_negativo: bool
    mesversario: int

    @staticmethod
    def from_model(model: AtivoIPCA):
        return AtivoIPCASchema(
            ipca_2_meses=model.ipca_2_meses,
            ipca_negativo=model.ipca_negativo,
            mesversario=model.mesversario,
        )


class FluxoSchema(Schema):
    id: int
    data_pagamento: date
    tipo_evento: str

    data_evento: date | None = None
    percentual: float | None = None
    pu_evento: float | None = None
    pu_calculado: float | None = None

    @staticmethod
    def from_model(model: AtivoFluxo):
        return FluxoSchema(
            id=model.id,
            data_pagamento=model.data_pagamento,
            tipo_evento=model.tipo.nome,
            data_evento=model.data_evento,
            percentual=model.percentual,
            pu_calculado=model.pu_calculado,
        )


class AtivoItemListaSchema(Schema):
    codigo: str
    emissor: str
    tipo: str
    indice: str
    apelido: str | None = None
    ativo_ipca: AtivoIPCASchema | None = None
    fluxos: list[FluxoSchema] = []
    isin: str | None = None

    @staticmethod
    def from_model(
        model: Ativo, *, acessar_fluxos: bool = True, acessar_info_ipca=True
    ):
        return AtivoItemListaSchema(
            codigo=model.codigo,
            emissor=model.emissor.nome,
            tipo=model.tipo.nome,
            indice=model.indice.nome,
            apelido=model.apelido,
            fluxos=(
                [FluxoSchema.from_model(fluxo) for fluxo in model.fluxos]
                if acessar_fluxos
                else []
            ),
            ativo_ipca=(
                (
                    AtivoIPCASchema.from_model(model.ativo_ipca)
                    if model.ativo_ipca
                    else None
                )
                if acessar_info_ipca
                else None
            ),
            isin=model.isin,
        )


class DeleteAtivoSchema(Schema):
    codigo: str


class UpdateAtivoIPCASchema(Schema):
    pass


# -------------------------------------------------------------------


class InsertEventSchema(Schema):
    tipo_id: int

    data_pagamento: date
    percentual: float | None = None

    pu_evento: float | None = None
    pu_calculado: float | None = None


class IPCAAssetSchema(Schema):
    mesversario: int
    ipca_2_meses: bool
    ipca_negativo: bool


class InsertAssetSchema(Schema):
    codigo: str
    emissor_id: int
    indice_id: int
    tipo_id: int

    taxa: float
    valor_emissao: float
    data_emissao: date
    inicio_rentabilidade: date
    data_vencimento: date

    apelido: str | None = None
    isin: str | None = None
    serie: int | None = None
    emissao: int | None = None

    ativo_ipca: IPCAAssetSchema | None = None

    fluxos: list[InsertEventSchema]


class UpdateEventSchema2(InsertEventSchema):
    id: int


class EventTransactionSchema(Schema):
    deleted: list[int]
    modified: list[UpdateEventSchema2]
    added: list[InsertEventSchema]


class UpdateAssetSchema(InsertAssetSchema):
    fluxos: EventTransactionSchema


class AssetTransactionSchema(Schema):
    deleted: list[str]
    modified: list[UpdateAssetSchema]
    added: list[InsertAssetSchema]

    # @model_validator(mode="after")
    # def check_conflitos_operacao(self):
    #     deletados = self.delete or []
    #     atualizados = self.update or []
    #     inseridos = self.insert or []

    #     codigos_deletados = {*deletados}
    #     codigos_originais_antes_da_atualizacao = {
    #         ativo.codigo_original for ativo in atualizados
    #     }
    #     codigos_atualizados_apos_atualizacao = {ativo.codigo for ativo in atualizados}
    #     codigos_inseridos = {ativo.codigo for ativo in inseridos}

    #     if len(deletados) != len(codigos_deletados):
    #         raise ValueError("Você não pode remover um ativo mais de uma vez")

    #     if len(atualizados) != len(codigos_originais_antes_da_atualizacao):
    #         raise ValueError("Você não pode atualizar um ativo mais de uma vez")

    #     if len(atualizados) != len(codigos_atualizados_apos_atualizacao):
    #         raise ValueError(
    #             "Você não pode atualizar mais de um ativo para o mesmo código"
    #         )

    #     if len(inseridos) != len(codigos_inseridos):
    #         raise ValueError("Você não pode inserir um ativo mais de uma vez")

    #     for codigo_original in codigos_originais_antes_da_atualizacao:
    #         if codigo_original in codigos_deletados:
    #             raise ValueError(
    #                 "Você não pode atualizar um ativo cujo código original foi deletado na mesma operação"
    #             )
    #     for codigo_inserido in codigos_inseridos:
    #         if codigo_inserido in codigos_atualizados_apos_atualizacao:
    #             raise ValueError(
    #                 "Você não pode inserir um ativo com o novo código de um outro ativo na mesma operação"
    #             )
    #         if codigo_inserido in codigos_deletados:
    #             raise ValueError(
    #                 'Você não pode inserir um ativo com o código de um ativo que foi removido na mesma operação. Utilize o campo "update" para isso'
    #             )

    #     return self


# -------------------------------------------------------------------


class InsertSetorSchema(Schema):
    nome: str
    sistema_icone: str | None = None


class SetorSchema(InsertSetorSchema):
    id: int


class SetorTransactionSchema(Schema):
    modified: list[SetorSchema]
    added: list[InsertSetorSchema]


class InsertGrupoSchema(Schema):
    nome: str


class GrupoSchema(InsertGrupoSchema):
    id: int


class GrupoTransactionSchema(Schema):
    modified: list[GrupoSchema]
    added: list[InsertGrupoSchema]


class InsertEmissorSchema(Schema):
    nome: str
    cnpj: str

    codigo_cvm: int | None = None
    tier: int | None = None

    grupo_id: int | None = None
    setor_id: int | None = None
    analista_credito_id: int | None = None


class UpdateEmissorSchema(InsertEmissorSchema):
    id: int


class EmissorTransactionSchema(Schema):
    modified: list[UpdateEmissorSchema]
    added: list[InsertEmissorSchema]


class UserSchema(Schema):
    id: int
    email: str
    nome: str


class AnalistaSchema(Schema):
    id: int
    user: UserSchema


class EmissorSchema(Schema):
    id: int
    cnpj: str
    nome: str
    grupo: GrupoSchema | None = None
    setor: SetorSchema | None = None
    analista_credito: AnalistaSchema | None = None
    codigo_cvm: int | None = None
    tier: int | None = None

    @staticmethod
    def from_model(model: Emissor):
        return EmissorSchema(
            id=model.id,
            cnpj=model.cnpj,
            nome=model.nome,
            codigo_cvm=model.codigo_cvm,
            tier=model.tier,
            grupo=(
                GrupoSchema(id=model.grupo.id, nome=model.grupo.nome)
                if model.grupo
                else None
            ),
            setor=(
                SetorSchema(
                    id=model.setor.id,
                    nome=model.setor.nome,
                    sistema_icone=(
                        model.setor.icone.icone if model.setor.icone else None
                    ),
                )
                if model.setor
                else None
            ),
            analista_credito=(
                AnalistaSchema(
                    id=model.analista_credito.id,
                    user=UserSchema(
                        id=model.analista_credito.user.id,
                        email=model.analista_credito.user.email,
                        nome=model.analista_credito.user.nome,
                    ),
                )
                if model.analista_credito
                else None
            ),
        )
