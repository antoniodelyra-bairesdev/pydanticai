"""
Módulo de rotas FastAPI para integração com PydanticAI.

Este módulo fornece endpoints REST para executar consultas de IA usando PydanticAI,
listar schemas disponíveis e modelos de IA cadastrados no banco de dados.

Endpoints:
    POST /pydantic-ai/consulta: Executa consulta de IA com schema estruturado
    POST /pydantic-ai/consulta-com-arquivo: Executa consulta com processamento de arquivo
    GET /pydantic-ai/schemas-disponiveis: Lista schemas disponíveis
    GET /pydantic-ai/modelos-disponiveis: Lista modelos de IA cadastrados

Funcionalidades:
    - Execução de consultas de IA com diferentes modelos e schemas
    - Suporte a consultas com e sem banco de dados
    - Processamento de arquivos via API externa
    - Validação de entrada e tratamento de erros
    - Dependency injection para serviços
    - Integração opcional com repositório de dados
"""

from config.swagger import token_field
from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile, status
from modules.integrations.enums import FerramentaExtracaoEnum, TipoExtracaoEnum
from modules.repository import BaseRepositoryImpl
from modules.util.request import db

from .model import ClientModel, ModelSchema, Prompt
from .repository import PydanticAIRepository
from .schema.api import ConsultaRequestSchema, ConsultaResponseSchema, ModeloDisponivelSchema
from .service import PydanticAIService, PydanticAIServiceImpl

router = APIRouter(prefix="/pydantic-ai", tags=["PydanticAI"], dependencies=[token_field])


def get_service() -> PydanticAIService:
    """
    Factory function para criar uma instância standalone do serviço PydanticAI.
    Esta versão NÃO requer conexão com banco de dados.
    """
    return PydanticAIServiceImpl()


def get_service_with_database(request: Request) -> PydanticAIService:
    """
    Factory function para criar uma instância do serviço PydanticAI com banco.
    Esta versão integra com o banco de dados para obter modelos cadastrados.
    """
    session = db(request)

    repository = PydanticAIRepository(
        base_repository_prompt=BaseRepositoryImpl[Prompt](db_session=session, model_class=Prompt),
        base_repository_client_model=BaseRepositoryImpl[ClientModel](
            db_session=session, model_class=ClientModel
        ),
        base_repository_model_schema=BaseRepositoryImpl[ModelSchema](
            db_session=session, model_class=ModelSchema
        ),
    )

    return PydanticAIServiceImpl(repository=repository)


@router.post("/consulta")
async def executar_consulta_ia(
    body: ConsultaRequestSchema,
    service: PydanticAIService = Depends(get_service),
) -> ConsultaResponseSchema:
    """
    # Executar Consulta de IA

    Executa uma consulta usando PydanticAI com os parâmetros especificados e retorna
    uma resposta estruturada conforme o schema definido.

    ## Parâmetros de Entrada

    - **user_prompt** (string, obrigatório): O prompt principal enviado pelo usuário
    - **model** (string, opcional): Modelo de IA a ser utilizado
    - **system_prompt** (string, opcional): Instruções do sistema para o modelo
    - **retries** (integer, opcional): Número de tentativas em caso de falha
    - **max_tokens** (integer, opcional): Máximo de tokens na resposta
    - **temperature** (float, opcional): Criatividade da resposta, 0.0-1.0
    - **schema_name** (string, opcional): Nome do schema de resposta
    - **doc** (string, opcional): Documento adicional para contexto

    ## Resposta

    Retorna um objeto `ConsultaResponseSchema` contendo:

    - **resultado**: Resposta estruturada conforme o schema especificado
    - **tempo_execucao**: Tempo de execução em segundos
    - **tokens_utilizados**: Número estimado de tokens utilizados
    - **modelo_utilizado**: Nome do modelo de IA utilizado
    - **schema_utilizado**: Nome do schema de resposta utilizado

    ## Exemplos de Uso

    ### Consulta Simples
    ```json
    {
        "user_prompt": "Explique o que é inteligência artificial",
        "model": "groq:llama-3.3-70b-versatile",
        "temperature": 0.3
    }
    ```

    ### Consulta com Documento
    ```json
    {
        "user_prompt": "Analise este documento e extraia os pontos principais",
        "doc": "Conteúdo do documento para análise...",
        "schema_name": "icred"
    }
    ```

    ## Códigos de Erro

    - **400 Bad Request**: Parâmetros inválidos ou schema não encontrado
    - **500 Internal Server Error**: Erro interno na execução da consulta

    ## Notas

    - Tokens são estimados baseados no tamanho do prompt e resposta
    """
    try:
        resultado = await service.executar_consulta(
            user_prompt=body.user_prompt,
            model=body.model,
            system_prompt=body.system_prompt,
            retries=body.retries,
            max_tokens=body.max_tokens,
            temperature=body.temperature,
            schema_name=body.schema_name,
            doc=body.doc,
        )

        return resultado
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parâmetros inválidos")


@router.post("/consulta-com-arquivo")
async def executar_consulta_com_arquivo(
    arquivo: UploadFile,
    user_prompt: str = Form(default="Resuma o conteúdo do documento."),
    ferramenta_extracao: FerramentaExtracaoEnum | None = Form(default=None),
    tipo_extracao: TipoExtracaoEnum = Form(...),
    model: str = Form(default="groq:llama-3.3-70b-versatile"),
    system_prompt: str = Form(default="Seja preciso e direto nas respostas."),
    retries: int = Form(default=2, ge=1, le=5),
    max_tokens: int = Form(default=1440, ge=1, le=8000),
    temperature: float = Form(default=0.1, ge=0.0, le=2.0),
    schema_name: str = Form(default="default"),
    service: PydanticAIService = Depends(get_service),
) -> ConsultaResponseSchema:
    """
    # Executar Consulta de IA com Arquivo

    Executa uma consulta de IA processando primeiro um arquivo enviado e usando
    seu conteúdo extraído como contexto para a análise.

    ## Parâmetros de Entrada

    - **arquivo** (file, obrigatório): Arquivo a ser processado (PDF, DOCX, TXT)
    - **user_prompt** (string, obrigatório): Pergunta ou instrução sobre o arquivo
    - **ferramenta_extracao** (string, opcional): Ferramenta para extração
      - `docling`: Para arquivos PDF usando DocLing (padrão)
      - `pypdf`: Para arquivos PDF usando PyPDF
      - `docx2txt`: Para arquivos DOCX usando docx2txt
    - **tipo_extracao** (string, obrigatório): Tipo de extração desejado
      - `markdown`: Extrai conteúdo formatado em Markdown
      - `dados-brutos`: Extrai texto bruto do documento
      - `imagens`: Extrai texto de imagens do documento
    - **model** (string, opcional): Modelo de IA a ser utilizado
    - **system_prompt** (string, opcional): Instruções do sistema
    - **retries** (integer, opcional): Número de tentativas em caso de falha
    - **max_tokens** (integer, opcional): Máximo de tokens na resposta
    - **temperature** (float, opcional): Criatividade da resposta
    - **schema_name** (string, opcional): Nome do schema de resposta
    """
    try:
        resultado = await service.executar_consulta_com_arquivo(
            user_prompt=user_prompt,
            arquivo=arquivo,
            ferramenta_extracao=ferramenta_extracao,
            tipo_extracao=tipo_extracao,
            model=model,
            system_prompt=system_prompt,
            retries=retries,
            max_tokens=max_tokens,
            temperature=temperature,
            schema_name=schema_name,
        )

        return resultado
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parâmetros inválidos")


@router.get("/schemas-disponiveis")
async def listar_schemas_disponiveis() -> list[str]:
    """
    Lista todos os schemas disponíveis para uso nas consultas.

    Esta rota não requer banco de dados, pois os schemas são definidos no código.

    Returns:
        list[str]: Lista de schemas disponíveis
    """
    from .enum_modules import ModelSchemaEnum

    return ModelSchemaEnum.get_available_schemas()


@router.get("/modelos-disponiveis")
async def listar_modelos_disponiveis(
    service: PydanticAIService = Depends(get_service_with_database),
) -> list[ModeloDisponivelSchema]:
    """
    Lista modelos de IA disponíveis.

    Args:
        service: Serviço injetado via dependency injection

    Returns:
        list[ModeloDisponivelSchema]: Lista de modelos disponíveis
    """
    try:
        modelos = await service.listar_modelos_disponiveis()
        return modelos
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar modelos",
        )
