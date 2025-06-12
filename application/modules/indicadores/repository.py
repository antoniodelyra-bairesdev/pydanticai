from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Sequence, TypedDict

from modules.fundos.model import IndiceBenchmark
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete, func

from modules.util.queries import optional_interval, upsert
from sqlalchemy.orm.strategy_options import contains_eager
from .model import (
    IndiceBenchmarkRentabilidade,
    TaxasDAP,
    TaxaNTNB,
    HistoricoCDI,
    HistoricoIGPM,
    HistoricoIPCA,
    IGPMProj,
    IPCAProj,
    TaxaDI,
)
from .schema import (
    AtualizacaoIGPMProjecaoSchema,
    AtualizacaoIPCAProjecaoSchema,
    AtualizarAjusteDAPSchema,
    AtualizarPontoCurvaNTNBSchema,
    SalvarIGPMRequest,
    SalvarIPCARequest,
)


@dataclass
class IndicadoresRepository:
    db: AsyncSession

    async def lista_indices_benchmark_ids(self):
        query = select(IndiceBenchmark.id)

        results = await self.db.execute(query)
        return results.scalars().all()

    async def lista_indices_benchmark_ids_nomes(self, indices_ids: list[int] = []):
        query = select(IndiceBenchmark.id, IndiceBenchmark.nome)

        if len(indices_ids) > 0:
            query = query.where(IndiceBenchmark.id.in_(indices_ids))

        results = await self.db.execute(query)
        return results.all()

    async def curva_di(self, data: date):
        max_data = (
            select(func.max(TaxaDI.data)).where(TaxaDI.data <= data).scalar_subquery()
        )
        query = (
            select(TaxaDI)
            .where(TaxaDI.data == max_data)
            .order_by(TaxaDI.dias_corridos.asc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def atualizar_curva_di(self, data: date, pontos: list[dict], *, commit: bool):
        for ponto in pontos:
            ponto["data"] = data
        async with self.db.begin_nested():
            await self.db.execute(delete(TaxaDI).where(TaxaDI.data == data))
            await self.db.execute(insert(TaxaDI).values(pontos))

    async def ajuste_dap(self, data: date):
        max_data = (
            select(func.max(TaxasDAP.data_referencia))
            .where(TaxasDAP.data_referencia <= data)
            .scalar_subquery()
        )
        query = (
            select(TaxasDAP)
            .where(TaxasDAP.data_referencia == max_data)
            .order_by(TaxasDAP.data_vencimento.asc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def curva_ntnb(self, data: date):
        max_data = (
            select(func.max(TaxaNTNB.data_referencia))
            .where(TaxaNTNB.data_referencia <= data)
            .scalar_subquery()
        )
        query = (
            select(TaxaNTNB)
            .where(TaxaNTNB.data_referencia == max_data)
            .order_by(TaxaNTNB.data_vencimento.asc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def atualizar_taxas_indicativas_ntnb(
        self, data_referencia: date, ajustes: list[AtualizarPontoCurvaNTNBSchema]
    ):
        async with self.db.begin_nested():
            for taxa_indicativa in ajustes:
                await self.atualizar_taxa_indicativas_ntnb(
                    data_referencia,
                    taxa_indicativa.data_vencimento,
                    float(taxa_indicativa.taxa),
                    taxa_indicativa.duration,
                )

    async def atualizar_taxa_indicativas_ntnb(
        self, data_referencia: date, data_vencimento: date, taxa: float, duration: float
    ):
        async with self.db.begin_nested():
            await self.db.execute(
                delete(TaxaNTNB).where(
                    TaxaNTNB.data_referencia == data_referencia,
                    TaxaNTNB.data_vencimento == data_vencimento,
                )
            )
            await self.db.execute(
                insert(TaxaNTNB).values(
                    {
                        "data_referencia": data_referencia,
                        "data_vencimento": data_vencimento,
                        "taxa": taxa,
                        "duration": duration,
                    }
                )
            )

    async def atualizar_ajustes_dap(
        self, data_referencia: date, ajustes: list[AtualizarAjusteDAPSchema]
    ):
        async with self.db.begin_nested():
            for ajuste in ajustes:
                await self.atualizar_ajuste_dap(
                    data_referencia,
                    ajuste.data_vencimento,
                    float(ajuste.taxa),
                    ajuste.duration,
                )

    async def atualizar_ajuste_dap(
        self, data_referencia: date, data_vencimento: date, taxa: float, duration: int
    ):
        async with self.db.begin_nested():
            await self.db.execute(
                delete(TaxasDAP).where(
                    TaxasDAP.data_referencia == data_referencia,
                    TaxasDAP.data_vencimento == data_vencimento,
                )
            )
            await self.db.execute(
                insert(TaxasDAP).values(
                    {
                        "data_referencia": data_referencia,
                        "data_vencimento": data_vencimento,
                        "taxa": taxa,
                        "duration": duration,
                    }
                )
            )

    async def cdi(
        self, intervalo: tuple[date, date] | None = None
    ) -> Sequence[HistoricoCDI]:
        results = await self.db.execute(
            optional_interval(HistoricoCDI, HistoricoCDI.data, intervalo).order_by(
                HistoricoCDI.data.asc()
            )
        )
        return results.scalars().all()

    async def ultimo_cdi(self):
        return (
            await self.db.execute(
                select(HistoricoCDI).order_by(HistoricoCDI.data.desc()).limit(1)
            )
        ).scalar()

    async def inserir_cdi(self, data: date, taxa: Decimal, indice_acumulado: float):
        await self.db.execute(
            insert(HistoricoCDI).values(
                {
                    "data": data,
                    "taxa": taxa,
                    "indice_acumulado": indice_acumulado,
                    "atualizacao": datetime.today(),
                }
            )
        )
        await self.db.commit()

    async def buscar_par_indices_acumulados(self, inicio: date, fim: date):
        results = await self.db.execute(
            select(HistoricoCDI)
            .where(HistoricoCDI.data.in_([inicio, fim]))
            .order_by(HistoricoCDI.data.asc())
        )
        return results.scalars().all()

    async def igpm(
        self, intervalo: tuple[date, date] | None = None
    ) -> Sequence[HistoricoIGPM]:
        results = await self.db.execute(
            optional_interval(HistoricoIGPM, HistoricoIGPM.data, intervalo).order_by(
                HistoricoIGPM.data.asc()
            )
        )
        return results.scalars().all()

    async def igpm_projecao(
        self, intervalo: tuple[date, date] | None = None
    ) -> Sequence[IGPMProj]:
        results = await self.db.execute(
            optional_interval(IGPMProj, IGPMProj.data, intervalo).order_by(
                IGPMProj.data.asc()
            )
        )
        return results.scalars().all()

    async def atualizar_igpm_projecao(
        self, projecoes: list[AtualizacaoIGPMProjecaoSchema]
    ):
        async with self.db.begin_nested():
            await self.db.execute(
                delete(IGPMProj).where(
                    IGPMProj.data.in_([projecao.data for projecao in projecoes])
                )
            )
            await self.db.execute(
                insert(IGPMProj).values(
                    [
                        {
                            "data": projecao.data,
                            "projetado": projecao.projetado,
                            "taxa": projecao.taxa,
                            "atualizacao": datetime.today(),
                        }
                        for projecao in projecoes
                    ]
                )
            )

    async def salvar_igpm(self, indices_acumulados: list[SalvarIGPMRequest]):
        async with self.db.begin_nested():
            await self.db.execute(
                delete(HistoricoIGPM).where(
                    HistoricoIGPM.data.in_(
                        [
                            indice_acumulado.data
                            for indice_acumulado in indices_acumulados
                        ]
                    )
                )
            )
            await self.db.execute(
                insert(HistoricoIGPM).values(
                    [
                        {
                            "data": indice_acumulado.data,
                            "indice_acumulado": indice_acumulado.indice_acumulado,
                            "atualizacao": datetime.today(),
                        }
                        for indice_acumulado in indices_acumulados
                    ]
                )
            )

    async def ipca(
        self, intervalo: tuple[date, date] | None = None
    ) -> Sequence[HistoricoIPCA]:
        results = await self.db.execute(
            optional_interval(HistoricoIPCA, HistoricoIPCA.data, intervalo).order_by(
                HistoricoIPCA.data.asc()
            )
        )
        return results.scalars().all()

    async def ipca_projecao(
        self, intervalo: tuple[date, date] | None = None
    ) -> Sequence[IPCAProj]:
        results = await self.db.execute(
            optional_interval(IPCAProj, IPCAProj.data, intervalo).order_by(
                IPCAProj.data.asc()
            )
        )
        return results.scalars().all()

    async def atualizar_ipca_projecao(
        self, projecoes: list[AtualizacaoIPCAProjecaoSchema]
    ):
        async with self.db.begin_nested():
            await self.db.execute(
                delete(IPCAProj).where(
                    IPCAProj.data.in_([projecao.data for projecao in projecoes])
                )
            )
            await self.db.execute(
                insert(IPCAProj).values(
                    [
                        {
                            "data": projecao.data,
                            "projetado": projecao.projetado,
                            "taxa": projecao.taxa,
                            "atualizacao": datetime.today(),
                        }
                        for projecao in projecoes
                    ]
                )
            )

    async def salvar_ipca(self, indices_acumulados: list[SalvarIPCARequest]):
        async with self.db.begin_nested():
            await self.db.execute(
                delete(HistoricoIPCA).where(
                    HistoricoIPCA.data.in_(
                        [
                            indice_acumulado.data
                            for indice_acumulado in indices_acumulados
                        ]
                    )
                )
            )
            await self.db.execute(
                insert(HistoricoIPCA).values(
                    [
                        {
                            "data": indice_acumulado.data,
                            "indice_acumulado": indice_acumulado.indice_acumulado,
                            "atualizacao": datetime.today(),
                        }
                        for indice_acumulado in indices_acumulados
                    ]
                )
            )

    async def lista_indices_benchmark_rentabilidades_by_data_referencia(
        self, data_referencia: date, indices_benchmark_ids: list[int]
    ):
        query = (
            select(IndiceBenchmarkRentabilidade)
            .distinct(IndiceBenchmarkRentabilidade.indice_benchmark_id)
            .join(IndiceBenchmarkRentabilidade.indice_benchmark)
            .options(contains_eager(IndiceBenchmarkRentabilidade.indice_benchmark))
            .where(
                IndiceBenchmarkRentabilidade.data_posicao <= data_referencia,
                IndiceBenchmarkRentabilidade.indice_benchmark_id.in_(
                    indices_benchmark_ids
                ),
            )
            .order_by(
                IndiceBenchmarkRentabilidade.indice_benchmark_id.asc(),
                IndiceBenchmarkRentabilidade.data_posicao.desc(),
            )
        )

        results = await self.db.execute(query)
        return results.scalars().all()

    class InserirIndiceBenchmarkRentabilidade(TypedDict):
        indice_benchmark_id: int
        data_posicao: date
        rentabilidade_dia: float | None
        rentabilidade_mes: float | None
        rentabilidade_ano: float | None
        rentabilidade_12meses: float | None
        rentabilidade_24meses: float | None
        rentabilidade_36meses: float | None

    async def inserir_rentabilidades(
        self,
        indices_benchmark_rentabilidades: list[InserirIndiceBenchmarkRentabilidade],
    ):
        await self.db.execute(
            insert(IndiceBenchmarkRentabilidade)
            .values(indices_benchmark_rentabilidades)
            .returning(IndiceBenchmarkRentabilidade.id)
        )
        return None
