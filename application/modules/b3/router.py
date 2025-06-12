from typing import Literal
from io import BytesIO
import config.database as db
from datetime import date
from config.environment import SessaoFIXType
from config.swagger import token_field
from fastapi import APIRouter, Depends, Request, UploadFile, HTTPException, Response
from requests_toolbelt import MultipartEncoder
from fastapi.responses import JSONResponse
from http import HTTPStatus
from pandas import DataFrame

from modules.auth.model import Usuario
from modules.queue.service import QueueService
from modules.util.request import get_user, user_with_role
from modules.util.mediatypes import CSV

from .schema import RelatorioVoicePostTradeSchema, RelatorioVoicePreTradeSchema
from .service import B3Service, B3ServiceFactory
from .fix.order_entry_application import OrderEntryApplicationSingleton
from .fix.post_trade_application import PostTradeApplicationSingleton

router = APIRouter(
    prefix="/b3",
    tags=["B3"],
    dependencies=[token_field],
)


@router.get("/connected")
def is_connected():
    info: dict[SessaoFIXType, dict[str, bool]] = {
        "ORDER_ENTRY": {
            "reachable": B3Service.is_messaging_reachable("ORDER_ENTRY")[0],
            "session": OrderEntryApplicationSingleton.get_application().session != None,
        },
        "POST_TRADE": {
            "reachable": B3Service.is_messaging_reachable("POST_TRADE")[0],
            "session": PostTradeApplicationSingleton.get_application().session != None,
        },
    }
    return JSONResponse(
        info,
        status_code=HTTPStatus.OK,
    )


@router.get("/voices")
async def listar_voices(request: Request):
    service = B3ServiceFactory.criarService(request.state.db)
    return await service.listar_voices(date.today())


@router.post("/voices/{data_negociacao}/{id_trader}/decisao")
def decisao_voice(
    data_negociacao: date,
    id_trader: str,
    decisao: Literal["ACATO", "REJEIÇÃO"],
    usuario: Usuario = Depends(user_with_role("operacoes.voice.decisao")),
):
    async def executar(data_negociacao: date, id_trader: str):
        async with db.get_session(db.engine) as session, session.begin():
            service = B3ServiceFactory.criarService(session)
            await service.enviar_decisao_voice(
                usuario, decisao, data_negociacao, id_trader
            )

    qs = QueueService()
    qs.enqueue(executar(data_negociacao, id_trader))


@router.get("/test/casamento")
async def teste_casamento(
    request: Request,
    usuario: Usuario = Depends(user_with_role("operacoes.voice.casamento")),
):
    service = B3ServiceFactory.criarService(request.state.db)
    await service.casar_voices_e_alocacoes(usuario, "ORDER_ENTRY")

@router.post('/contingencia/importacao-hub-balcao')
async def contingencia_importacao_alocacoes_hub_balcao(
    request: Request,
    voices: UploadFile,
    boleta: UploadFile
):
    service = B3ServiceFactory.criarService(request.state.db)
    try:
        convertidos = await service.converter_exportacoes(voices.file, boleta.file)
    except:
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, {
            'request_id': request.state.uuid,
            'message': "Formato inválido. Verifique se os arquivos enviados estão no formato correto e se os dados estão corretamente preenchidos. Ou talvez a ordem dos arquivos tenha sido trocada?"
        })
    voices_casados = 0
    alocacoes_casadas = 0
    casamento: dict[int, list[AlocacaoSimulacaoCasamento]] = {}
    for voice in convertidos.voices:
        casadas = service._casar_voice_com_alocacoes(voice, convertidos.boleta)
        alocacoes_casadas += len(casadas)
        voices_casados += 1 if len(casadas) > 0 else 0
        casamento[voice.id] = casadas

    infos = {
        "Participante": [],
        "DataPregao": [],
        "NumeroNegocio": [],
        "NaturazaOperacao": [],
        "Conta": [],
        "QuantidadeConta": [],
        "AlocacaoFinal": [],
        "Documento": [],
        "QuantidadeDocumento": []
    }

    for voice_id in casamento:
        for alocacao in casamento[voice_id]:
            infos["Participante"].append("39-20967")
            infos["DataPregao"].append(alocacao.data_negociacao.strftime("%d/%m/%Y"))
            infos["NumeroNegocio"].append(voice_id)
            infos["NaturazaOperacao"].append(
                "Compra" if alocacao.lado_operacao == 'C' else "Venda"
            )
            conta_cetip = convertidos.cnpj_para_cetip[alocacao.fundo_cnpj]
            infos["Conta"].append(f"{conta_cetip[:5]}.{conta_cetip[5:7]}-{conta_cetip[7:]}")
            infos["QuantidadeConta"].append(
                int(alocacao.quantidade)
            )
            infos["AlocacaoFinal"].append("S")
            infos["Documento"].append(None)
            infos["QuantidadeDocumento"].append(None)
    
    df = DataFrame.from_dict(infos)
    binary = BytesIO()
    df.to_csv(binary, sep=";", index=False)
    binary.seek(0)

    multipart = MultipartEncoder(
        fields={"avisos": 'OK', "arquivo": ('ImportacaoHubBalcao.csv', binary, CSV)}
    )

    return Response(multipart.to_string(), media_type=multipart.content_type)

@router.post("/test/relatorio-pre-trade")
async def teste_relatorio_pre_trade(
    request: Request,
    body: RelatorioVoicePreTradeSchema,
    usuario: Usuario = Depends(user_with_role("operacoes.voice.relatorio.pretrade")),
):
    service = B3ServiceFactory.criarService(request.state.db)
    await service.atualizar_informacoes_voice_pre_trade(usuario, body)


@router.post("/test/relatorio-post-trade")
async def teste_relatorio_post_trade(
    request: Request,
    body: RelatorioVoicePostTradeSchema,
    usuario: Usuario = Depends(user_with_role("operacoes.voice.relatorio.posttrade")),
):
    service = B3ServiceFactory.criarService(request.state.db)
    await service.atualizar_informacoes_voice_post_trade(usuario, body)


@router.post("/test/enviar-decisoes-nao-transmitidas")
async def teste_enviar_decisoes_nao_transmitidas(
    request: Request, usuario: Usuario = Depends(get_user)
):
    service = B3ServiceFactory.criarService(request.state.db)
    await service.enviar_decisoes_nao_transmitidas(usuario)


@router.post("/test/enviar-alocacoes-nao-transmitidas")
async def teste_enviar_alocacoes_nao_transmitidas(
    request: Request, usuario: Usuario = Depends(get_user)
):
    service = B3ServiceFactory.criarService(request.state.db)
    await service.enviar_alocacoes_nao_transmitidas(usuario)
