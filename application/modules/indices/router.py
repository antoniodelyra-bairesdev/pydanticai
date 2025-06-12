from fastapi import APIRouter, Depends, Request

from .service import IndiceService, IndiceServiceImpl
from .model import Indice
from .schema import PostBodySchema, PostResponseSchma
from .repository import IndicesRepositoryImpl

from modules.fontes_dados.repository import FontesDadosRepositoryImpl
from modules.fontes_dados.model import FonteDados
from modules.repository import BaseRepositoryImpl
from modules.moedas.repository import MoedasRepositoryImpl
from modules.moedas.model import Moeda
from modules.util.request import db

router = APIRouter(prefix="/indices", tags=["Indices"])


def get_service(request: Request) -> IndiceService:
    session = db(request)

    return IndiceServiceImpl(
        fontes_dados_repository=FontesDadosRepositoryImpl(
            base_repository=BaseRepositoryImpl[FonteDados](
                db_session=session, model_class=FonteDados
            )
        ),
        indices_repository=IndicesRepositoryImpl(
            base_repository=BaseRepositoryImpl[Indice](
                db_session=session, model_class=Indice
            )
        ),
        moedas_repository=MoedasRepositoryImpl(
            base_repository=BaseRepositoryImpl[Moeda](
                db_session=session, model_class=Moeda
            )
        ),
    )


@router.post("/cotacoes")
async def inserir_indices(
    body: PostBodySchema,
    service: IndiceService = Depends(get_service),
):
    if body:
        return await service.insere_cotacoes(cotacoes_indices=body.cotacoes)

    return PostResponseSchma(
        cotacoes_inseridas=[],
        cotacoes_nao_inseridas=[],
        avisos=[],
    )
