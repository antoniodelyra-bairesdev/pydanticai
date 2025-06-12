import asyncio
from http import HTTPStatus
from io import BytesIO
from typing import Annotated, Any
from fastapi import APIRouter, Request, UploadFile, Query
from fastapi.exceptions import HTTPException
from modules.auth.service import AuthService
from starlette.responses import StreamingResponse
from .repository import ArquivosDatabaseRepository

from modules.util.mediatypes import stream
from modules.util.request import db
from config.swagger import token_field

from modules.indicadores.service import IndicadoresService, IndicadoresRepository
from modules.fundos.service import FundosService, FundosRepository

from urllib.parse import quote

router = APIRouter(prefix="/arquivos", tags=["Arquivos"], dependencies=[token_field])


@router.get("/{id}")
async def arquivo(request: Request, id: str):

    arquivos_repository = ArquivosDatabaseRepository(db=request.state.db)

    arquivo = await arquivos_repository.buscar(id)
    conteudo = await arquivos_repository.decodificar(arquivo)

    return StreamingResponse(
        stream(BytesIO(conteudo)),
        media_type=arquivo.extensao,
        headers={
            "Content-Disposition": f'attachment; filename="{quote(arquivo.nome)}"',
            "Content-Length": str(len(conteudo)),
        },
    )


@router.post("/bd-folder")
async def processar_bd_folder(
    rentabilidades: UploadFile, request: Request, persist: bool = Query(False)
):
    _valida_permissao_carregar_bdfolder(request)

    _: Any = ...

    session = db(request)
    ind_svc = IndicadoresService(
        indicadores_repository=IndicadoresRepository(session),
        rotinas_repository=_,
    )
    fnd_svc = FundosService(
        fundos_repository=FundosRepository(db=session),
        arquivos_repository=ArquivosDatabaseRepository(db=session),
    )

    async with session.begin_nested():
        indicadores = await ind_svc.inserir_rentabilidades(
            rentabilidades, persist=persist
        )
        fundo_pls_rentabilidades = await fnd_svc.inserir_fundo_patrimonio_liquido_rentabilidades(
            rentabilidades, persist=persist
        )
        fundo_cotas_rentabilidades = await fnd_svc.inserir_fundo_cotas_rentabilidades(
            rentabilidades, persist=persist
        )

        return {
            "persist": persist,
            "indicadores": indicadores,
            "fundos": {"pls": fundo_pls_rentabilidades, "rentabilidades": fundo_cotas_rentabilidades},
        }


def _valida_permissao_carregar_bdfolder(request: Request):
    if not AuthService.usuario_possui_funcao(
        "Site Institucional - Carregar arquivo de rentabilidades",
        request.state.user,
    ):
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            "Você não possui autorização para carregar o arquivo de rentabilidades.",
        )
