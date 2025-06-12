import config.database as db

from config.swagger import token_field
from fastapi import APIRouter, UploadFile, HTTPException, Depends, Request
from http import HTTPStatus
from typing import Literal

from modules.auth.service import AuthService, AuthRepository, Usuario
from modules.fundos.repository import FundosRepository
from modules.queue.service import QueueService
from modules.util import mediatypes, request
from modules.websockets.service import WebSocketService

from .schema import (
    AlocacaoSchema,
    BoletaSchema,
    IdentificadorCorretora,
    TipoIdentificadorCorretora,
)
from .service import OperacoesService, OperacoesServiceFactory


router = APIRouter(prefix="/operacoes", tags=["Operações"], dependencies=[token_field])


def get_service(request: Request):
    db = request.state.db
    return OperacoesServiceFactory.criarService(db)


@router.get("/corretoras")
async def _(
    tipo: TipoIdentificadorCorretora,
    valor: str,
    service: OperacoesService = Depends(get_service),
):
    return await service.buscar_corretoras(
        [IdentificadorCorretora(tipo=tipo, valor=valor)]
    )


@router.post("/alocacoes/processamento")
async def processar_boleta_v2(
    file: UploadFile,
    formato: Literal["titpriv"],
    service: OperacoesService = Depends(get_service),
):
    if file.content_type != mediatypes.XLSX:
        raise HTTPException(
            HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "Somente arquivos .xlsx são suportados"
        )
    data = await service.processar_boleta_v2(file.file, formato)
    return data


@router.post("/alocacoes/separacao")
async def separacao_alocacoes(
    formato: Literal["titpriv"],
    estrategia_duplicadas: Literal[
        "ignorar-alterar", "ignorar-criar", "manter-alterar", "manter-criar"
    ],
    alocacoes: list[AlocacaoSchema],
    service: OperacoesService = Depends(get_service),
):
    data = await service.separacao_alocacoes(alocacoes, formato, estrategia_duplicadas)
    return data


@router.post("/alocacoes/boleta")
async def criar_boleta(
    boleta: BoletaSchema,
    service: OperacoesService = Depends(get_service),
    usuario: Usuario = Depends(request.user_with_role("operacoes.alocar")),
):
    return await service.criar_alocacoes(boleta, usuario)


@router.get("/alocacoes/boleta/ws")
async def transmitir_boletas_ws(
    usuario: Usuario = Depends(request.get_user),
):
    async def executar(usuario: Usuario):
        async with db.get_session(db.engine) as session:
            service = OperacoesServiceFactory.criarService(session)
            await service.transmitir_boletas_ws(usuario)

    qs = QueueService()
    qs.enqueue(executar(usuario))


@router.post("/alocacoes/aprovar")
async def aprovar_alocacoes(
    ids_alocacoes: list[int] = Depends(request.query_int_list("ids")),
    usuario: Usuario = Depends(request.user_with_role("operacoes.aprovar")),
):
    async def executar(usuario: Usuario, ids_alocacoes: list[int]):
        async with db.get_session(db.engine) as session, session.begin():
            service = OperacoesServiceFactory.criarService(session)
            await service.aprovar_alocacoes(usuario, ids_alocacoes)

    qs = QueueService()
    qs.enqueue(executar(usuario, ids_alocacoes))


@router.post("/alocacoes/alocar-administrador")
async def alocar_administrador(
    ids_alocacoes: list[int] = Depends(request.query_int_list("ids")),
    usuario: Usuario = Depends(
        request.user_with_role("operacoes.alocar.administrador")
    ),
):
    async def executar(usuario: Usuario, ids_alocacoes: list[int]):
        async with db.get_session(db.engine) as session, session.begin():
            service = OperacoesServiceFactory.criarService(session)
            await service.alocar_administrador(usuario, ids_alocacoes)

    qs = QueueService()
    qs.enqueue(executar(usuario, ids_alocacoes))


@router.post("/alocacoes/cancelar")
async def cancelar_alocacao(
    ids_alocacoes: list[int] = Depends(request.query_int_list("ids")),
    usuario: Usuario = Depends(request.user_with_role("operacoes.cancelar")),
    motivo: str | None = None,
):
    async def executar(usuario: Usuario, ids_alocacoes: list[int]):
        async with db.get_session(db.engine) as session, session.begin():
            service = OperacoesServiceFactory.criarService(session)
            await service.cancelar_alocacoes(usuario, ids_alocacoes, motivo)

    qs = QueueService()
    qs.enqueue(executar(usuario, ids_alocacoes))


@router.post("/alocacoes/cancelar-administrador")
async def cancelar_alocacao_administrador(
    ids_alocacoes: list[int] = Depends(request.query_int_list("ids")),
    usuario: Usuario = Depends(
        request.user_with_role("operacoes.cancelar.administrador")
    ),
    motivo: str | None = None,
):
    async def executar(usuario: Usuario, ids_alocacoes: list[int]):
        async with db.get_session(db.engine) as session, session.begin():
            service = OperacoesServiceFactory.criarService(session)
            await service.cancelar_alocacoes_administrador(
                usuario, ids_alocacoes, motivo
            )

    qs = QueueService()
    qs.enqueue(executar(usuario, ids_alocacoes))


@router.post("/alocacoes/liquidacao")
async def sinalizar_liquidacao(
    ids_alocacoes: list[int] = Depends(request.query_int_list("ids")),
    usuario: Usuario = Depends(request.user_with_role("operacoes.liquidacao")),
):
    async def executar(usuario: Usuario, ids_alocacoes: list[int]):
        async with db.get_session(db.engine) as session, session.begin():
            service = OperacoesServiceFactory.criarService(session)
            await service.sinalizar_liquidacao(usuario, ids_alocacoes)

    qs = QueueService()
    qs.enqueue(executar(usuario, ids_alocacoes))
