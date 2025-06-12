from datetime import date
from typing import Annotated

from fastapi import APIRouter
from config.swagger import token_field
from fastapi.exceptions import HTTPException
from fastapi import Query

from .service import CalculosService

router = APIRouter(prefix="/calculos", tags=["Cálculos"], dependencies=[token_field])


@router.get("/data/gerar-intervalos")
def intervalo_fluxos(
    data_inicio_rentabilidade: date, data_vencimento: date, periodicidade_meses: int
):
    return CalculosService.periodicidade_datas(
        data_inicio_rentabilidade, data_vencimento, periodicidade_meses
    )


@router.get("/data/proximos-dias-uteis")
def proximos_dias_uteis(dias: Annotated[list[date], Query()]):
    return CalculosService.dias_uteis_seguintes(dias)


@router.get("/porcentagem/absoluta-para-relativa")
def porcentagens_absolutas_para_proporcionais(
    absolutas: Annotated[list[float], Query()]
):
    return CalculosService.porcentagens_absolutas_para_relativas(absolutas)


@router.get("/porcentagem/relativa-para-absoluta")
def porcentagens_proporcionais_para_absolutas(
    relativas: Annotated[list[float], Query()]
):
    return CalculosService.porcentagens_relativas_para_absolutas(relativas)
