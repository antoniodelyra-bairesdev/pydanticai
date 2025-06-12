from typing import Annotated
from fastapi import APIRouter, Response, Depends, Request, Query
from requests_toolbelt import MultipartEncoder

from modules.auth.model import Usuario
from modules.websockets.service import WebSocketService
from modules.util.request import user_with_role

from config.swagger import token_field

from .schema import BodyCriacaoDadosExecucaoDaycovalSchema, DadosExecucaoDaycovalSchema, ExecucaoDaycovalSchema, FundoInquilinoSchema
from .service import CobrancaService, CobrancaServiceFactory

router = APIRouter(prefix="/cobranca", tags=["Cobranças"], dependencies=[token_field])


def get_service(request: Request):
    session = request.state.db
    return CobrancaServiceFactory.criarService(session)


@router.post("/execucoes/daycoval/criacao-cobranca")
async def criacao_cobranca_daycoval(
    dados: list[BodyCriacaoDadosExecucaoDaycovalSchema] | int,
    tipo_execucao_id: Annotated[int, Query()],
    usuario: Usuario = Depends(user_with_role('cobrancas.execucao.daycoval.criacao_cobranca.criar'))
):
    CobrancaService.tentativa_acesso_execucao_daycoval(dados, tipo_execucao_id, usuario)

@router.get("/inquilinos/{fundo_id}")
async def inquilinos_fundo(
    fundo_id: int,
    service: CobrancaService = Depends(get_service),
    _: Usuario = Depends(user_with_role("locacoes.inquilinos.listar")),
):
    inquilinos = await service.inquilinos_fundo(fundo_id)
    return [
        inquilino
        for inquilino in [
            FundoInquilinoSchema.from_model(inquilino, fundo_id)
            for inquilino in inquilinos
        ]
        if inquilino != None
    ]

@router.get("/boletos/ws")
async def dados_execucao_ws(
    request: Request,
    usuario: Usuario = Depends(user_with_role("locacoes.boletos.listar")),
):
    svc = CobrancaServiceFactory.criarService(request.state.db)
    boletos = await svc.dados_execucao()
    execucoes = await svc.execucoes_daycoval()
    await WebSocketService.send_json(
        {
            "canal": "locacoes.boletos",
            "tipo": "boletos.todos",
            "dados": [DadosExecucaoDaycovalSchema.from_model(boleto) for boleto in boletos],
        },
        user_ids=[usuario.id],
    )
    await WebSocketService.send_json(
        {
            "canal": "locacoes.boletos",
            "tipo": "execucoes_daycoval.todas",
            "dados": [ExecucaoDaycovalSchema.from_model(execucao) for execucao in execucoes]
        }
    )