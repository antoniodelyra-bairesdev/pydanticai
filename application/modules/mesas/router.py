from fastapi import Request, Depends
from fastapi.routing import APIRouter

from sqlalchemy.ext.asyncio.session import AsyncSession

from config.swagger import token_field

from .service import MesasService
from .repository import MesasRepository
from .schema import MesaSchema

router = APIRouter(prefix="/mesa", tags=["Mesas"], dependencies=[token_field])


def get_service(request: Request):
    sessao: AsyncSession = request.state.db
    return MesasService(mesas_repository=MesasRepository(db=sessao))


@router.get("/")
async def listar_mesas(service: MesasService = Depends(get_service)):
    resultados = await service.mesas()
    return MesaSchema.a_partir_de_resultado_geral(resultados)
