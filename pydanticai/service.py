"""
Módulo de serviço para integração com PydanticAI.

Este módulo fornece uma interface abstrata e implementação concreta para
executar consultas de IA usando PydanticAI, com suporte a diferentes schemas
de resposta e modelos de IA.

Classes:
    PydanticAIService: Interface abstrata para o serviço PydanticAI
    PydanticAIServiceImpl: Implementação concreta do serviço PydanticAI

Funcionalidades:
    - Execução de consultas de IA com diferentes modelos
    - Suporte a schemas de resposta customizados
    - Integração opcional com repositório para listagem de modelos
    - Estimativa de uso de tokens
    - Tratamento de erros e retry automático
"""

from abc import ABC, abstractmethod
from time import time
from typing import Optional

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from .repository import PydanticAIRepository
from .schema.api import ConsultaResponseSchema, ModeloDisponivelSchema
from .enum_modules import ModelSchemaEnum

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()


class PydanticAIService(ABC):
    """Interface para o serviço PydanticAI."""

    @abstractmethod
    async def executar_consulta(
        self,
        user_prompt: str,
        model: str = "groq:llama-3.3-70b-versatile",
        system_prompt: str = "Seja preciso e direto nas respostas.",
        retries: int = 2,
        max_tokens: int = 1440,
        temperature: float = 0.1,
        schema_name: str = "default",
        doc: Optional[str] = "",
    ) -> ConsultaResponseSchema:
        """Executa uma consulta usando PydanticAI."""
        raise NotImplementedError

    @abstractmethod
    async def listar_modelos_disponiveis(self) -> list[ModeloDisponivelSchema]:
        """Lista todos os modelos de IA disponíveis."""
        raise NotImplementedError


class PydanticAIServiceImpl(PydanticAIService):
    """Implementação do serviço PydanticAI."""

    def __init__(self, repository: Optional[PydanticAIRepository] = None):
        self.__repository = repository

    def _estimate_tokens(self, prompt: str, response: str) -> int:
        """
        Estima o número de tokens utilizados baseado no prompt e resposta.

        Args:
            prompt: Texto do prompt enviado
            response: Texto da resposta recebida

        Returns:
            int: Número estimado de tokens utilizados
        """
        prompt_tokens = len(prompt.split()) * 1.3  # Estimativa simples
        response_tokens = len(response.split()) * 1.3  # Estimativa simples
        total = prompt_tokens + response_tokens
        return int(total)

    async def executar_consulta(
        self,
        user_prompt: str,
        model: str = ("google-gla:gemini-2.5-flash-preview-05-20"),
        system_prompt: str = "Seja preciso e direto nas respostas.",
        retries: int = 2,
        max_tokens: int = 1440,
        temperature: float = 0.1,
        schema_name: str = "default",
        doc: Optional[str] = "",
    ) -> ConsultaResponseSchema:
        """
        Executa uma consulta usando PydanticAI.

        Args:
            user_prompt: Prompt do usuário
            model: Modelo de IA a ser utilizado
            system_prompt: Prompt do sistema
            retries: Número de tentativas
            max_tokens: Máximo de tokens
            temperature: Criatividade da resposta
            schema_name: Nome do schema de resposta
            doc: Documento adicional para contexto

        Returns:
            ConsultaResponseSchema: Resultado da consulta

        Raises:
            ValueError: Se parâmetros inválidos
            Exception: Para outros erros
        """
        # Validar schema
        try:
            schema_class = ModelSchemaEnum.get_schema_class(schema_name)
        except ValueError as e:
            raise ValueError(f"Schema inválido: {e}")

        # Iniciar cronômetro
        start_time = time()

        try:
            # Executar consulta
            if doc:
                # Criar agente com dependências para documento
                agent = Agent(
                    model=model,
                    deps_type=str,
                    output_type=schema_class,
                    system_prompt=system_prompt,
                    output_retries=retries,
                    model_settings={"temperature": temperature, "max_tokens": max_tokens},
                )

                @agent.system_prompt
                async def adicionar_documento_deps(ctx: RunContext[str]) -> str:
                    return f"Documento a ser analisado: <doc>{ctx.deps}</doc>"

                resultado = await agent.run(user_prompt, deps=doc)
            else:
                # Criar agente sem dependências para consulta simples
                agent = Agent(
                    model=model,
                    output_type=schema_class,
                    system_prompt=system_prompt,
                    output_retries=retries,
                    model_settings={"temperature": temperature, "max_tokens": max_tokens},
                )
                resultado = await agent.run(user_prompt)

            # Calcular tempo de execução
            tempo_execucao = time() - start_time

            # Estimar tokens utilizados
            response_text = str(resultado.output)
            tokens_estimados = self._estimate_tokens(user_prompt, response_text)

            return ConsultaResponseSchema(
                resultado=resultado.output,
                tempo_execucao=tempo_execucao,
                tokens_utilizados=tokens_estimados,
                modelo_utilizado=model,
                schema_utilizado=schema_name,
            )

        except Exception as e:
            raise Exception(f"Erro ao executar consulta: {str(e)}")

    def _create_agent(
        self,
        model: str,
        system_prompt: str,
        retries: int,
        max_tokens: int,
        temperature: float,
        schema_class: type,
        doc: Optional[str] = "",
    ):
        """
        Cria um agente PydanticAI configurado.

        Args:
            model: Modelo de IA
            system_prompt: Prompt do sistema
            retries: Número de tentativas
            max_tokens: Máximo de tokens
            temperature: Criatividade
            schema_class: Classe do schema de resposta
            doc: Documento para contexto

        Returns:
            Agent: Agente configurado
        """
        if doc:
            # Agente com dependências para documento
            agent = Agent(
                model=model,
                deps_type=str,
                output_type=schema_class,
                system_prompt=system_prompt,
                output_retries=retries,
                model_settings={"temperature": temperature, "max_tokens": max_tokens},
            )

            @agent.system_prompt
            async def adicionar_documento_deps(ctx: RunContext[str]) -> str:
                return f"{system_prompt}\n\nDocumento a ser analisado: <doc>{ctx.deps}</doc>"

            return agent
        else:
            # Agente simples sem dependências
            return Agent(
                model=model,
                output_type=schema_class,
                system_prompt=system_prompt,
                output_retries=retries,
                model_settings={"temperature": temperature, "max_tokens": max_tokens},
            )

    async def listar_modelos_disponiveis(self) -> list[ModeloDisponivelSchema]:
        """
        Lista todos os modelos de IA disponíveis.

        Returns:
            list[ModeloDisponivelSchema]: Lista de modelos com informações organizadas
        """
        if self.__repository is None:
            # Retorna lista vazia se não há repository configurado
            return [
                ModeloDisponivelSchema(
                    client_model_id=1,
                    model_name="google-gla:gemini-2.0-flash-lite",
                    client_name="Gemini",
                    client_abrev="google-gla",
                    description="Gemini 2.0 Flash Lite",
                    cost="Variável",
                    order=1,
                )
            ]

        modelos = await self.__repository.listar_modelos_disponiveis()

        return [
            ModeloDisponivelSchema(
                client_model_id=modelo.client_model_id,
                model_name=modelo.model_nm,
                client_name=modelo.client_ia.client_nm,
                client_abrev=modelo.client_ia.client_abrev,
                description=modelo.descricao,
                cost=modelo.custo,
                order=modelo.ordenacao,
            )
            for modelo in modelos
        ]
