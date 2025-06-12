from http import HTTPStatus
import logging
from typing import Annotated


from fastapi import APIRouter, Depends, Request, Query, HTTPException, BackgroundTasks

from config.swagger import token_field
from modules.util.request import db
from modules.util.validators import get_filtering, get_ordering

from .repository import AtivosRepository
from .schema import (
    AnalistaSchema,
    AssetTransactionSchema,
    EmissorSchema,
    EmissorTransactionSchema,
    GrupoTransactionSchema,
    SetorSchema,
    SetorTransactionSchema,
    UserSchema,
)
from .service import AtivosService


def get_service(request: Request, bg_tasks: BackgroundTasks):
    session = db(request)
    return AtivosService(
        ativos_repository=AtivosRepository(db=session),
        background_tasks=bg_tasks,
    )


router = APIRouter(prefix="/ativos", tags=["Ativos"], dependencies=[token_field])

ordering = '<pre><code>type SortType = "asc" | "desc"</code></pre>'
filters = """<pre><code>type FilterType = "blank" | "notBlank" | {
    "equals": string
} | {
    "notEqual": string
} | {
    "contains": string
} | {
    "notContains": string
} | {
    "startsWith": string
} | {
    "endsWith": string
} | {
    "greaterThan": string
} | {
    "greaterThanOrEqual": string
} | {
    "lessThan": string
} | {
    "lessThanOrEqual": string
} | {
    "inRange": [string, string]
} | {
    "set": string[]
} | {
    "notInSet": string[]
}
</code></pre>"""

campos_ativos = """<pre><code>type ColsAtivo = "codigo" | "emissor" | "indice" | "tipo" | "valor_emissao" | "data_emissao" | "inicio_rentabilidade" | "data_vencimento" | "taxa" | "apelido" | "isin" | "serie" | "emissao"""
campos_eventos = """<pre><code>type ColsEvento = "ativo_codigo" | "data_pagamento" | "tipo_evento" | "percentual" | "pu_evento" | "pu_calculado"</code></pre>"""

ordenacao_description_ativos = (
    "<p>Formato JSON:</p>"
    + """
<pre><code>type ordenacao = [
    {
        "colId": ColsAtivo,
        "sort": SortType
    },
    ...
]
</code></pre>
"""
    + "<p>Tipos:</p>"
    + ordering
    + campos_ativos
)

filtro_description_ativos = (
    "<p>Formato JSON:</p>"
    + """
<pre><code>type filtros_ativos = {
    [ColsAtivo]: FilterType,
    ...
}
</code></pre>
"""
    + "<p>Tipos:</p>"
    + filters
    + campos_ativos
)

ordenacao_description_eventos = (
    "<p>Formato JSON:</p>"
    + """
<pre><code>type ordenacao = [
    {
        "colId": ColsEvento,
        "sort": SortType
    },
    ...
]
</code></pre>
"""
    + "<p>Tipos:</p>"
    + ordering
    + campos_eventos
)

filtro_description_eventos = (
    "<p>Formato JSON:</p>"
    + """
<pre><code>type filtros_eventos = {
    [ColsEvento]: FilterType,
    ...
}
</code></pre>
"""
    + "<p>Tipos:</p>"
    + filters
    + campos_eventos
)


@router.get("/")
async def ativos(
    deslocamento: int = 0,
    quantidade: int = 20,
    ordenacao_ativos: Annotated[
        str, Query(description=ordenacao_description_ativos)
    ] = "",
    filtros_ativos: Annotated[str, Query(description=filtro_description_ativos)] = "",
    service: AtivosService = Depends(get_service),
):
    dados_ordenacao = get_ordering(ordenacao_ativos)
    dados_filtragem = get_filtering(filtros_ativos)

    ativos, total = await service.lista_ativos(
        deslocamento, quantidade, dados_ordenacao, dados_filtragem
    )
    return {"ativos": ativos, "total": total}


@router.get("/total")
async def total_ativos(service: AtivosService = Depends(get_service)):
    return await service.total_ativos()


@router.get("/eventos/total")
async def total_eventos(service: AtivosService = Depends(get_service)):
    return await service.total_eventos()


@router.get("/eventos")
async def eventos(
    deslocamento: int = 0,
    quantidade: int = 20,
    ordenacao_eventos: Annotated[
        str, Query(description=ordenacao_description_eventos)
    ] = "",
    filtros_eventos: Annotated[str, Query(description=filtro_description_eventos)] = "",
    service: AtivosService = Depends(get_service),
):
    dados_ordenacao = get_ordering(ordenacao_eventos)
    dados_filtragem = get_filtering(filtros_eventos)

    ativos, eventos, total = await service.lista_eventos(
        deslocamento, quantidade, dados_ordenacao, dados_filtragem
    )
    return {"ativos": ativos, "eventos": eventos, "total": total}


@router.get("/codigos")
async def codigos(service: AtivosService = Depends(get_service)):
    codigos = await service.lista_codigos()
    return codigos


@router.get("/nomes_emissores")
async def nomes_emissores(service: AtivosService = Depends(get_service)):
    nomes = await service.nomes_emissores()
    return nomes


@router.get("/tipo_evento")
async def tipo_eventos(service: AtivosService = Depends(get_service)):
    return await service.tipo_evento(False)


@router.get("/tipo_evento/suportados")
async def tipo_eventos_suportados(service: AtivosService = Depends(get_service)):
    return await service.tipo_evento()


@router.get("/tipo_ativos")
async def tipo_ativos(service: AtivosService = Depends(get_service)):
    return await service.tipo_ativos()


@router.get("/indice")
async def indice_ativos(service: AtivosService = Depends(get_service)):
    return await service.indice_ativos()


@router.put("/transacao")
async def transacao(
    diff: AssetTransactionSchema, service: AtivosService = Depends(get_service)
):
    delete = diff.deleted or []
    update = diff.modified or []
    insert = diff.added or []
    await service.transacao(delete, update, insert)
    return


@router.get("/emissores")
async def emissores(
    deslocamento: int = 0,
    quantidade: int = 20,
    service: AtivosService = Depends(get_service),
):
    emissores, total = await service.emissores(deslocamento, quantidade)
    return {
        "total": total,
        "emissores": [EmissorSchema.from_model(emissor) for emissor in emissores],
    }


@router.put("/emissores/transacao")
async def transacao_emissores(
    diff: EmissorTransactionSchema, service: AtivosService = Depends(get_service)
):
    update = diff.modified or []
    insert = diff.added or []
    await service.transacao_emissores(update, insert)


@router.get("/emissores/{id}")
async def emissor(
    id: str,
    service: AtivosService = Depends(get_service),
):
    try:
        codigo = int(id)
    except:
        raise HTTPException(HTTPStatus.NOT_FOUND)
    emissor = await service.emissor(codigo)
    if not emissor:
        raise HTTPException(HTTPStatus.NOT_FOUND)
    return EmissorSchema.from_model(emissor)


@router.get("/setores")
async def setores(
    with_sys_data: bool | None = None,
    service: AtivosService = Depends(get_service),
):
    setores = await service.setores(bool(with_sys_data))
    return [
        SetorSchema(
            id=setor.id,
            nome=setor.nome,
            sistema_icone=setor.icone.icone if with_sys_data and setor.icone else None,
        ).model_dump(exclude_none=True)
        for setor in setores
    ]


@router.put("/setores/transacao")
async def transacao_setores(
    diff: SetorTransactionSchema, service: AtivosService = Depends(get_service)
):
    update = diff.modified or []
    insert = diff.added or []
    await service.transacao_setores(update, insert)
    return


@router.get("/grupos")
async def grupos(service: AtivosService = Depends(get_service)):
    return await service.grupos()


@router.put("/grupos/transacao")
async def transacao_grupos(
    diff: GrupoTransactionSchema, service: AtivosService = Depends(get_service)
):
    update = diff.modified or []
    insert = diff.added or []
    await service.transacao_grupos(update, insert)
    return


@router.get("/analistas")
async def analistas(service: AtivosService = Depends(get_service)):
    analistas = await service.analistas()
    return [
        AnalistaSchema(
            id=analista.id,
            user=UserSchema(
                id=analista.user_id, email=analista.user.email, nome=analista.user.nome
            ),
        )
        for analista in analistas
    ]


@router.get("/{codigo}")
async def ativo(codigo: str, service: AtivosService = Depends(get_service)):
    ativo = await service.ativo(codigo)
    return ativo
