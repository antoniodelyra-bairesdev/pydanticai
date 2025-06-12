from dataclasses import dataclass
from datetime import date, datetime
from typing import TypedDict

from sqlalchemy import delete, select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm.strategy_options import contains_eager
from sqlalchemy.sql.expression import func

from .schema import (
    IdentificadorFundo,
    IndiceBenchmarkSchema,
    PatchDetalhesFundoSiteInstitucionalSchema,
    InsertFundoInstitucionalSchema,
    PostDetalhesFundoSiteInstitucionalSchema,
    UpdateFundo,
    UpdateFundoInstitucionalSchema,
)
from .model import (
    Fundo,
    FundoAdministrador,
    FundoCaracteristicaExtra,
    FundoCaracteristicaExtraRelacionamento,
    FundoCaracteristicaExtraRelacionamentoSiteInstitucional,
    FundoCategoriaDocumento,
    FundoClassificacaoSiteInstitucional,
    FundoControlador,
    FundoCotaRentabilidade,
    FundoCustodiante,
    FundoDistribuidorRelacionamento,
    FundoDistribuidorRelacionamentoSiteInstitucional,
    FundoDocumento,
    FundoDocumentoSiteInstitucional,
    FundoIndiceBenchmark,
    FundoIndiceBenchmarkSiteInstitucional,
    FundoPatrimonioLiquidoRentabilidade,
    FundoSiteInstitucional,
    FundoTipoSiteInstitucional,
    FundoMesaAssociacao,
)
from modules.mesas.model import Mesa


@dataclass
class FundosRepository:
    db: AsyncSession

    async def lista_fundo_cnpj_por_id(self, fundo_id: int):
        query = select(Fundo.cnpj).where(Fundo.id == fundo_id)
        results = await self.db.execute(query)
        return results.scalars().one()

    async def lista_fundos_ids_cnpjs(self, fundos_ids: list[int] = []):
        query = select(Fundo.id, Fundo.cnpj)
        if len(fundos_ids) > 0:
            query = query.where(Fundo.id.in_(fundos_ids))

        results = await self.db.execute(query)
        return results.all()

    async def lista_tipos_fundos_site_institucional(self):
        results = await self.db.execute(select(FundoTipoSiteInstitucional))
        return results.scalars().all()

    async def lista_classificacao_fundos_site_institucional(self):
        results = await self.db.execute(select(FundoClassificacaoSiteInstitucional))
        return results.scalars().all()

    async def lista_fundos_site_institucional(
        self, dos_fundos: list[int] | None = None
    ):
        query = (
            select(FundoSiteInstitucional)
            .outerjoin(FundoSiteInstitucional.classificacao)
            .outerjoin(FundoSiteInstitucional.tipo)
            .outerjoin(FundoSiteInstitucional.indices_benchmark)
            .outerjoin(FundoIndiceBenchmarkSiteInstitucional.indice_benchmark)
            .outerjoin(FundoSiteInstitucional.mesa)
            .outerjoin(FundoSiteInstitucional.caracteristicas_extras)
            .outerjoin(
                FundoCaracteristicaExtraRelacionamentoSiteInstitucional.caracteristica_extra
            )
            .outerjoin(FundoSiteInstitucional.distribuidores)
            .outerjoin(FundoDistribuidorRelacionamentoSiteInstitucional.distribuidor)
            .options(
                contains_eager(FundoSiteInstitucional.classificacao),
                contains_eager(FundoSiteInstitucional.tipo),
                contains_eager(FundoSiteInstitucional.indices_benchmark),
                contains_eager(
                    FundoSiteInstitucional.caracteristicas_extras,
                ),
                contains_eager(
                    FundoSiteInstitucional.caracteristicas_extras,
                    FundoCaracteristicaExtraRelacionamentoSiteInstitucional.caracteristica_extra,
                ),
                contains_eager(
                    FundoSiteInstitucional.indices_benchmark,
                    FundoIndiceBenchmarkSiteInstitucional.indice_benchmark,
                ),
                contains_eager(FundoSiteInstitucional.mesa).load_only(
                    Mesa.id, Mesa.nome, Mesa.ordenacao
                ),
                contains_eager(
                    FundoSiteInstitucional.distribuidores,
                ),
                contains_eager(
                    FundoSiteInstitucional.distribuidores,
                    FundoDistribuidorRelacionamentoSiteInstitucional.distribuidor,
                ),
            )
            .order_by(FundoSiteInstitucional.nome.asc())
        )
        if dos_fundos != None:
            query = query.where(FundoSiteInstitucional.fundo_id.in_(dos_fundos))
        results = await self.db.execute(query)
        return results.unique().scalars().all()

    async def lista_fundo_site_institucional_por_nome_ou_ticker_ou_id(
        self, nome_ou_ticker_ou_fundo_id: str | int
    ):
        query = (
            select(FundoSiteInstitucional)
            .outerjoin(FundoSiteInstitucional.classificacao)
            .outerjoin(FundoSiteInstitucional.tipo)
            .outerjoin(FundoSiteInstitucional.fundos_documentos)
            .outerjoin(FundoDocumentoSiteInstitucional.fundo_documento)
            .outerjoin(FundoDocumento.fundo_categoria_documento)
            .outerjoin(FundoDocumento.arquivo)
            .outerjoin(FundoSiteInstitucional.indices_benchmark)
            .outerjoin(FundoIndiceBenchmarkSiteInstitucional.indice_benchmark)
            .outerjoin(FundoSiteInstitucional.mesa)
            .outerjoin(FundoSiteInstitucional.caracteristicas_extras)
            .outerjoin(
                FundoCaracteristicaExtraRelacionamentoSiteInstitucional.caracteristica_extra
            )
            .options(
                contains_eager(FundoSiteInstitucional.classificacao),
                contains_eager(FundoSiteInstitucional.tipo),
                contains_eager(FundoSiteInstitucional.fundos_documentos),
                contains_eager(
                    FundoSiteInstitucional.fundos_documentos,
                    FundoDocumentoSiteInstitucional.fundo_documento,
                ),
                contains_eager(
                    FundoSiteInstitucional.fundos_documentos,
                    FundoDocumentoSiteInstitucional.fundo_documento,
                    FundoDocumento.fundo_categoria_documento,
                ),
                contains_eager(
                    FundoSiteInstitucional.fundos_documentos,
                    FundoDocumentoSiteInstitucional.fundo_documento,
                    FundoDocumento.arquivo,
                ),
                contains_eager(FundoSiteInstitucional.indices_benchmark),
                contains_eager(
                    FundoSiteInstitucional.indices_benchmark,
                    FundoIndiceBenchmarkSiteInstitucional.indice_benchmark,
                ),
                contains_eager(FundoSiteInstitucional.mesa).load_only(
                    Mesa.id, Mesa.nome, Mesa.ordenacao
                ),
                contains_eager(FundoSiteInstitucional.caracteristicas_extras),
                contains_eager(
                    FundoSiteInstitucional.caracteristicas_extras,
                    FundoCaracteristicaExtraRelacionamentoSiteInstitucional.caracteristica_extra,
                ),
            )
        )
        if type(nome_ou_ticker_ou_fundo_id) == str:
            query = query.where(
                (
                    func.lower(FundoSiteInstitucional.ticker_b3)
                    == func.lower(nome_ou_ticker_ou_fundo_id)
                )
                | (
                    func.lower(FundoSiteInstitucional.nome)
                    == func.lower(nome_ou_ticker_ou_fundo_id)
                )
            )
        else:
            query = query.where(
                FundoSiteInstitucional.fundo_id == int(nome_ou_ticker_ou_fundo_id)
            )
        results = await self.db.execute(query)
        return results.unique().scalars().one_or_none()

    async def alterar_apelidos_de_fundos(self, ids_e_apelidos: list[tuple[int, str]]):
        if len(ids_e_apelidos) == 0:
            return
        await self.db.execute(
            update(Fundo),
            [
                {
                    "id": id,
                    "apelido": apelido,
                }
                for id, apelido in ids_e_apelidos
            ],
        )

    async def remover_fundo_do_site_institucional(
        self, ids_relacionamentos_deletados: list[int]
    ):
        if len(ids_relacionamentos_deletados) == 0:
            return
        await self.db.execute(
            delete(FundoSiteInstitucional).where(
                FundoSiteInstitucional.id.in_(ids_relacionamentos_deletados)
            )
        )

    async def alterar_caracteristicas_fundo_site_institucional(
        self, modificados: list[UpdateFundoInstitucionalSchema]
    ):
        if len(modificados) == 0:
            return
        await self.db.execute(
            update(FundoSiteInstitucional),
            [
                {
                    "id": modificado.id,
                    "site_institucional_classificacao_id": modificado.classificacao_id,
                    "site_institucional_tipo_id": modificado.tipo_id,
                }
                for modificado in modificados
            ],
        )

    async def adicionar_fundos_no_site_institucional(
        self, adicionados: list[InsertFundoInstitucionalSchema]
    ):
        if len(adicionados) == 0:
            return
        await self.db.execute(
            insert(FundoSiteInstitucional).values(
                [
                    {
                        "fundo_id": adicionado.fundo_id,
                        "site_institucional_classificacao_id": adicionado.classificacao_id,
                        "site_institucional_tipo_id": adicionado.tipo_id,
                    }
                    for adicionado in adicionados
                ]
            )
        )

    async def fundos(self, ids: list[int] | None = None):
        query = (
            select(Fundo)
            .outerjoin(Fundo.custodiante)
            .outerjoin(Fundo.fundo_site_institucional)
            .outerjoin(Fundo.indices_benchmark)
            .outerjoin(FundoIndiceBenchmark.indice_benchmark)
            .options(
                contains_eager(Fundo.custodiante),
                contains_eager(Fundo.fundo_site_institucional),
                contains_eager(Fundo.indices_benchmark),
                contains_eager(
                    Fundo.indices_benchmark, FundoIndiceBenchmark.indice_benchmark
                ),
            )
        )
        if ids:
            query = query.where(Fundo.id.in_(ids))
        results = await self.db.execute(query)
        return results.unique().scalars().all()

    async def inserir_fundo(self, body: UpdateFundo):
        result = await self.db.execute(
            insert(Fundo)
            .values({**dict(body), "atualizacao": datetime.today()})
            .returning(Fundo.id)
        )
        await self.db.commit()
        [new_id] = result.fetchall()
        return new_id

    async def atualizar_fundo(self, id: int, body: UpdateFundo):
        values = dict(body)
        for value in [
            "remover_documentos",
            "mesas_contribuidoras",
            "mesa_responsavel",
            "indices",
            "caracteristicas_extras",
            "data_inicio",
        ]:
            del values[value]
        result = await self.db.execute(
            update(Fundo).where(Fundo.id == id).values(values).returning(Fundo.id)
        )
        await self.db.commit()
        [new_id] = result.fetchall()
        return new_id

    async def fundos_custodiantes(self):
        return (
            (
                await self.db.execute(
                    select(FundoCustodiante)
                    .outerjoin(FundoCustodiante.instituicao_financeira)
                    .options(contains_eager(FundoCustodiante.instituicao_financeira))
                )
            )
            .scalars()
            .all()
        )

    async def fundos_controladores(self):
        return (
            (
                await self.db.execute(
                    select(FundoControlador)
                    .outerjoin(FundoControlador.instituicao_financeira)
                    .options(contains_eager(FundoControlador.instituicao_financeira))
                )
            )
            .scalars()
            .all()
        )

    async def fundos_administradores(self):
        return (
            (
                await self.db.execute(
                    select(FundoAdministrador)
                    .outerjoin(FundoAdministrador.instituicao_financeira)
                    .options(contains_eager(FundoAdministrador.instituicao_financeira))
                )
            )
            .scalars()
            .all()
        )

    async def fundos_cetip(self, contas: list[str]):
        REPLACE = func.REPLACE
        results = await self.db.execute(
            select(Fundo)
            .outerjoin(Fundo.custodiante)
            .options(
                contains_eager(Fundo.custodiante),
            )
            .where(REPLACE(REPLACE(Fundo.conta_cetip, ".", ""), "-", "").in_(contas))
        )
        return results.scalars().all()

    async def fundo_detalhes(self, id: int):
        results = await self.db.execute(
            select(Fundo)
            .outerjoin(Fundo.custodiante)
            .outerjoin(Fundo.fundo_site_institucional)
            .outerjoin(Fundo.documentos)
            .outerjoin(FundoDocumento.fundo_categoria_documento)
            .outerjoin(FundoDocumento.arquivo)
            .outerjoin(Fundo.indices_benchmark)
            .outerjoin(FundoIndiceBenchmark.indice_benchmark)
            .outerjoin(Fundo.mesas)
            .outerjoin(FundoMesaAssociacao.mesa)
            .outerjoin(Fundo.caracteristicas_extras)
            .outerjoin(FundoCaracteristicaExtraRelacionamento.caracteristica_extra)
            .outerjoin(Fundo.distribuidores)
            .outerjoin(FundoDistribuidorRelacionamento.distribuidor)
            .options(
                contains_eager(Fundo.custodiante),
                contains_eager(Fundo.fundo_site_institucional),
                contains_eager(Fundo.documentos),
                contains_eager(
                    Fundo.documentos, FundoDocumento.fundo_categoria_documento
                ),
                contains_eager(Fundo.documentos, FundoDocumento.arquivo),
                contains_eager(Fundo.indices_benchmark),
                contains_eager(
                    Fundo.indices_benchmark, FundoIndiceBenchmark.indice_benchmark
                ),
                contains_eager(
                    Fundo.mesas,
                ),
                contains_eager(Fundo.mesas, FundoMesaAssociacao.mesa),
                contains_eager(Fundo.caracteristicas_extras),
                contains_eager(
                    Fundo.caracteristicas_extras,
                    FundoCaracteristicaExtraRelacionamento.caracteristica_extra,
                ),
                contains_eager(
                    Fundo.distribuidores,
                ),
                contains_eager(
                    Fundo.distribuidores,
                    FundoDistribuidorRelacionamento.distribuidor,
                ),
            )
            .where(Fundo.id == id)
        )
        return results.unique().scalars().one_or_none()

    async def fundo_categorias_documentos(self):
        results = await self.db.execute(select(FundoCategoriaDocumento))
        return results.scalars().all()

    async def fundo_caracteristicas_extras(self):
        results = await self.db.execute(select(FundoCaracteristicaExtra))
        return results.scalars().all()

    async def fundo_documento(self, id: int):
        results = await self.db.execute(
            select(FundoDocumento)
            .outerjoin(FundoDocumento.arquivo)
            .outerjoin(FundoDocumento.fundo)
            .outerjoin(Fundo.fundo_site_institucional)
            .outerjoin(FundoSiteInstitucional.fundos_documentos)
            .options(
                contains_eager(FundoDocumento.arquivo),
                contains_eager(FundoDocumento.fundo),
                contains_eager(FundoDocumento.fundo, Fundo.fundo_site_institucional),
                contains_eager(
                    FundoDocumento.fundo,
                    Fundo.fundo_site_institucional,
                    FundoSiteInstitucional.fundos_documentos,
                ),
            )
            .where(FundoDocumento.id == id)
        )
        return results.unique().scalars().one_or_none()

    class InserirFundoDocumento(TypedDict):
        fundo_id: int
        arquivo_id: str
        fundo_categoria_documento_id: int
        titulo: str | None
        criado_em: datetime
        data_referencia: date

    async def inserir_documentos(self, fundos_documentos: list[InserirFundoDocumento]):
        if len(fundos_documentos) == 0:
            return []
        results = await self.db.execute(
            insert(FundoDocumento)
            .values(fundos_documentos)
            .returning(FundoDocumento.id)
        )
        return results.scalars().all()

    async def remover_documentos(self, ids_fundos_documento: list[int]):
        if len(ids_fundos_documento) == 0:
            return
        await self.db.execute(
            delete(FundoDocumento).where(FundoDocumento.id.in_(ids_fundos_documento))
        )

    async def lista_cotas_rentabilidades_by_data_referencia(
        self, data_referencia: date, fundos_ids: list[int]
    ):
        query = (
            select(FundoCotaRentabilidade)
            .distinct(FundoCotaRentabilidade.fundo_id)
            .where(
                FundoCotaRentabilidade.data_posicao <= data_referencia,
                FundoCotaRentabilidade.fundo_id.in_(fundos_ids),
            )
            .order_by(
                FundoCotaRentabilidade.fundo_id.asc(),
                FundoCotaRentabilidade.data_posicao.desc(),
            )
        )

        results = await self.db.execute(query)
        return results.scalars().all()

    class InserirFundoCotaRentabilidade(TypedDict):
        fundo_id: int
        data_posicao: date
        preco_cota: float | None
        rentabilidade_dia: float | None
        rentabilidade_mes: float | None
        rentabilidade_ano: float | None
        rentabilidade_12meses: float | None
        rentabilidade_24meses: float | None
        rentabilidade_36meses: float | None

    async def inserir_cotas_rentabilidades(
        self, fundos_cotas_rentabilidades: list[InserirFundoCotaRentabilidade]
    ):
        return await self.db.execute(
            insert(FundoCotaRentabilidade)
            .values(fundos_cotas_rentabilidades)
            .returning(FundoCotaRentabilidade.id)
        )

    async def lista_patrimonio_liquido_rentabilidades_by_data_referencia(
        self, data_referencia: date, fundos_ids: list[int]
    ):
        query = (
            select(FundoPatrimonioLiquidoRentabilidade)
            .distinct(FundoPatrimonioLiquidoRentabilidade.fundo_id)
            .where(
                FundoPatrimonioLiquidoRentabilidade.data_posicao <= data_referencia,
                FundoPatrimonioLiquidoRentabilidade.fundo_id.in_(fundos_ids),
            )
            .order_by(
                FundoPatrimonioLiquidoRentabilidade.fundo_id.asc(),
                FundoPatrimonioLiquidoRentabilidade.data_posicao.desc(),
            )
        )

        results = await self.db.execute(query)
        return results.scalars().all()

    class InserirFundoPatrimonioLiquidoRentabilidade(TypedDict):
        fundo_id: int
        data_posicao: date
        patrimonio_liquido: float | None
        media_12meses: float | None
        media_24meses: float | None
        media_36meses: float | None

    async def inserir_patrimonio_liquido_rentabilidades(
        self,
        fundos_patrimonio_liquido_rentabilidades: list[
            InserirFundoPatrimonioLiquidoRentabilidade
        ],
    ):
        return await self.db.execute(
            insert(FundoPatrimonioLiquidoRentabilidade)
            .values(fundos_patrimonio_liquido_rentabilidades)
            .returning(FundoPatrimonioLiquidoRentabilidade.id)
        )

    async def publicacao_documentos(
        self, site_institucional_fundo_id: int, fundos_documento_ids: list[int]
    ):
        async with self.db.begin_nested():
            await self.db.execute(
                delete(FundoDocumentoSiteInstitucional).where(
                    FundoDocumentoSiteInstitucional.site_institucional_fundo_id
                    == site_institucional_fundo_id
                )
            )
            await self.db.execute(
                insert(FundoDocumentoSiteInstitucional).values(
                    [
                        {
                            "site_institucional_fundo_id": site_institucional_fundo_id,
                            "fundos_documento_id": fundos_documento_id,
                        }
                        for fundos_documento_id in fundos_documento_ids
                    ]
                )
            )

    async def deleta_site_institucional_fundo(self, site_institucional_fundo_id: int):
        await self.db.execute(
            delete(FundoSiteInstitucional).where(
                FundoSiteInstitucional.id == site_institucional_fundo_id
            )
        )

    async def insere_site_institucional_fundo(
        self,
        fundo_id: int,
        fundo_cnpj: str,
        detalhes: PostDetalhesFundoSiteInstitucionalSchema,
    ) -> int:
        query = (
            insert(FundoSiteInstitucional)
            .values(
                {"fundo_id": fundo_id} | {"cnpj": fundo_cnpj} | detalhes.model_dump()
            )
            .returning(FundoSiteInstitucional.id)
        )

        results = await self.db.execute(query)
        return results.scalars().one()

    async def edita_site_institucional_fundo_por_id(
        self, id: int, detalhes: PatchDetalhesFundoSiteInstitucionalSchema
    ):
        detalhes_dict = detalhes.model_dump(exclude_unset=True)
        query = (
            update(FundoSiteInstitucional)
            .where(FundoSiteInstitucional.id == id)
            .values(detalhes_dict)
            .returning(FundoSiteInstitucional.id)
        )

        results = await self.db.execute(query)
        return results.scalars().one()

    async def insere_site_institucional_fundo_documentos(
        self,
        site_institucional_fundo_id: int,
        fundos_documento_ids: list[int],
    ):
        fundos_documentos_dicts = [
            {
                "site_institucional_fundo_id": site_institucional_fundo_id,
                "fundos_documento_id": fundo_documento,
            }
            for fundo_documento in fundos_documento_ids
        ]

        query = (
            insert(FundoDocumentoSiteInstitucional)
            .values(fundos_documentos_dicts)
            .returning(
                FundoDocumentoSiteInstitucional.site_institucional_fundo_id,
                FundoDocumentoSiteInstitucional.fundos_documento_id,
            )
        )

        results = await self.db.execute(query)
        return results.scalars().all()

    async def deleta_site_institucional_fundos_documentos(
        self,
        site_institucional_fundo_id: int,
        fundos_documento_ids: list[int],
    ):

        query = (
            delete(FundoDocumentoSiteInstitucional)
            .where(
                FundoDocumentoSiteInstitucional.site_institucional_fundo_id
                == site_institucional_fundo_id,
                FundoDocumentoSiteInstitucional.fundos_documento_id.in_(
                    fundos_documento_ids
                ),
            )
            .returning(
                FundoDocumentoSiteInstitucional.site_institucional_fundo_id,
                FundoDocumentoSiteInstitucional.fundos_documento_id,
            )
        )

        results = await self.db.execute(query)
        return results.scalars().all()

    async def insere_site_institucional_fundo_caracteristicas_extras(
        self,
        site_institucional_fundo_id: int,
        caracteristicas_extras_ids: list[int],
    ):
        caracteristicas_extras_dicts = [
            {
                "site_institucional_fundo_id": site_institucional_fundo_id,
                "fundo_caracteristica_extra_id": caracteristica_extra,
            }
            for caracteristica_extra in caracteristicas_extras_ids
        ]

        query = (
            insert(FundoCaracteristicaExtraRelacionamentoSiteInstitucional)
            .values(caracteristicas_extras_dicts)
            .returning(
                FundoCaracteristicaExtraRelacionamentoSiteInstitucional.site_institucional_fundo_id,
                FundoCaracteristicaExtraRelacionamentoSiteInstitucional.fundo_caracteristica_extra_id,
            )
        )

        results = await self.db.execute(query)
        return results.scalars().all()

    async def deleta_site_institucional_fundo_caracteristicas_extras(
        self,
        site_institucional_fundo_id: int,
        caracteristicas_extra_ids: list[int],
    ):
        query = (
            delete(FundoCaracteristicaExtraRelacionamentoSiteInstitucional)
            .where(
                FundoCaracteristicaExtraRelacionamentoSiteInstitucional.site_institucional_fundo_id
                == site_institucional_fundo_id,
                FundoCaracteristicaExtraRelacionamentoSiteInstitucional.fundo_caracteristica_extra_id.in_(
                    caracteristicas_extra_ids
                ),
            )
            .returning(
                FundoCaracteristicaExtraRelacionamentoSiteInstitucional.site_institucional_fundo_id,
                FundoCaracteristicaExtraRelacionamentoSiteInstitucional.fundo_caracteristica_extra_id,
            )
        )

        results = await self.db.execute(query)
        return results.scalars().all()

    async def insere_site_institucional_fundo_indices_benchmark(
        self, site_institucional_fundo_id: int, indices: list[IndiceBenchmarkSchema]
    ):
        indices_dicts = [
            {"site_institucional_fundo_id": site_institucional_fundo_id}
            | indice.model_dump()
            for indice in indices
        ]

        query = (
            insert(FundoIndiceBenchmarkSiteInstitucional)
            .values(indices_dicts)
            .returning(
                FundoIndiceBenchmarkSiteInstitucional.site_institucional_fundo_id,
                FundoIndiceBenchmarkSiteInstitucional.indice_benchmark_id,
            )
        )

        results = await self.db.execute(query)
        return results.scalars().all()

    async def deleta_site_institucional_fundo_indices_benchmark(
        self,
        site_institucional_fundo_id: int,
        indices_benchmark_ids: list[int],
    ):
        query = (
            delete(FundoIndiceBenchmarkSiteInstitucional)
            .where(
                FundoIndiceBenchmarkSiteInstitucional.site_institucional_fundo_id
                == site_institucional_fundo_id,
                FundoIndiceBenchmarkSiteInstitucional.indice_benchmark_id.in_(
                    indices_benchmark_ids
                ),
            )
            .returning(
                FundoIndiceBenchmarkSiteInstitucional.site_institucional_fundo_id,
                FundoIndiceBenchmarkSiteInstitucional.indice_benchmark_id,
            )
        )

        results = await self.db.execute(query)
        return results.scalars().all()

    async def insere_site_institucional_fundo_distribuidores(
        self,
        site_institucional_fundo_id: int,
        distribuidores_ids: list[int],
    ):
        distribuidores_dicts = [
            {
                "site_institucional_fundo_id": site_institucional_fundo_id,
                "fundo_distribuidor_id": distribuidor_id,
            }
            for distribuidor_id in distribuidores_ids
        ]

        query = (
            insert(FundoDistribuidorRelacionamentoSiteInstitucional)
            .values(distribuidores_dicts)
            .returning(
                FundoDistribuidorRelacionamentoSiteInstitucional.site_institucional_fundo_id,
                FundoDistribuidorRelacionamentoSiteInstitucional.fundo_distribuidor_id,
            )
        )

        results = await self.db.execute(query)
        return results.scalars().all()

    async def deleta_site_institucional_fundo_distribuidores(
        self,
        site_institucional_fundo_id: int,
        distribuidores_ids: list[int],
    ):
        query = (
            delete(FundoDistribuidorRelacionamentoSiteInstitucional)
            .where(
                FundoDistribuidorRelacionamentoSiteInstitucional.site_institucional_fundo_id
                == site_institucional_fundo_id,
                FundoDistribuidorRelacionamentoSiteInstitucional.fundo_distribuidor_id.in_(
                    distribuidores_ids
                ),
            )
            .returning(
                FundoDistribuidorRelacionamentoSiteInstitucional.site_institucional_fundo_id,
                FundoDistribuidorRelacionamentoSiteInstitucional.fundo_distribuidor_id,
            )
        )

        results = await self.db.execute(query)
        return results.scalars().all()

    async def buscar_fundos(self, identificadores: list[IdentificadorFundo]):
        def limpar_str_py(s: str):
            return s.strip().replace("-", "").replace(".", "").replace("/", "")

        def limpar_str_bd(
            c: InstrumentedAttribute[str] | InstrumentedAttribute[str | None],
        ):
            r = func.REPLACE
            return r(r(r(c, "-", ""), ".", ""), "/", "")

        ids = [int(idf.valor) for idf in identificadores if idf.tipo == "ID_VANGUARDA"]
        cnpjs = [
            limpar_str_py(idf.valor) for idf in identificadores if idf.tipo == "CNPJ"
        ]
        cetips = [
            limpar_str_py(idf.valor) for idf in identificadores if idf.tipo == "CETIP"
        ]
        selics = [
            limpar_str_py(idf.valor) for idf in identificadores if idf.tipo == "SELIC"
        ]

        results = await self.db.execute(
            select(Fundo)
            .outerjoin(Fundo.administrador)
            .options(contains_eager(Fundo.administrador))
            .where(
                Fundo.id.in_(ids)
                | limpar_str_bd(Fundo.cnpj).in_(cnpjs)
                | limpar_str_bd(Fundo.conta_cetip).in_(cetips)
                | limpar_str_bd(Fundo.conta_selic).in_(selics)
            )
        )

        return results.scalars().all()
