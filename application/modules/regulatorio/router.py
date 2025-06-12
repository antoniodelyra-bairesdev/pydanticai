from http import HTTPStatus
from io import BytesIO
import json
from typing import Annotated
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import StreamingResponse
from urllib.parse import quote
from modules.util.mediatypes import stream

from config.swagger import token_field
from fastapi.exceptions import HTTPException

from .schema import (
    CriacaoCategoriaRelatoriosSchema,
    EnvioDocumentosRegulatoriosSchema,
    ReordenarCategoriasSchema,
)
from .service import RegulatorioService, RegulatorioRepository
from modules.arquivos.repository import ArquivosDatabaseRepository
from modules.auth.model import Usuario
from modules.auth.service import AuthService

router = APIRouter(
    prefix="/regulatorio", tags=["Regulatório"], dependencies=[token_field]
)


def get_service(request: Request):
    session = request.state.db
    return RegulatorioService(
        regulatorio_repository=RegulatorioRepository(db=session),
        arquivos_repository=ArquivosDatabaseRepository(db=session),
    )


def validar_permissao_de_site_institucional_do_usuario(request: Request):
    if not AuthService.usuario_possui_funcao(
        "Site Institucional - Alterar documentos regulatórios", request.state.user
    ):
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            "Você não possui autorização para alterar os documentos regulatórios do site institucional.",
        )


@router.get("/publico")
async def documentacao_publica(service: RegulatorioService = Depends(get_service)):
    return await service.categorias_e_documentos()


@router.get("/relatorio/{documento_id}")
async def download_relatorio(
    documento_id: int,
    service: RegulatorioService = Depends(get_service),
):
    documento = await service.baixar_relatorio(documento_id)
    if not documento:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Relatório não encontrado")
    return StreamingResponse(
        stream(BytesIO(documento.conteudo)),
        media_type=documento.arquivo.extensao,
        headers={
            "Content-Disposition": f'attachment; filename="{quote(documento.arquivo.nome)}"',
            "Content-Length": str(len(documento.conteudo)),
        },
    )


@router.delete("/relatorio/{documento_id}")
async def remover_documentacao(
    request: Request,
    documento_id: int,
    service: RegulatorioService = Depends(get_service),
):
    validar_permissao_de_site_institucional_do_usuario(request)
    await service.remover_documentacao(documento_id)


@router.post("/categoria")
async def criar_categoria(
    request: Request,
    dados: CriacaoCategoriaRelatoriosSchema,
    service: RegulatorioService = Depends(get_service),
):
    validar_permissao_de_site_institucional_do_usuario(request)
    return await service.criar_categoria(dados.nome)


@router.put("/categoria")
async def reordenar_categorias(
    request: Request,
    dados: list[ReordenarCategoriasSchema],
    service: RegulatorioService = Depends(get_service),
):
    validar_permissao_de_site_institucional_do_usuario(request)
    return await service.reordenar_categorias(dados)


@router.get("/categoria/plano-de-fundo")
async def buscar_planos_de_fundo(service: RegulatorioService = Depends(get_service)):
    return await service.buscar_planos_de_fundo()


@router.put("/categoria/plano-de-fundo")
async def atribuir_plano_de_fundo(
    request: Request,
    categoria_id: int,
    plano_de_fundo_id: int | None,
    service: RegulatorioService = Depends(get_service),
):
    validar_permissao_de_site_institucional_do_usuario(request)
    return await service.atribuir_plano_de_fundo_a_categoria(
        categoria_id=categoria_id, plano_de_fundo_id=plano_de_fundo_id
    )


@router.delete("/categoria/{categoria_id}")
async def remover_categoria(
    request: Request,
    categoria_id: int,
    service: RegulatorioService = Depends(get_service),
):
    validar_permissao_de_site_institucional_do_usuario(request)
    await service.remover_categoria(categoria_id)


@router.post("/categoria/{categoria_id}/relatorio")
async def adicionar_documentacao(
    request: Request,
    categoria_id: int,
    metadados: Annotated[str, Form()],
    arquivos: Annotated[list[UploadFile], File()] = [],
    service: RegulatorioService = Depends(get_service),
):
    validar_permissao_de_site_institucional_do_usuario(request)
    infos = EnvioDocumentosRegulatoriosSchema(**json.loads(metadados))
    return await service.adicionar_documentacao(categoria_id, arquivos, infos.dados)
