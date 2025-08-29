"""
Módulo de serviço para integração com PydanticAI.

Este módulo fornece uma interface abstrata e implementação concreta para
executar consultas de IA usando PydanticAI, com suporte a diferentes schemas
de resposta e modelos de IA, incluindo fallback entre modelos.

Classes:
    ModelFactory: Factory para criação de instâncias de modelos de IA
    PydanticAIService: Interface abstrata para o serviço PydanticAI
    PydanticAIServiceImpl: Implementação concreta do serviço PydanticAI

Funcionalidades:
    - Execução de consultas de IA com diferentes modelos
    - Suporte a fallback entre múltiplos modelos
    - Suporte a schemas de resposta customizados
    - Integração opcional com repositório para listagem de modelos
    - Estimativa de uso de tokens
    - Tratamento de erros e retry automático
    - Processamento de documentos via API externa
    - Cadastro de prompts com resolução automática de IDs
"""

from abc import ABC, abstractmethod
from datetime import datetime
from time import time

from dotenv import load_dotenv
from fastapi import UploadFile
from modules.integrations.connectors_factories import DocumentConnectorFactory
from modules.integrations.enums import FerramentaExtracaoEnum, FontesDadosEnum, TipoExtracaoEnum
from modules.util.string import format_duration
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.models.openai import OpenAIModel

from .enum_modules import ModelSchemaEnum
from .repository import PydanticAIRepository
from .schema import (
    ConsultaResponseSchema,
    ModeloDisponivelSchema,
    PromptCadastroSchema,
    PromptResponseSchema,
    PromptStatusResponseSchema,
)

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()


class ModelFactory:
    """
    Factory para criação de instâncias de modelos de IA.

    Centraliza a lógica de criação e configuração de modelos,
    seguindo o padrão Factory Method para melhor separação de responsabilidades.
    """

    # Registro de modelos suportados com aliases
    MODEL_REGISTRY = {
        "openai": OpenAIModel,
        "gpt": OpenAIModel,  # alias
        "anthropic": AnthropicModel,
        "claude": AnthropicModel,  # alias
        "groq": GroqModel,
        "google": GoogleModel,
        "google-gla": GoogleModel,  # compatibilidade com banco
        "gemini": GoogleModel,  # alias
    }

    @classmethod
    def criar_modelo(cls, nome_completo: str):
        """
        Cria uma instância de modelo de IA.

        Args:
            nome_completo: String no formato "provider:model-name"

        Returns:
            Instância configurada do modelo apropriado

        Raises:
            ValueError: Se o formato ou provider não for suportado
        """
        if ":" not in nome_completo:
            raise ValueError(
                f"Formato inválido: '{nome_completo}'. "
                f"Use 'provider:model-name' (ex: 'openai:gpt-4o')"
            )

        provider, model_name = nome_completo.split(":", 1)
        provider_lower = provider.lower()

        model_class = cls.MODEL_REGISTRY.get(provider_lower)
        if not model_class:
            providers_disponiveis = list(cls.MODEL_REGISTRY.keys())
            raise ValueError(
                f"Provider '{provider}' não suportado. Disponíveis: {providers_disponiveis}"
            )

        return model_class(model_name)

    @classmethod
    def criar_fallback(cls, modelos: list[str]):
        """
        Cria um modelo com fallback para múltiplos providers.

        Args:
            modelos: Lista de strings no formato "provider:model-name"

        Returns:
            FallbackModel configurado com os modelos especificados

        Raises:
            ValueError: Se a lista estiver vazia ou houver erro na criação
        """
        if not modelos:
            raise ValueError("Lista de modelos não pode estar vazia")

        instancias = []
        for nome_modelo in modelos:
            try:
                modelo = cls.criar_modelo(nome_modelo)
                instancias.append(modelo)
            except Exception as e:
                raise ValueError(f"Erro ao criar modelo '{nome_modelo}': {e}")

        return FallbackModel(*instancias)

    @classmethod
    def get_providers_disponiveis(cls) -> list[str]:
        """
        Retorna lista de providers disponíveis.

        Returns:
            Lista com os nomes dos providers suportados
        """
        return list(cls.MODEL_REGISTRY.keys())


class PydanticAIService(ABC):
    """Interface para o serviço PydanticAI."""

    @abstractmethod
    async def executar_consulta(
        self,
        user_prompt: str,
        model: str | list[str] = "groq:llama-3.3-70b-versatile",
        system_prompt: str = "Seja preciso e direto nas respostas.",
        retries: int = 2,
        max_tokens: int = 2400,
        temperature: float = 0.1,
        schema_name: str = "default",
        doc: str | None = None,
    ) -> ConsultaResponseSchema:
        """Executa uma consulta usando PydanticAI com suporte a fallback."""
        raise NotImplementedError

    @abstractmethod
    async def executar_consulta_com_arquivo(
        self,
        user_prompt: str,
        arquivo: UploadFile,
        ferramenta_extracao: FerramentaExtracaoEnum | None,
        tipo_extracao: TipoExtracaoEnum,
        model: str | list[str] = "groq:llama-3.3-70b-versatile",
        system_prompt: str = "Seja preciso e direto nas respostas.",
        retries: int = 2,
        max_tokens: int = 2400,
        temperature: float = 0.1,
        schema_name: str = "default",
    ) -> ConsultaResponseSchema:
        """Executa uma consulta com arquivo usando PydanticAI."""
        raise NotImplementedError

    @abstractmethod
    async def listar_modelos_disponiveis(self) -> list[ModeloDisponivelSchema]:
        """Lista todos os modelos de IA disponíveis."""
        raise NotImplementedError

    @abstractmethod
    async def cadastrar_prompt(self, dados: PromptCadastroSchema) -> PromptResponseSchema:
        """Cadastra um novo prompt no sistema."""
        raise NotImplementedError

    @abstractmethod
    async def atualizar_status_prompt(self, prompt_id: int, status: str) -> PromptStatusResponseSchema:
        """Atualiza o status (ativo/inativo) de um prompt existente."""
        raise NotImplementedError


class PydanticAIServiceImpl(PydanticAIService):
    """
    Implementação do serviço PydanticAI com suporte a fallback.

    Esta implementação utiliza a ModelFactory para criação de modelos,
    seguindo o princípio de responsabilidade única (SRP).
    """

    def __init__(self, repository: PydanticAIRepository | None = None):
        """
        Inicializa o serviço PydanticAI.

        Args:
            repository: Repositório opcional para operações com banco de dados
        """
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

    def _extrair_modelo_utilizado(self, resultado) -> str:
        """
        Extrai o nome do modelo que foi efetivamente utilizado.

        Args:
            resultado: Resultado do agent.run()

        Returns:
            Nome do modelo utilizado ou "modelo não identificado"
        """
        try:
            # Tentar extrair o model_name da resposta
            if hasattr(resultado, "all_messages"):
                messages = resultado.all_messages()
                for msg in reversed(messages):
                    if hasattr(msg, "model_name") and msg.model_name:
                        return msg.model_name

            return "modelo não identificado"
        except Exception:
            return "modelo não identificado"

    async def executar_consulta(
        self,
        user_prompt: str,
        model: str | list[str] = "groq:llama-3.3-70b-versatile",
        system_prompt: str = "Seja preciso e direto nas respostas.",
        retries: int = 2,
        max_tokens: int = 2400,
        temperature: float = 0.1,
        schema_name: str = "default",
        doc: str | None = None,
    ) -> ConsultaResponseSchema:
        """
        Executa uma consulta usando PydanticAI com suporte a fallback de modelos.

        O parâmetro `model` pode ser:
        - String: "prefixo:nome_modelo" (ex: "openai:gpt-4o")
        - Lista de strings para fallback: ["groq:llama-3.3-70b", "openai:gpt-4o"]

        Args:
            user_prompt: Prompt do usuário
            model: String ou lista de strings com modelos
            system_prompt: Prompt do sistema
            retries: Número de tentativas para output
            max_tokens: Máximo de tokens
            temperature: Temperatura (criatividade)
            schema_name: Nome do schema de resposta
            doc: Documento adicional para contexto

        Returns:
            ConsultaResponseSchema: Resultado da consulta

        Raises:
            ValueError: Se parâmetros inválidos ou schema não encontrado
        """
        # Validar e obter schema
        try:
            schema_class = ModelSchemaEnum.get_schema_class(schema_name)
        except ValueError as e:
            raise ValueError(f"Schema inválido: {e}")

        # Iniciar cronômetro
        start_time = time()

        # Criar modelo ou fallback usando a Factory
        try:
            if isinstance(model, list):
                modelo_principal = ModelFactory.criar_fallback(model)
            else:
                modelo_principal = ModelFactory.criar_modelo(model)

        except Exception as e:
            raise ValueError(f"Erro ao configurar modelo(s): {e}")

        # Criar agent com ou sem documento
        if doc:
            # Agent com dependências para documento
            agent = Agent(
                model=modelo_principal,
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
            # Agent sem dependências
            agent = Agent(
                model=modelo_principal,
                output_type=schema_class,
                system_prompt=system_prompt,
                output_retries=retries,
                model_settings={"temperature": temperature, "max_tokens": max_tokens},
            )
            resultado = await agent.run(user_prompt)

        # Calcular métricas
        tempo_execucao = time() - start_time
        modelo_utilizado = self._extrair_modelo_utilizado(resultado)
        response_text = str(resultado.output)
        tokens_estimados = self._estimate_tokens(user_prompt, response_text)

        return ConsultaResponseSchema(
            resultado=resultado.output,
            tempo_execucao=format_duration(tempo_execucao),
            tokens_utilizados=tokens_estimados,
            modelo_utilizado=modelo_utilizado,
            schema_utilizado=schema_name,
        )

    async def executar_consulta_com_arquivo(
        self,
        user_prompt: str,
        arquivo: UploadFile,
        ferramenta_extracao: FerramentaExtracaoEnum | None,
        tipo_extracao: TipoExtracaoEnum,
        model: str | list[str] = "groq:llama-3.3-70b-versatile",
        system_prompt: str = "Seja preciso e direto nas respostas.",
        retries: int = 2,
        max_tokens: int = 2400,
        temperature: float = 0.1,
        schema_name: str = "default",
    ) -> ConsultaResponseSchema:
        """
        Executa uma consulta com arquivo usando PydanticAI.

        Processa o arquivo usando a ferramenta de extração especificada
        e executa a consulta com o conteúdo extraído como contexto.

        Args:
            user_prompt: Prompt do usuário
            arquivo: Arquivo a ser processado
            ferramenta_extracao: Ferramenta para extração (None usa DOCLING)
            tipo_extracao: Tipo de extração
            model: String ou lista de strings com modelos (suporta fallback)
            system_prompt: Prompt do sistema
            retries: Número de tentativas
            max_tokens: Máximo de tokens
            temperature: Criatividade da resposta
            schema_name: Nome do schema de resposta

        Returns:
            ConsultaResponseSchema: Resultado da consulta
        """
        # Default para DOCLING se não especificado
        if ferramenta_extracao is None:
            ferramenta_extracao = FerramentaExtracaoEnum.DOCLING

        # Criar connector e extrair conteúdo
        factory = DocumentConnectorFactory()
        connector = factory.create(FontesDadosEnum.DEPENDENCIAS_EXTERNAS)

        conteudo_extraido = await connector.extract_document_content(
            arquivo=arquivo,
            ferramenta_extracao=ferramenta_extracao,
            tipo_extracao=tipo_extracao,
        )

        # Executar consulta com o conteúdo extraído
        return await self.executar_consulta(
            user_prompt=user_prompt,
            model=model,
            system_prompt=system_prompt,
            retries=retries,
            max_tokens=max_tokens,
            temperature=temperature,
            schema_name=schema_name,
            doc=conteudo_extraido,
        )

    async def listar_modelos_disponiveis(self) -> list[ModeloDisponivelSchema]:
        """
        Lista todos os modelos de IA disponíveis no banco de dados.

        Returns:
            Lista de modelos com informações detalhadas
        """
        if self.__repository is None:
            # Retorna exemplo se não há repository
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

    async def cadastrar_prompt(self, dados: PromptCadastroSchema) -> PromptResponseSchema:
        """
        Cadastra um novo prompt no sistema.

        Args:
            dados: Dados do prompt a ser cadastrado

        Returns:
            PromptResponseSchema: Dados do prompt cadastrado

        Raises:
            ValueError: Se dados inválidos (cliente, modelo, mesa não encontrados)
        """
        try:
            # 1. Resolver IDs via cache
            client_model_id = await self.__repository.buscar_client_model_por_nomes(
                dados.client_name, dados.model_name
            )

            mesa_id = await self.__repository.buscar_mesa_por_nome(dados.mesa_nome)

            model_schema_id = await self.__repository.buscar_model_schema_por_nome(
                dados.model_schema_name
            )

            # 2. Verificar se combinação já existe
            prompt_existente = await self.__repository.buscar_prompt_ativo_existente(
                client_model_id=client_model_id,
                codigo_ativo=dados.codigo_ativo,
                is_image=dados.is_image,
            )

            # 3. Se existe, desativar o anterior
            if prompt_existente:
                await self.__repository.atualizar_status_prompt(prompt_existente.prompt_id, False)

            # 4. Criar novo prompt
            dados_prompt = {
                "client_model_id": client_model_id,
                "mesa_id": mesa_id,
                "codigo_ativo": dados.codigo_ativo,
                "model_schema_id": model_schema_id,
                "temperatura": dados.temperatura,
                "max_tokens": dados.max_tokens,
                "prompt_sistema": dados.prompt_sistema,
                "prompt_usuario": dados.prompt_usuario,
                "is_image": dados.is_image,
                "ativo": True,
                "descricao": dados.descricao,
            }

            novo_prompt = await self.__repository.criar_prompt(dados_prompt)

            # 5. Buscar prompt completo para response
            prompt_completo = await self.__repository.buscar_prompt_completo_por_id(
                novo_prompt.prompt_id
            )

            if not prompt_completo:
                raise ValueError("Erro ao recuperar prompt cadastrado")

            # 6. Montar response usando dados do prompt completo
            return PromptResponseSchema(
                prompt_id=prompt_completo.prompt_id,
                client_name=prompt_completo.client_model.client_ia.client_nm,
                model_name=prompt_completo.client_model.model_nm,
                mesa_nome=dados.mesa_nome,
                codigo_ativo=prompt_completo.codigo_ativo,
                schema_name=dados.model_schema_name,
                temperatura=prompt_completo.temperatura,
                max_tokens=prompt_completo.max_tokens,
                prompt_sistema=prompt_completo.prompt_sistema,
                prompt_usuario=prompt_completo.prompt_usuario,
                is_image=prompt_completo.is_image,
                data_criacao=prompt_completo.data_criacao,
                ativo=prompt_completo.ativo,
                descricao=prompt_completo.descricao,
            )

        except ValueError as e:
            # Re-raise com contexto adicional
            raise ValueError(f"Erro ao cadastrar prompt: {e}")
        except Exception as e:
            # Log do erro e re-raise como ValueError genérico
            raise ValueError(f"Erro interno ao cadastrar prompt: {str(e)}")

    async def atualizar_status_prompt(self, prompt_id: int, status: str) -> PromptStatusResponseSchema:
        """
        Atualiza o status (ativo/inativo) de um prompt existente.

        Args:
            prompt_id: ID do prompt a ser atualizado
            status: Status desejado ("enabled" ou "disabled")

        Returns:
            PromptStatusResponseSchema: Informações sobre a atualização realizada

        Raises:
            ValueError: Se prompt não encontrado ou status inválido
        """
        if self.__repository is None:
            raise ValueError("Repositório não disponível para esta operação")

        # Validar status
        if status not in ["enabled", "disabled"]:
            raise ValueError("Status deve ser 'enabled' ou 'disabled'")

        # Converter status para boolean
        novo_status = status == "enabled"

        # Buscar prompt atual para verificar se existe e obter status anterior
        prompt_atual = await self.__repository.buscar_prompt_por_id(prompt_id)

        if not prompt_atual:
            raise ValueError(f"Prompt com ID {prompt_id} não encontrado")

        # Verificar se já está no status desejado
        status_atual = "enabled" if prompt_atual.ativo else "disabled"
        if status_atual == status:
            raise ValueError(f"Prompt já está com status '{status}'")

        # Atualizar status
        prompt_atualizado = await self.__repository.atualizar_status_prompt(prompt_id, novo_status)

        if not prompt_atualizado:
            raise ValueError(f"Erro ao atualizar status do prompt {prompt_id}")

        # Montar resposta
        return PromptStatusResponseSchema(
            prompt_id=prompt_id,
            status=status,
            message=f"Status do prompt atualizado com sucesso para '{status}'",
            updated_at=datetime.now(),
            previous_status=status_atual
        )
