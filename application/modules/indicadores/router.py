from datetime import date

from fastapi import APIRouter, Query, Request, Depends
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body
from fastapi.responses import StreamingResponse
from typing import Annotated
from urllib.parse import quote

from modules.util.request import db

from modules.util.mediatypes import XLSX, stream
from modules.rotinas.repository import RotinaRepository
from modules.util.validators import DateInterval, OptionalDateInterval
from starlette.responses import JSONResponse

from .repository import IndicadoresRepository
from .schema import (
    AtualizacaoIGPMProjecaoSchema,
    AtualizacaoIPCAProjecaoSchema,
    AtualizarAjusteDAPSchema,
    AtualizarCDIRequest,
    AtualizarPontoCurvaNTNBSchema,
    CurvaNTNBResponse,
    SalvarIGPMRequest,
    SalvarIPCARequest,
    AtualizarPontoCurvaDISchema,
    CurvaDIResponse,
    HistoricoCDISchema,
    HistoricoIGPMSchema,
    HistoricoIPCASchema,
    IGPMProjecaoSchema,
    IPCAProjecaoSchema,
    IndicadorSchema,
)
from .service import IndicadoresService

from config.swagger import token_field

router = APIRouter(prefix="/indicadores", dependencies=[token_field])


def get_service(request: Request):
    session = db(request)
    return IndicadoresService(
        indicadores_repository=IndicadoresRepository(session),
        rotinas_repository=RotinaRepository(session),
    )


@router.get("/")
async def indicadores(service: IndicadoresService = Depends(get_service)):
    indicadores = await service.indicadores()
    return [
        IndicadorSchema(id=tuple(indicador)[0], nome=tuple(indicador)[1])
        for indicador in indicadores
    ]


# Curvas

# DI


@router.get("/curva-di", tags=["Curva DI"])
async def curva_di(
    data: Annotated[date, Query()] = date.today(),
    service: IndicadoresService = Depends(get_service),
) -> CurvaDIResponse:
    r = await service.curva_di_interpolada(data)
    return r


@router.get("/curva-di/xlsx", tags=["Curva DI"])
async def curva_di_xlsx(
    data: Annotated[date, Query()] = date.today(),
    service: IndicadoresService = Depends(get_service),
):
    planilha = await service.curva_di_interpolada_xlsx(data)
    arquivo = planilha.gerar()
    return StreamingResponse(
        stream(arquivo),
        media_type=XLSX,
        headers={
            "Content-Disposition": f'attachment; filename="{quote(planilha.nome)}.xlsx"',
            "Content-Length": str(arquivo.getbuffer().nbytes),
        },
    )


@router.put("/curva-di", tags=["Curva DI"])
async def atualizar_curva_di(
    data: Annotated[date, Query()],
    body: list[AtualizarPontoCurvaDISchema],
    service: IndicadoresService = Depends(get_service),
):
    await service.atualizar_curva_di(data, body)


# NTN-B


@router.get("/curva-ntnb", tags=["Curva NTN-B"])
async def curva_ntnb(
    data: Annotated[date, Query()] = date.today(),
    service: IndicadoresService = Depends(get_service),
) -> CurvaNTNBResponse:
    return await service.curva_ntnb_interpolada(data)


@router.get("/curva-ntnb/xlsx", tags=["Curva NTN-B"])
async def curva_ntnb_xlsx(
    data: Annotated[date, Query()] = date.today(),
    service: IndicadoresService = Depends(get_service),
):
    planilha = await service.curva_ntnb_xlsx(data)
    arquivo = planilha.gerar()
    return StreamingResponse(
        stream(arquivo),
        media_type=XLSX,
        headers={
            "Content-Disposition": f'attachment; filename="{quote(planilha.nome)}.xlsx"',
            "Content-Length": str(arquivo.getbuffer().nbytes),
        },
    )


@router.put("/curva-ntnb/taxas_indicativas", tags=["Curva NTN-B"])
async def atualizar_taxas_indicativas_ntnb(
    data_referencia: Annotated[date, Query()],
    body: list[AtualizarPontoCurvaNTNBSchema],
    service: IndicadoresService = Depends(get_service),
):
    return await service.atualizar_taxas_indicativas_ntnb(data_referencia, body)


@router.put("/curva-ntnb/ajuste-dap", tags=["Curva NTN-B"])
async def atualizar_ajuste_dap(
    data_referencia: Annotated[date, Query()],
    body: list[AtualizarAjusteDAPSchema],
    service: IndicadoresService = Depends(get_service),
):
    return await service.atualizar_ajustes_dap(data_referencia, body)


# Históricos

# CDI


@router.get("/cdi", tags=["CDI"])
async def cdi(
    intervalo: OptionalDateInterval, service: IndicadoresService = Depends(get_service)
) -> list[HistoricoCDISchema]:
    return await service.cdi(intervalo)


@router.post("/cdi", tags=["CDI"])
async def inserir_cdi(
    data: Annotated[date, Query()],
    body: AtualizarCDIRequest,
    service: IndicadoresService = Depends(get_service),
):
    return await service.inserir_cdi(data, body.taxa)


@router.get("/cdi/acumulado", tags=["CDI"])
async def cdi_acumulado(
    intervalo: DateInterval,
    valor: Annotated[float, Query()],
    percentual: Annotated[float, Query()],
    juros: Annotated[float, Query()],
    service: IndicadoresService = Depends(get_service),
):
    inicio, fim = intervalo
    return await service.cdi_acumulado(inicio, fim, valor, percentual, juros)


# Inflação


@router.get("/inflacao/xlsx", tags=["Inflação"])
async def indices_xlsx(service: IndicadoresService = Depends(get_service)):
    planilha = await service.indices_xlsx()
    arquivo = planilha.gerar()
    return StreamingResponse(
        stream(arquivo),
        media_type=XLSX,
        headers={
            "Content-Disposition": f'attachment; filename="{quote(planilha.nome)}.xlsx"',
            "Content-Length": str(arquivo.getbuffer().nbytes),
        },
    )


# IGPM


@router.get("/inflacao/igpm", tags=["Inflação"])
async def igpm(
    intervalo: OptionalDateInterval, service: IndicadoresService = Depends(get_service)
) -> list[HistoricoIGPMSchema]:
    return await service.igpm(intervalo)


@router.get("/inflacao/igpm/projecao", tags=["Inflação"])
async def igpm_projecao(
    intervalo: OptionalDateInterval, service: IndicadoresService = Depends(get_service)
) -> list[IGPMProjecaoSchema]:
    return await service.igpm_projecao(intervalo)


@router.put("/inflacao/igpm", tags=["Inflação"])
async def atualizar_igpm(
    body: list[SalvarIGPMRequest],
    service: IndicadoresService = Depends(get_service),
):
    return await service.atualizar_igpm(body)


@router.put("/inflacao/igpm/projecao", tags=["Inflação"])
async def atualizar_igpm_projecao(
    body: list[AtualizacaoIGPMProjecaoSchema],
    service: IndicadoresService = Depends(get_service),
):
    return await service.atualizar_igpm_projecao(body)


# IPCA


@router.get("/inflacao/ipca", tags=["Inflação"])
async def ipca(
    intervalo: OptionalDateInterval, service: IndicadoresService = Depends(get_service)
) -> list[HistoricoIPCASchema]:
    return await service.ipca(intervalo)


@router.get("/inflacao/ipca/projecao", tags=["Inflação"])
async def ipca_projecao(
    intervalo: OptionalDateInterval, service: IndicadoresService = Depends(get_service)
) -> list[IPCAProjecaoSchema]:
    return await service.ipca_projecao(intervalo)


@router.put("/inflacao/ipca", tags=["Inflação"])
async def atualizar_ipca(
    body: list[SalvarIPCARequest],
    service: IndicadoresService = Depends(get_service),
):
    return await service.atualizar_ipca(body)


@router.put("/inflacao/ipca/projecao", tags=["Inflação"])
async def atualizar_ipca_projecao(
    body: list[AtualizacaoIPCAProjecaoSchema],
    service: IndicadoresService = Depends(get_service),
):
    return await service.atualizar_ipca_projecao(body)


@router.get("/rentabilidades")
async def indices_benchmark_rentabilidades(
    indices_benchmark_ids: str | None = Query(
        None,
        title="Ids dos índices",
        description="Ids dos índices que terão suas rentabilidades listadas. Caso não seja especificado nenhum id, todos os índices serão considerados",
    ),
    data_referencia: date | None = Query(
        None,
        title="Data de referência",
        description="Data utilizada como referência para a listagem das rentabilidades. Caso não seja específicada, será utilizada a data atual",
    ),
    service: IndicadoresService = Depends(get_service),
):
    """
    Lista as rentabilidades do dia, mês, ano 12, 24 e 36 meses dos índices identificados em [indices_benchmark_ids]
    da [data_referencia].\n
    Caso não exista preço da cota na [data_referencia], será listado o preço da cota da data anterior mais próxima.
    """
    indices_benchmark_ids_tratados: list[int] = []
    if indices_benchmark_ids == "" or indices_benchmark_ids is None:
        indices_benchmark_ids_tratados = await service.get_indicadores_benchmark_ids()
    else:
        try:
            indices_benchmark_ids_tratados = [
                int(id) for id in indices_benchmark_ids.split(",")
            ]
        except ValueError:
            raise HTTPException(
                422,
                "Um ou mais id informado na lista de ids é inválido. Ids devem ser números inteiros",
            )

    return await service.get_indicadores_benchmark_rentabilidades(
        data_referencia=data_referencia,
        indices_benchmark_ids=indices_benchmark_ids_tratados,
    )


@router.post("/rentabilidades", tags=["Rentabilidades"])
async def inserir_rentabilidades(
    rentabilidades: UploadFile,
    service: IndicadoresService = Depends(get_service),
):
    """
    Insere as rentabilidades do dia, mês, ano, 12 meses, 24 meses e 36 meses das cotas
    mais recentes dos indices presentes no arquivo carregado.
    """
    return await service.inserir_rentabilidades(rentabilidades)
