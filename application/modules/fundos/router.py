from http import HTTPStatus
from io import BytesIO
import json
from datetime import date
from typing import Annotated
from urllib.parse import quote
from fastapi import APIRouter, Request, UploadFile, Depends, File, Form

from config.swagger import token_field
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Query
from modules.util.request import db, get_user
from modules.util.mediatypes import stream
from starlette.responses import StreamingResponse

from .schema import (
    AtualizacaoInternaFundosSchema,
    FundoCategoriaDocumentoSchema,
    FundoDetalhesInformacoesPublicasSchema,
    PatchFundoSiteInstitucionalSchema,
    PostFundoSiteInstitucionalSchema,
    PublicarDetalhesResponseSchema,
    UpdateFundo,
    CreateFundoResponse,
    FundoSchema,
    FundoCaracteristicaExtraSchema,
    PublicacaoMateriaisMassaSchema,
)
from .service import FundosService
from .repository import FundosRepository

from modules.arquivos.repository import ArquivosDatabaseRepository
from modules.auth.model import Usuario
from modules.auth.service import AuthService

router = APIRouter(prefix="/fundos", tags=["Fundos"], dependencies=[token_field])


def get_service(request: Request):
    session = db(request)
    return FundosService(
        fundos_repository=FundosRepository(db=session),
        arquivos_repository=ArquivosDatabaseRepository(db=session),
    )


def validar_permissao_de_alteracao_fundos_site_institucional(request: Request):
    if not AuthService.usuario_possui_funcao(
        "Site Institucional - Alterar fundos", request.state.user
    ):
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            "Você não possui autorização para alterar os fundos disponibilizados no site institucional.",
        )


def validar_permissao_de_alteracao_documentacao_fundo(request: Request):
    if not AuthService.usuario_possui_funcao(
        "Fundos - Alterar documentação", request.state.user
    ):
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            "Você não possui autorização para alterar a documentação de nenhum fundo.",
        )


@router.get("/", tags=["Fundos"])
async def fundos(service: FundosService = Depends(get_service)) -> list[FundoSchema]:
    return await service.fundos()


@router.post("/", tags=["Fundos"])
async def inserir_fundo(
    body: UpdateFundo, service: FundosService = Depends(get_service)
) -> CreateFundoResponse:
    return await service.inserir_fundo(body)


@router.put("/{id}", tags=["Fundos"])
async def atualizar_fundo(
    id: int,
    dados_serializados: Annotated[str, Form()],
    novos_arquivos: Annotated[list[UploadFile], File()] = [],
    service: FundosService = Depends(get_service),
):
    dicionario = json.loads(dados_serializados)
    dados = AtualizacaoInternaFundosSchema(**dicionario)
    return await service.atualizar_fundo(id, dados, novos_arquivos)


@router.get("/documentos/categorias", tags=["Fundos"])
async def fundos_categorias_documentos(
    service: FundosService = Depends(get_service),
):
    categorias = await service.fundo_categorias_documentos()
    return [
        FundoCategoriaDocumentoSchema(id=categoria.id, nome=categoria.nome)
        for categoria in categorias
    ]


@router.get("/documentos/{id}", tags=["Fundos"])
async def fundo_documento(
    id: int,
    service: FundosService = Depends(get_service),
    usuario: Usuario = Depends(get_user),
):
    usuario_possui_acesso_interno = "Acesso Interno" in {
        funcao.nome for funcao in usuario.funcoes
    }
    documento = await service.fundo_documento(id, usuario_possui_acesso_interno)
    if documento == None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Fundo não encontrado")

    return StreamingResponse(
        stream(BytesIO(documento.conteudo)),
        media_type=documento.arquivo.extensao,
        headers={
            "Content-Disposition": f'attachment; filename="{quote(documento.arquivo.nome)}"',
            "Content-Length": str(len(documento.conteudo)),
        },
    )


@router.get("/caracteristicas-extras", tags=["Fundos"])
async def fundos_caracteristicas_extras(
    service: FundosService = Depends(get_service),
):
    caracteristicas = await service.fundo_caracteristicas_extras()
    return [
        FundoCaracteristicaExtraSchema(id=categoria.id, nome=categoria.nome)
        for categoria in caracteristicas
    ]


@router.get("/custodiantes", tags=["Fundos"])
async def fundos_custodiantes(
    service: FundosService = Depends(get_service),
):
    return await service.fundos_custodiantes()


@router.get("/controladores", tags=["Fundos"])
async def fundos_controladores(
    service: FundosService = Depends(get_service),
):
    return await service.fundos_controladores()


@router.get("/administradores", tags=["Fundos"])
async def fundos_administradores(
    service: FundosService = Depends(get_service),
):
    return await service.fundos_administradores()


@router.get("/institucionais/classificacoes")
async def fundos_site_institucional_classificacoes(
    service: FundosService = Depends(get_service),
):
    return await service.fundos_classificacoes_site_institucional()


@router.get("/institucionais/tipos")
async def fundos_site_institucional_tipos(
    service: FundosService = Depends(get_service),
):
    return await service.fundos_tipos_site_institucional()


@router.get("/institucionais")
async def fundos_site_institucional(service: FundosService = Depends(get_service)):
    fundos = await service.fundos_site_institucional()
    return [
        FundoDetalhesInformacoesPublicasSchema.from_model(fundo).com_distribuidores()
        for fundo in fundos
    ]


@router.get("/institucionais/{nome_ou_ticker}")
async def fundo_detalhes_site_institucional(
    nome_ou_ticker: str,
    service: FundosService = Depends(get_service),
):
    nome_ou_ticker = nome_ou_ticker.replace("-", " ")
    detalhes = await service.detalhes_fundo_site_institucional(nome_ou_ticker)
    return FundoDetalhesInformacoesPublicasSchema.from_model(
        detalhes, com_documentos=True
    )


@router.post("/institucionais", tags=["Site Institucional"])
async def publica_fundo_site_institucional(
    body: PostFundoSiteInstitucionalSchema,
    service: FundosService = Depends(get_service),
):
    site_institucional_fundo_id = await service.publica_fundo_site_institucional(
        fundo_id=body.fundo_id,
        detalhes_fundo=body.detalhes,
        caracteristicas_extras_ids=body.caracteristicas_extras_ids,
        documentos_ids=body.documentos_ids,
        indices_benchmark=body.indices_benchmark,
        distribuidores_ids=body.distribuidores_ids,
    )

    return PublicarDetalhesResponseSchema(
        message=f"Fundo criado com sucesso. Id do novo fundo criado: {site_institucional_fundo_id}"
    )


@router.post("/institucionais/publicacao-massa", tags=["Site Institucional"])
async def publicar_materiais_publicitarios_em_massa(
    dados_serializados: Annotated[str, Form()],
    novos_arquivos: Annotated[list[UploadFile], File()] = [],
    service: FundosService = Depends(get_service),
):
    dicionarios = json.loads(dados_serializados)
    dados = PublicacaoMateriaisMassaSchema(**dicionarios)
    await service.publicacao_massa(dados, novos_arquivos)
    return dados


@router.patch("/institucionais/{id}", tags=["Site Institucional"])
async def edita_fundo_site_institucional_publicado(
    id: int,
    body: PatchFundoSiteInstitucionalSchema,
    service: FundosService = Depends(get_service),
) -> PublicarDetalhesResponseSchema:
    await service.edita_fundo_site_institucional(
        site_institucional_fundo_id=id,
        detalhes_fundo=body.detalhes,
        caracteristicas_extras_para_publicacao_ids=body.caracteristicas_extras_para_publicacao_ids,
        caracteristicas_extras_para_despublicacao_ids=body.caracteristicas_extras_para_despublicacao_ids,
        documentos_para_publicacao_ids=body.documentos_para_publicacao_ids,
        documentos_para_despublicacao_ids=body.documentos_para_despublicacao_ids,
        indices_benchmark_para_publicacao=body.indices_benchmark_para_publicacao,
        indices_benchmark_para_despublicacao=body.indices_benchmark_para_despublicacao,
        distribuidores_para_publicacao_ids=body.distribuidores_para_publicacao_ids,
        distribuidores_para_despublicacao_ids=body.distribuidores_para_despublicacao_ids,
    )

    return PublicarDetalhesResponseSchema(message=f"Fundo {id} alterado com sucesso")


@router.delete("/institucionais/{id}")
async def despublica_fundo_site_institucional(
    id: int, service: FundosService = Depends(get_service)
):
    await service.despublica_fundo_site_institucional(id)


@router.get("/{id}", tags=["Fundos"])
async def detalhes_fundo(id: int, service: FundosService = Depends(get_service)):
    fundo = await service.get_fundo(id)
    return (
        FundoSchema.from_model(fundo)
        .com_documentos()
        .com_indices()
        .com_mesas()
        .com_caracteristicas_extras()
        .com_publicacao()
        .com_detalhes_publicacao()
        .com_distribuidores()
    )


@router.get("/rentabilidades/cotas")
async def fundo_rentabilidades_cotas(
    fundos_ids: str = Query(
        ...,
        title="Ids dos fundos",
        description="Ids dos fundos que terão as rentabilidades de seus patrimônios líquidos listados",
    ),
    data_referencia: date | None = Query(
        None,
        title="Data de referência",
        description="Data utilizada como referência para a listagem das rentabilidades. Caso não seja específicada, será utilizada a data atual",
    ),
    service: FundosService = Depends(get_service),
):
    """
    Lista o preço das cotas e as rentabilidades do dia, mês, ano 12, 24 e 36 meses a partir da [data_referencia] das cotas dos fundos
    identificados em [fundo_ids].\n
    Caso não preço da cota na [data_referencia], será listado o preço da cota da data anterior mais próxima.
    """
    if fundos_ids == "":
        raise HTTPException(
            422,
            """
            É obrigatório passar pelo menos o id de um fundo em fundos_ids.
            Para passar mais de um id, passe-os separados por vírgula
            """,
        )

    try:
        fundos_ids_tratados = [int(id) for id in fundos_ids.split(",")]
    except ValueError:
        raise HTTPException(
            422,
            "Um ou mais id informado na lista de ids de fundos é inválido. Ids devem ser números inteiros",
        )

    return await service.get_fundos_cotas_rentabilidades(
        data_referencia=data_referencia, fundos_ids=fundos_ids_tratados
    )


@router.post("/rentabilidades/cotas")
async def inserir_cotas_rentabilidades(
    rentabilidades: UploadFile,
    persist: bool = Query(
        False,
        title="Persistência do dado",
        description="Se for verdadeiro, armazena os dados no banco e diz quais fundos tiveram suas rentabilidades armazenadas ou não.\n"
        + "Caso contrário, devolve as informações processadas sem armazená-las.",
    ),
    service: FundosService = Depends(get_service),
):
    """
    Insere as cotas e rentabilidades do dia, mês, ano, 12 meses, 24 meses e 36 meses das cotas
    mais recentes dos fundos presentes no arquivo carregado.
    """

    return await service.inserir_fundo_cotas_rentabilidades(
        rentabilidades, persist=persist
    )


@router.get("/rentabilidades/patrimonio_liquido")
async def fundo_rentabilidades_patrimonio_liquido(
    fundos_ids: str = Query(
        ...,
        title="Ids dos fundos",
        description="Ids dos fundos que terão as rentabilidades de seus patrimônios líquidos listados",
    ),
    data_referencia: date | None = Query(
        None,
        title="Data de referência",
        description="Data utilizada como referência para a listagem das rentabilidades. Caso não seja específicada, será utilizada a data atual",
    ),
    service: FundosService = Depends(get_service),
):
    """
    Lista patrimônio líquido e médias de 12, 24 e 36 meses dos patrimônios líquidos a partir da [data_referencia] dos fundos
    identificados em [fundo_ids].\n
    Caso não haja patrimônio líquido na [data_referencia], será listado o patrimônio líquido da data anterior mais próxima.
    """

    if fundos_ids == "":
        raise HTTPException(
            422,
            """
            É obritório passar pelo menos o id de um fundo em fundos_ids.
            Para passar mais de um id, passe-os separados por vírgula
            """,
        )

    try:
        fundos_ids_tratados = [int(id) for id in fundos_ids.split(",")]
    except ValueError:
        raise HTTPException(
            422,
            "Um ou mais id informado na lista de ids de fundos é inválido. Ids devem ser números inteiros",
        )

    return await service.get_patrimonio_liquido_rentabilidades(
        data_referencia=data_referencia, fundos_ids=fundos_ids_tratados
    )


@router.post("/rentabilidades/patrimonio_liquido")
async def inserir_patrimonio_liquido_rentabilidades(
    rentabilidades: UploadFile,
    service: FundosService = Depends(get_service),
):
    """
    Insere o patrimônio líquido e as médias de 12, 24 e 36 meses do patrimônio
    líquido mais recente dos fundos presentes no arquivo carregado.
    """
    return await service.inserir_fundo_patrimonio_liquido_rentabilidades(rentabilidades)
