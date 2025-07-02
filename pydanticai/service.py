from pydantic_ai import Agent, RunContext
from typing import Any, Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from modules.pydanticai.enum import ModelSchemaEnum

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()


# Função para criar o agente
def create_agent(
    model: str,
    system_prompt: str,
    retries: int,
    max_tokens: int,
    temperature: float,
    schema_name: str,
    doc: Optional[str] = "",
):
    schema_class = ModelSchemaEnum.get_schema_class(schema_name)
    return Agent(
        model=model,
        output_type=schema_class,
        system_prompt=system_prompt,
        output_retries=retries,
        model_settings={"temperature": temperature, "max_tokens": max_tokens},
    )


# Função para adicionar documento, será chamada se o documento for fornecido
async def adicionar_documento(ctx: RunContext[str]) -> str:
    return f"Documento a ser analisado: <doc> {ctx.deps} </doc>"


# Função assíncrona para executar a consulta com parâmetros default
async def executar_consulta(
    user_prompt: str,
    model: str = "google-gla:gemini-2.5-flash-preview-05-20",
    system_prompt: str = "Seja preciso e direto nas respostas.",
    retries: int = 2,
    max_tokens: int = 1440,
    temperature: float = 0.1,
    schema_name: str = "default",
    doc: Optional[str] = "",
) -> Any:
    try:
        agent = create_agent(
            model, system_prompt, retries, max_tokens, temperature, schema_name, doc
        )

        if doc:  # Se há documento, usa o decorador system_prompt
            agent_with_deps = Agent(
                model=model,
                deps_type=str,
                output_type=agent.output_type,
                system_prompt=system_prompt,
                output_retries=retries,
                model_settings={"temperature": temperature, "max_tokens": max_tokens},
            )

            @agent_with_deps.system_prompt
            async def adicionar_documento_deps(ctx: RunContext[str]) -> str:
                return f"Documento a ser analisado: <doc> {ctx.deps} </doc>"

            resultado = await agent_with_deps.run(user_prompt, deps=doc)
        else:
            # Caso contrário, não usa as dependências
            resultado = await agent.run(user_prompt)

        return resultado
    except Exception as e:
        print(f"Erro ao executar consulta: {e}")
        raise


# Classe Pydantic para receber os parâmetros de consulta
class ConsultaRequest(BaseModel):
    user_prompt: str
    model: str = "google-gla:gemini-2.5-flash-preview-05-20"
    system_prompt: str = "Seja preciso e direto nas respostas."
    retries: int = 2
    max_tokens: int = 1440
    temperature: float = 0.1
    schema_name: str = "default"
    doc: Optional[str] = ""
