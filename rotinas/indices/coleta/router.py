from config.swagger import token_field
from datetime import date
from fastapi import APIRouter, Depends, Request

from .service import RotinaIndiceColetaService, RotinaIndiceColetaServiceImpl
from .schema import ColetaIndiceSchema

from modules.integrations.connectors_factories import (
    IntegrationsIndicesConnectorFactory,
)
from modules.indices.repository import IndicesRepositoryImpl
from modules.indices.model import Indice
from modules.moedas.repository import MoedasRepositoryImpl
from modules.moedas.model import Moeda
from modules.repository import BaseRepositoryImpl
from modules.util.request import db
from modules.util.datas import get_data_inicio_coleta

router = APIRouter(
    prefix="/rotinas/indices",
    tags=["Rotinas", "Indices", "Coleta"],
    dependencies=[token_field],
)


def get_service(request: Request) -> RotinaIndiceColetaService:
    session = db(request)

    return RotinaIndiceColetaServiceImpl(
        indices_repository=IndicesRepositoryImpl(
            base_repository=BaseRepositoryImpl[Indice](
                db_session=session,
                model_class=Indice,
            )
        ),
        moedas_repository=MoedasRepositoryImpl(
            base_repository=BaseRepositoryImpl[Moeda](
                db_session=session,
                model_class=Moeda,
            )
        ),
        integrations_connector_factory=IntegrationsIndicesConnectorFactory(),
    )


@router.post("/cotacoes/coleta")
async def coletar_cotacoes_indices(
    data_inicio: date | None = None,
    data_fim: date | None = None,
    indices: list[ColetaIndiceSchema] | None = None,
    service: RotinaIndiceColetaService = Depends(get_service),
):
    if not data_inicio:
        data_inicio = get_data_inicio_coleta()
    if not data_fim:
        data_fim = date.today()

    if indices:
        return await service.coleta_cotacoes_indices(
            data_inicio=data_inicio,
            data_fim=data_fim,
            dados_indices_a_serem_coletados=indices,
        )

    return await service.coleta_cotacoes_todos_indices(
        data_inicio=data_inicio, data_fim=data_fim
    )


@router.post("/cotacoes/coleta/ultimos")
async def coletar_ultimas_cotacoes_indices(
    service: RotinaIndiceColetaService = Depends(get_service),
):
    return await service.coleta_ultimas_cotacoes_todos_indices()
