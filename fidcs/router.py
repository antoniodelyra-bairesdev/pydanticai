"""
Endpoints FastAPI para o módulo FIDCS.

Fornece endpoints REST para:
- Listagem de arquivos e prompts correspondentes
- Processamento automatizado de arquivos FIDC
- Consulta de dados consolidados
"""

from config.swagger import token_field
from fastapi import APIRouter, Depends, Request

# Imports para typing das entidades
from modules.pydanticai.service import PydanticAIServiceImpl
from modules.util.request import db

from .repository import FidcsRepository
from .schema import (
    ArquivoPromptInfoSchema,
    DadosCadastraisResponseSchema,
    DadosConsolidadosSchema,
    ProcessarRequestSchema,
    ProcessarResponseSchema,
)
from .service import FidcsService

router = APIRouter(prefix="/fidcs", tags=["FIDCS"], dependencies=[token_field])


def get_fidcs_service(request: Request) -> FidcsService:
    """
    Factory function para criar instância do FidcsService.

    Args:
        request: Request FastAPI para acesso à sessão do banco

    Returns:
        FidcsService: Service configurado com dependências
    """
    session = db(request)

    # Cria repository
    repository = FidcsRepository(session)

    # Cria service do PydanticAI
    pydantic_ai_service = PydanticAIServiceImpl()

    # Cria service principal
    return FidcsService(repository, pydantic_ai_service)


@router.get("/arquivos-prompts")
async def listar_arquivos_prompts(
    service: FidcsService = Depends(get_fidcs_service),
) -> list[ArquivoPromptInfoSchema]:
    """
    # Lista Arquivos e Prompts Correspondentes

    Lista todos os arquivos PDF na pasta `files/fidcs/` e busca os prompts
    correspondentes na tabela `prompt_tb` baseado no nome do FIDC.

    ## Padrão de Arquivo
    - `FIDC_BEMOL_2024_08.pdf` → FIDC: BEMOL, Ano: 2024, Mês: 08
    - `FIDC_ICRED_2024_09.pdf` → FIDC: ICRED, Ano: 2024, Mês: 09

    ## Resposta
    Para cada arquivo retorna:
    - Informações do arquivo (nome, FIDC, ano, mês)
    - Status do prompt (encontrado/não encontrado)
    - Dados do prompt (ID, descrição, modelo, parâmetros)
    """
    return await service.listar_arquivos_e_prompts()


@router.post("/processar")
async def processar_arquivos(
    request: ProcessarRequestSchema, service: FidcsService = Depends(get_fidcs_service)
) -> ProcessarResponseSchema:
    """
    # Processar Arquivos FIDC

    Processa uma lista de arquivos FIDC selecionados, extraindo dados
    estruturados e armazenando no banco de dados.

    ## Parâmetros de Entrada
    ```json
    {
        "itens": [
            {
                "arquivo": "FIDC_BEMOL_2024_08.pdf",
                "fidc_nome": "BEMOL",
                "ano": 2024,
                "mes": 8,
                "prompt_encontrado": true,
                "prompt_descricao": "Processamento FIDC Bemol",
                "model_name": "groq:llama-3.3-70b-versatile",
                "schema_name": "bemol",
                "is_image": false,
                "temperatura": 0.1,
                "max_tokens": 1440,
                "system_prompt": "Seja preciso...",
                "user_prompt": "Extraia os dados..."
            }
        ]
    }
    ```

    ## Fluxo de Processamento
    1. **Validação**: Verifica se o prompt foi encontrado e schema definido
    2. **Chama PydanticAI**: Executa `executar_consulta_com_arquivo` usando dados do prompt
    3. **Identifica processador**: Seleciona parser específico baseado no schema
    4. **Processa dados**: Executa parser específico do FIDC
    5. **Salva no banco**: Insere dados nas tabelas apropriadas

    ## Tabelas de Destino
    - **indicador_fidc_valor_tb**: Dados periódicos (mês/ano)
    - **fidc_dados_cadastrais_tb**: Dados cadastrais (únicos por ativo)

    ## Transações
    - Cada arquivo é processado em transação separada
    - **Sucesso**: Commit automático
    - **Falha**: Rollback automático

    ## Observações
    - Os dados do prompt são obtidos do endpoint `/arquivos-prompts`
    - Não é necessário consultar o banco novamente para obter dados do prompt
    """
    return await service.processar_arquivos(request)


@router.get("/dados-consolidados")
async def get_dados_consolidados(
    service: FidcsService = Depends(get_fidcs_service),
) -> list[DadosConsolidadosSchema]:
    """
    # Consulta Dados Consolidados

    Executa consulta SQL pré-definida que junta as tabelas de indicadores,
    ativos e dados, retornando informações consolidadas.

    ## Resposta
    Retorna lista de registros com:
    - **apelido**: Nome/apelido do ativo FIDC
    - **indicador_fidc_nm**: Nome do indicador
    - **valor**: Valor numérico do indicador
    - **limite**: Limite estabelecido (se houver)
    - **limite_superior**: Se o limite é superior ou inferior
    - **extra_data**: Dados adicionais em formato JSON
    - **mes**: Mês de referência
    - **ano**: Ano de referência
    - **data_captura**: Data/hora da captura dos dados

    ## Filtros e Ordenação
    - **Filtro automático**: Apenas ativos ativos (`ativo = true`)
    - **Ordenação**: Por apelido → indicador → ano (desc) → mês (desc)
    """
    return await service.get_dados_consolidados()


@router.get("/dados-cadastrais")
async def get_dados_cadastrais(
    service: FidcsService = Depends(get_fidcs_service),
) -> list[DadosCadastraisResponseSchema]:
    """
    # Consulta Dados Cadastrais

    Executa consulta SQL que junta as tabelas de dados cadastrais,
    indicadores e ativos, retornando informações cadastrais dos FIDCs.

    ## Resposta
    Retorna lista de registros com:
    - **apelido**: Nome/apelido do ativo FIDC
    - **indicador_fidc_nm**: Nome do indicador
    - **valor**: Valor do indicador como string
    """
    return await service.get_dados_cadastrais()
