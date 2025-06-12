from dataclasses import dataclass
from datetime import date, datetime
import logging
from typing import NotRequired, TypedDict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import (
    BinaryExpression,
    ColumnElement,
    UnaryExpression,
    insert,
    select,
    delete,
    update,
)
from sqlalchemy.orm.strategy_options import contains_eager
from sqlalchemy.sql.functions import count

from modules.auth.model import Usuario

from .schema import (
    GrupoSchema,
    IPCAAssetSchema,
    InsertAssetSchema,
    InsertEmissorSchema,
    InsertGrupoSchema,
    InsertSetorSchema,
    SetorSchema,
    UpdateAssetSchema,
    UpdateEmissorSchema,
)
from .model import (
    AnalistaCredito,
    AtivoFluxo,
    AtivoIPCA,
    AtivoIndice,
    Ativo,
    AtivoFluxoTipo,
    AtivoTipo,
    Emissor,
    EmissorGrupo,
    EmissorSetor,
    EmissorSetorIcone,
)


@dataclass
class AtivosRepository:
    db: AsyncSession

    class AssetDict(TypedDict):
        codigo: str
        valor_emissao: float
        data_emissao: date
        inicio_rentabilidade: date
        data_vencimento: date
        taxa: float
        atualizacao: datetime
        cadastro_manual: bool
        emissor_id: int
        tipo_id: int
        indice_id: int
        apelido: NotRequired[str | None]
        isin: NotRequired[str | None]
        serie: NotRequired[int | None]
        emissao: NotRequired[int | None]

    class EventDict(TypedDict):
        ativo_codigo: str
        data_pagamento: date
        ativo_fluxo_tipo_id: int
        data_evento: date
        percentual: NotRequired[float | None]
        pu_evento: NotRequired[float | None]
        pu_calculado: NotRequired[float | None]

    class UpdateEventDict(EventDict):
        id: int

    class InsertAtivoIPCADict(TypedDict):
        ativo_codigo: str
        mesversario: int
        ipca_negativo: bool
        ipca_2_meses: bool

    async def tipo_evento(self, supported: bool = True):
        results = await self.db.execute(
            select(AtivoFluxoTipo).where(AtivoFluxoTipo.id.in_({1, 2, 3, 8}))
            if supported
            else select(AtivoFluxoTipo)
        )
        return results.scalars().all()

    async def tipo_ativos(self):
        results = await self.db.execute(select(AtivoTipo))
        return results.scalars().all()

    async def indices(self):
        results = await self.db.execute(select(AtivoIndice))
        return results.scalars().all()

    async def total_ativos(self):
        total = await self.db.execute(select(count()).select_from(Ativo))
        return total.scalars().one()

    async def total_eventos(self):
        total = await self.db.execute(select(count()).select_from(AtivoFluxo))
        return total.scalars().one()

    async def lista_ativos(
        self,
        deslocamento: int = 0,
        quantidade: int = 35,
        ordenacao: list[UnaryExpression] = [Ativo.codigo.asc()],
        filtro: list[ColumnElement[bool] | BinaryExpression[bool]] = [],
    ):
        total = await self.db.execute(
            select(count())
            .select_from(Ativo)
            .join(Ativo.indice)
            .join(Ativo.tipo)
            .join(Ativo.emissor)
            .join(Ativo.ativo_ipca, isouter=True)
            .where(*filtro)
        )
        query = (
            select(Ativo)
            .join(Ativo.indice)
            .join(Ativo.tipo)
            .join(Ativo.emissor)
            .join(Ativo.ativo_ipca, isouter=True)
            .options(
                contains_eager(Ativo.indice),
                contains_eager(Ativo.tipo),
                contains_eager(Ativo.emissor),
                contains_eager(Ativo.ativo_ipca),
                selectinload(Ativo.fluxos).selectinload(AtivoFluxo.tipo),
            )
            .where(*filtro)
            .order_by(*ordenacao)
            .offset(deslocamento)
            .limit(quantidade)
        )
        results = await self.db.execute(query)

        return (
            results.scalars().all(),
            total.unique().scalar() or 0,
        )

    async def lista_eventos(
        self,
        deslocamento: int = 0,
        quantidade: int = 35,
        ordenacao: list[UnaryExpression] = [AtivoFluxo.id.asc()],
        filtro: list[ColumnElement[bool] | BinaryExpression[bool]] = [],
    ):
        total = await self.db.execute(
            select(count()).select_from(AtivoFluxo).join(AtivoFluxo.tipo).where(*filtro)
        )
        query_eventos = (
            select(AtivoFluxo)
            .join(AtivoFluxo.tipo)
            .options(contains_eager(AtivoFluxo.tipo))
            .where(*filtro)
            .order_by(*ordenacao)
            .offset(deslocamento)
            .limit(quantidade)
        )
        query_ativos = (
            select(Ativo)
            .join(Ativo.indice)
            .join(Ativo.tipo)
            .join(Ativo.emissor)
            .join(Ativo.ativo_ipca, isouter=True)
            .join(Ativo.fluxos)
            .join(AtivoFluxo.tipo)
            .options(
                contains_eager(Ativo.indice),
                contains_eager(Ativo.tipo),
                contains_eager(Ativo.emissor),
                contains_eager(Ativo.ativo_ipca),
            )
            .where(*filtro)
            .order_by(*ordenacao)
            .offset(deslocamento)
            .limit(quantidade)
        )
        eventos = await self.db.execute(query_eventos)
        ativos = await self.db.execute(query_ativos)
        return (
            ativos.unique().scalars().all(),
            eventos.scalars().all(),
            total.unique().scalar() or 0,
        )

    async def lista_codigos(self):
        results = await self.db.execute(select(Ativo.codigo))
        return results.scalars().all()

    async def nomes_emissores(self):
        results = await self.db.execute(select(Emissor.id, Emissor.nome))
        return results.all()

    async def ativo(self, codigo: str):
        result = await self.db.execute(
            select(Ativo)
            .options(
                selectinload(Ativo.indice),
                selectinload(Ativo.tipo),
                selectinload(Ativo.emissor),
                selectinload(Ativo.fluxos).selectinload(AtivoFluxo.tipo),
            )
            .where(Ativo.codigo == codigo)
        )
        return result.scalar()

    async def transacao(
        self,
        deletar: list[str],
        atualizar: list[UpdateAssetSchema],
        inserir: list[InsertAssetSchema],
    ):
        async with self.db.begin_nested():
            await self.deletar_ativos(deletar)
            await self.atualizar_ativos(atualizar)
            await self.inserir_ativos(inserir)

    async def deletar_ativos(self, deletar: list[str]):
        async with self.db.begin_nested():
            await self.db.execute(delete(Ativo).where(Ativo.codigo.in_(deletar)))

    async def atualizar_ativos(self, atualizar: list[UpdateAssetSchema]):
        async with self.db.begin_nested():
            atualizar_ativos: list[AtivosRepository.AssetDict] = []

            novos_eventos: list[AtivosRepository.EventDict] = []
            atualizar_eventos: list[AtivosRepository.UpdateEventDict] = []
            remover_eventos: list[int] = []

            novos_ativos_ipca: list[AtivosRepository.InsertAtivoIPCADict] = []
            remover_ativos_ipca: list[str] = []

            for ativo in atualizar:
                atualizar_ativos.append(
                    {
                        "codigo": ativo.codigo,
                        "apelido": ativo.apelido,
                        "atualizacao": datetime.today(),
                        "cadastro_manual": True,
                        "data_emissao": ativo.data_emissao,
                        "data_vencimento": ativo.data_vencimento,
                        "emissao": ativo.emissao,
                        "emissor_id": ativo.emissor_id,
                        "indice_id": ativo.indice_id,
                        "inicio_rentabilidade": ativo.inicio_rentabilidade,
                        "isin": ativo.isin,
                        "serie": ativo.serie,
                        "taxa": ativo.taxa,
                        "tipo_id": ativo.tipo_id,
                        "valor_emissao": ativo.valor_emissao,
                    }
                )
                novos_eventos_ativo: list[AtivosRepository.EventDict] = [
                    {
                        "ativo_codigo": ativo.codigo,
                        "ativo_fluxo_tipo_id": evento.tipo_id,
                        "data_evento": evento.data_pagamento,
                        "data_pagamento": evento.data_pagamento,
                        "percentual": evento.percentual,
                        "pu_calculado": evento.pu_calculado,
                        "pu_evento": evento.pu_evento,
                    }
                    for evento in ativo.fluxos.added
                ]
                atualizar_eventos_ativo: list[AtivosRepository.UpdateEventDict] = [
                    {
                        "id": evento.id,
                        "ativo_codigo": ativo.codigo,
                        "ativo_fluxo_tipo_id": evento.tipo_id,
                        "data_evento": evento.data_pagamento,
                        "data_pagamento": evento.data_pagamento,
                        "percentual": evento.percentual,
                        "pu_calculado": evento.pu_calculado,
                        "pu_evento": evento.pu_evento,
                    }
                    for evento in ativo.fluxos.modified
                ]
                remover_eventos_ativo: list[int] = [
                    evento_id for evento_id in ativo.fluxos.deleted
                ]

                novos_eventos += novos_eventos_ativo
                atualizar_eventos += atualizar_eventos_ativo
                remover_eventos += remover_eventos_ativo

                if ativo.indice_id == AtivoIndice.IPCA_M:
                    ipca = ativo.ativo_ipca or IPCAAssetSchema(
                        ipca_2_meses=False, ipca_negativo=False, mesversario=15
                    )
                    remover_ativos_ipca.append(ativo.codigo)
                    novos_ativos_ipca.append(
                        {
                            "ativo_codigo": ativo.codigo,
                            "ipca_2_meses": ipca.ipca_2_meses,
                            "ipca_negativo": ipca.ipca_negativo,
                            "mesversario": ipca.mesversario,
                        }
                    )
            if len(atualizar_ativos) > 0:
                await self.db.execute(update(Ativo), atualizar_ativos)

            await self.deletar_ativos_ipca(remover_ativos_ipca)
            await self.inserir_ativos_ipca(novos_ativos_ipca)

            await self.deletar_eventos(remover_eventos)
            await self.atualizar_eventos(atualizar_eventos)
            await self.inserir_eventos(novos_eventos)

    async def inserir_ativos(self, inserir: list[InsertAssetSchema]):
        async with self.db.begin_nested():
            novos_ativos: list[AtivosRepository.AssetDict] = [
                {
                    "codigo": ativo.codigo,
                    "valor_emissao": ativo.valor_emissao,
                    "data_emissao": ativo.data_emissao,
                    "inicio_rentabilidade": ativo.inicio_rentabilidade,
                    "data_vencimento": ativo.data_vencimento,
                    "taxa": ativo.taxa,
                    "atualizacao": datetime.today(),
                    "cadastro_manual": True,
                    "emissor_id": ativo.emissor_id,
                    "tipo_id": ativo.tipo_id,
                    "indice_id": ativo.indice_id,
                    "apelido": ativo.apelido,
                    "isin": ativo.isin,
                    "serie": ativo.serie,
                    "emissao": ativo.emissao,
                }
                for ativo in inserir
            ]
            if len(novos_ativos) == 0:
                return
            await self.db.execute(insert(Ativo).values(novos_ativos))
            novos_eventos: list[AtivosRepository.EventDict] = [
                {
                    "ativo_codigo": ativo.codigo,
                    "data_pagamento": evento.data_pagamento,
                    "ativo_fluxo_tipo_id": evento.tipo_id,
                    "data_evento": evento.data_pagamento,
                    "percentual": evento.percentual,
                    "pu_evento": evento.pu_evento,
                    "pu_calculado": evento.pu_calculado,
                }
                for ativo in inserir
                for evento in ativo.fluxos
            ]
            if len(novos_eventos) == 0:
                return
            await self.inserir_eventos(novos_eventos)

    async def deletar_ativos_ipca(self, codigos_ativos: list[str]):
        if len(codigos_ativos) == 0:
            return
        async with self.db.begin_nested():
            await self.db.execute(
                delete(AtivoIPCA).where(AtivoIPCA.ativo_codigo.in_({*codigos_ativos}))
            )

    async def inserir_ativos_ipca(self, ativos_ipca: list[InsertAtivoIPCADict]):
        if len(ativos_ipca) == 0:
            return
        async with self.db.begin_nested():
            await self.db.execute(insert(AtivoIPCA).values(ativos_ipca))

    async def deletar_eventos(self, deletar: list[int]):
        if len(deletar) == 0:
            return
        async with self.db.begin_nested():
            await self.db.execute(
                delete(AtivoFluxo).where(AtivoFluxo.id.in_({*deletar}))
            )

    async def atualizar_eventos(self, atualizar: list[UpdateEventDict]):
        if len(atualizar) == 0:
            return
        async with self.db.begin_nested():
            await self.db.execute(update(AtivoFluxo), atualizar)

    async def inserir_eventos(self, inserir: list[EventDict]):
        if len(inserir) == 0:
            return
        async with self.db.begin_nested():
            await self.db.execute(insert(AtivoFluxo).values(inserir))

    async def emissores(
        self,
        deslocamento: int = 0,
        quantidade: int = 35,
        ordenacao: list[UnaryExpression] = [Emissor.id.asc()],
    ):
        total = await self.db.execute(select(count()).select_from(Emissor))
        results = await self.db.execute(
            select(Emissor)
            .join(Emissor.setor, isouter=True)
            .join(EmissorSetor.icone, isouter=True)
            .join(Emissor.grupo, isouter=True)
            .join(Emissor.analista_credito, isouter=True)
            .join(AnalistaCredito.user, isouter=True)
            .options(
                contains_eager(Emissor.setor),
                contains_eager(Emissor.setor, EmissorSetor.icone),
                contains_eager(Emissor.grupo),
                contains_eager(Emissor.analista_credito),
                contains_eager(Emissor.analista_credito, AnalistaCredito.user),
            )
            .order_by(*ordenacao)
            .offset(deslocamento)
            .limit(quantidade)
        )
        return results.unique().scalars().all(), (total.unique().scalar() or 0)

    async def transacao_emissores(
        self, update: list[UpdateEmissorSchema], insert: list[InsertEmissorSchema]
    ):
        async with self.db.begin_nested():
            emissores_antigos = await self.emissores_from_ids(
                [emissor.id for emissor in update]
            )
            emissores_antigos = [
                UpdateEmissorSchema(
                    analista_credito_id=emissor.analista_credito_id,
                    cnpj=emissor.cnpj,
                    codigo_cvm=emissor.codigo_cvm,
                    grupo_id=emissor.grupo_id,
                    id=emissor.id,
                    nome=emissor.nome,
                    setor_id=emissor.setor_id,
                    tier=emissor.tier,
                )
                for emissor in emissores_antigos
            ]
            await self.atualizar_emissores(update)
            novos_ids_emissores = await self.inserir_emissores(insert)

        return novos_ids_emissores, [*emissores_antigos]

    async def atualizar_emissores(self, atualizar: list[UpdateEmissorSchema]):
        async with self.db.begin_nested():
            atualizar_emissores: list[dict] = []
            for emissor in atualizar:
                atualizar_emissores.append(
                    {
                        "id": emissor.id,
                        "cnpj": emissor.cnpj,
                        "nome": emissor.nome,
                        "tier": emissor.tier,
                        "codigo_cvm": emissor.codigo_cvm,
                        "grupo_id": emissor.grupo_id,
                        "setor_id": emissor.setor_id,
                        "analista_credito_id": emissor.analista_credito_id,
                    }
                )
            if len(atualizar_emissores) > 0:
                await self.db.execute(update(Emissor), atualizar_emissores)

    async def inserir_emissores(self, inserir: list[InsertEmissorSchema]) -> list[int]:
        async with self.db.begin_nested():
            novos_emissores: list[dict] = [
                {
                    "cnpj": emissor.cnpj,
                    "nome": emissor.nome,
                    "tier": emissor.tier,
                    "codigo_cvm": emissor.codigo_cvm,
                    "grupo_id": emissor.grupo_id,
                    "setor_id": emissor.setor_id,
                    "analista_credito_id": emissor.analista_credito_id,
                }
                for emissor in inserir
            ]
            if len(novos_emissores) == 0:
                return []
            ids = await self.db.execute(
                insert(Emissor).values(novos_emissores).returning(Emissor.id)
            )
            return [*ids.scalars().all()]

    async def emissor(self, id: int):
        result = await self.db.execute(
            select(Emissor)
            .join(Emissor.setor, isouter=True)
            .join(EmissorSetor.icone, isouter=True)
            .join(Emissor.grupo, isouter=True)
            .join(Emissor.analista_credito, isouter=True)
            .join(AnalistaCredito.user, isouter=True)
            .options(
                contains_eager(Emissor.setor),
                contains_eager(Emissor.setor, EmissorSetor.icone),
                contains_eager(Emissor.grupo),
                contains_eager(Emissor.analista_credito),
                contains_eager(Emissor.analista_credito, AnalistaCredito.user),
            )
            .where(Emissor.id == id)
        )
        return result.scalar_one_or_none()

    async def setores(self, with_sys_data: bool = False):
        select_query = select(EmissorSetor)
        if with_sys_data:
            select_query = select_query.join(EmissorSetor.icone, isouter=True).options(
                contains_eager(EmissorSetor.icone)
            )
        results = await self.db.execute(select_query.order_by(EmissorSetor.nome.asc()))
        return results.scalars().all()

    async def transacao_setores(
        self,
        atualizar: list[SetorSchema],
        inserir: list[InsertSetorSchema],
    ):
        async with self.db.begin_nested():
            await self.atualizar_setores(atualizar)
            await self.inserir_setores(inserir)

    async def atualizar_setores(self, atualizar: list[SetorSchema]):
        async with self.db.begin_nested():
            atualizar_setores: list[dict] = []
            atualizar_icones: list[dict] = []

            for setor in atualizar:
                atualizar_setores.append({"id": setor.id, "nome": setor.nome})
                atualizar_icones.append(
                    {"setor_id": setor.id, "icone": setor.sistema_icone}
                )

            if len(atualizar_setores) > 0:
                await self.db.execute(update(EmissorSetor), atualizar_setores)
            if len(atualizar_icones) > 0:
                await self.db.execute(update(EmissorSetorIcone), atualizar_icones)

    async def inserir_setores(self, inserir: list[InsertSetorSchema]):
        async with self.db.begin_nested():
            novos_setores: list[dict] = [{"nome": setor.nome} for setor in inserir]
            if len(novos_setores) == 0:
                return
            ids_setores = (
                (
                    await self.db.execute(
                        insert(EmissorSetor)
                        .values(novos_setores)
                        .returning(EmissorSetor.id)
                    )
                )
                .scalars()
                .all()
            )
            novos_icones: list[dict] = [
                {"setor_id": id_setor, "icone": inserir[posicao].sistema_icone}
                for posicao, id_setor in enumerate(ids_setores)
                if inserir[posicao].sistema_icone
            ]
            if len(novos_icones) > 0:
                await self.db.execute(insert(EmissorSetorIcone).values(novos_icones))

    async def grupos(self):
        results = await self.db.execute(
            select(EmissorGrupo).order_by(EmissorGrupo.nome.asc())
        )
        return results.scalars().all()

    async def transacao_grupos(
        self,
        atualizar: list[GrupoSchema],
        inserir: list[InsertGrupoSchema],
    ):
        async with self.db.begin_nested():
            await self.atualizar_grupos(atualizar)
            await self.inserir_grupos(inserir)

    async def atualizar_grupos(self, atualizar: list[GrupoSchema]):
        async with self.db.begin_nested():
            atualizar_grupos: list[dict] = []
            for grupo in atualizar:
                atualizar_grupos.append({"id": grupo.id, "nome": grupo.nome})
            if len(atualizar_grupos) > 0:
                await self.db.execute(update(EmissorGrupo), atualizar_grupos)

    async def inserir_grupos(self, inserir: list[InsertGrupoSchema]):
        async with self.db.begin_nested():
            novos_grupos: list[dict] = [{"nome": grupo.nome} for grupo in inserir]
            if len(novos_grupos) == 0:
                return
            await self.db.execute(insert(EmissorGrupo).values(novos_grupos))

    async def analistas(self):
        results = await self.db.execute(
            select(AnalistaCredito)
            .join(AnalistaCredito.user)
            .options(contains_eager(AnalistaCredito.user))
            .order_by(Usuario.nome.asc())
        )
        return results.scalars().all()

    async def analistas_from_ids(self, analista_ids: list[int]):
        results = await self.db.execute(
            select(AnalistaCredito).where(AnalistaCredito.id.in_(analista_ids))
        )
        return results.scalars().all()

    async def emissores_from_ids(self, emissor_ids: list[int]):
        results = await self.db.execute(
            select(Emissor).where(Emissor.id.in_(emissor_ids))
        )
        return results.scalars().all()

    def ativos(self, codigos: list[str]):
        return self.lista_ativos(
            0, len(codigos), [Ativo.codigo.asc()], [Ativo.codigo.in_(codigos)]
        )
