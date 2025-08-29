"""
Repositório para o módulo PydanticAI.

Este módulo contém a implementação do repositório PydanticAI, responsável por
gerenciar operações de banco de dados relacionadas a prompts, modelos de IA
e schemas de modelo.

Funcionalidades:
- Listagem de modelos de IA disponíveis
- Busca de modelos por nome
- Listagem de schemas de modelo
- Busca de schemas por nome
- Cadastro de prompts com cache de performance
"""

from functools import lru_cache
from typing import Sequence

from modules.repository import BaseRepository
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from .entity import ClientModel, ModelSchema, Prompt


class PydanticAIRepository:
    """Implementação do repositório PydanticAI."""

    def __init__(
        self,
        base_repository_prompt: BaseRepository[Prompt],
        base_repository_client_model: BaseRepository[ClientModel],
        base_repository_model_schema: BaseRepository[ModelSchema],
    ):
        self.__base_repository_prompt = base_repository_prompt
        self.__base_repository_client_model = base_repository_client_model
        self.__base_repository_model_schema = base_repository_model_schema

    async def listar_modelos_disponiveis(self) -> Sequence[ClientModel]:
        """
        Lista todos os modelos de IA disponíveis.

        Returns:
            Sequence[ClientModel]: Lista de modelos disponíveis
        """
        from .entity import ClientIa

        query = (
            select(ClientModel)
            .join(ClientIa, ClientModel.client_id == ClientIa.client_id)
            .order_by(ClientIa.client_nm, ClientModel.ordenacao)
        )

        result = await self.__base_repository_client_model.get_db_session().execute(query)
        return result.unique().scalars().all()

    async def buscar_modelo_por_nome(self, model_name: str) -> ClientModel | None:
        """
        Busca um modelo específico pelo nome.

        Args:
            model_name: Nome do modelo

        Returns:
            ClientModel | None: Modelo encontrado ou None
        """
        query = select(ClientModel).where(ClientModel.model_nm == model_name)

        result = await self.__base_repository_client_model.get_db_session().execute(query)
        return result.unique().scalar_one_or_none()

    async def listar_schemas_modelo(self) -> Sequence[ModelSchema]:
        """
        Lista todos os schemas de modelo disponíveis.

        Returns:
            Sequence[ModelSchema]: Lista de schemas disponíveis
        """
        query = select(ModelSchema).order_by(ModelSchema.model_nm)

        result = await self.__base_repository_model_schema.get_db_session().execute(query)
        return result.unique().scalars().all()

    async def buscar_schema_por_nome(self, schema_name: str) -> ModelSchema | None:
        """
        Busca um schema específico pelo nome.

        Args:
            schema_name: Nome do schema

        Returns:
            ModelSchema | None: Schema encontrado ou None
        """
        query = select(ModelSchema).where(ModelSchema.model_nm == schema_name)

        result = await self.__base_repository_model_schema.get_db_session().execute(query)
        return result.unique().scalar_one_or_none()

    @lru_cache(maxsize=128)
    async def _get_client_models_cache(self) -> dict[tuple[str, str], int]:
        """
        Cache de client models por (client_name, model_name) -> client_model_id.

        Returns:
            dict[tuple[str, str], int]: Mapeamento (client_name, model_name) -> client_model_id
        """
        from .entity import ClientIa

        query = select(ClientModel, ClientIa.client_nm).join(
            ClientIa, ClientModel.client_id == ClientIa.client_id
        )

        result = await self.__base_repository_client_model.get_db_session().execute(query)

        cache_data = {}
        for client_model, client_name in result:
            cache_data[(client_name, client_model.model_nm)] = client_model.client_model_id

        return cache_data

    @lru_cache(maxsize=64)
    async def _get_mesas_cache(self) -> dict[str, int]:
        """
        Cache de mesas por nome -> mesa_id.

        Returns:
            dict[str, int]: Mapeamento nome -> mesa_id
        """
        from modules.mesas.model import Mesa

        query = select(Mesa.id, Mesa.nome).order_by(Mesa.nome)
        result = await self.__base_repository_prompt.get_db_session().execute(query)

        cache_data = {}
        for mesa_id, nome in result:
            cache_data[nome] = mesa_id

        return cache_data

    @lru_cache(maxsize=64)
    async def _get_model_schemas_cache(self) -> dict[str, int]:
        """
        Cache de model schemas por nome -> model_schema_id.

        Returns:
            dict[str, int]: Mapeamento nome -> model_schema_id
        """
        query = select(ModelSchema.model_schema_id, ModelSchema.model_nm)
        result = await self.__base_repository_model_schema.get_db_session().execute(query)

        cache_data = {}
        for model_schema_id, model_nm in result:
            cache_data[model_nm] = model_schema_id

        return cache_data

    async def buscar_client_model_por_nomes(self, client_nm: str, model_nm: str) -> int:
        """
        Busca client_model_id por nomes do cliente e modelo.

        Args:
            client_nm: Nome do cliente (ex: "Open AI")
            model_nm: Nome do modelo (ex: "gpt-4.1-mini")

        Returns:
            int: ID do client model

        Raises:
            ValueError: Se combinação não for encontrada
        """
        cache = await self._get_client_models_cache()

        key = (client_nm, model_nm)
        if key not in cache:
            # Tentar buscar no banco caso o cache esteja desatualizado
            from .entity import ClientIa

            query = (
                select(ClientModel)
                .join(ClientIa, ClientModel.client_id == ClientIa.client_id)
                .where(ClientIa.client_nm == client_nm, ClientModel.model_nm == model_nm)
            )
            result = await self.__base_repository_client_model.get_db_session().execute(query)
            client_model = result.unique().scalar_one_or_none()

            if not client_model:
                raise ValueError(f"Modelo '{model_nm}' do cliente '{client_nm}' não encontrado")

            return client_model.client_model_id

        return cache[key]

    async def buscar_mesa_por_nome(self, mesa_nome: str) -> int:
        """
        Busca mesa_id por nome da mesa.

        Args:
            mesa_nome: Nome da mesa

        Returns:
            int: ID da mesa

        Raises:
            ValueError: Se mesa não for encontrada
        """
        cache = await self._get_mesas_cache()

        if mesa_nome not in cache:
            # Tentar buscar no banco caso o cache esteja desatualizado
            from modules.mesas.model import Mesa
            query = select(Mesa.id).where(Mesa.nome == mesa_nome)
            result = await self.__base_repository_prompt.get_db_session().execute(query)
            mesa_id = result.scalar_one_or_none()

            if not mesa_id:
                raise ValueError(f"Mesa '{mesa_nome}' não encontrada")

            return mesa_id

        return cache[mesa_nome]

    async def buscar_model_schema_por_nome(self, schema_name: str) -> int | None:
        """
        Busca model_schema_id por nome do schema.

        Args:
            schema_name: Nome do schema

        Returns:
            int | None: ID do schema ou None se não encontrado
        """
        cache = await self._get_model_schemas_cache()

        if schema_name not in cache:
            # Tentar buscar no banco caso o cache esteja desatualizado
            query = select(ModelSchema.model_schema_id).where(ModelSchema.model_nm == schema_name)
            result = await self.__base_repository_model_schema.get_db_session().execute(query)
            schema_id = result.scalar_one_or_none()

            return schema_id

        return cache[schema_name]

    async def buscar_prompt_ativo_existente(
        self, client_model_id: int, codigo_ativo: str, is_image: bool
    ) -> Prompt | None:
        """
        Busca prompt ativo existente pela combinação única.

        Args:
            client_model_id: ID do client model
            codigo_ativo: Código do ativo
            is_image: Flag de imagem

        Returns:
            Prompt | None: Prompt encontrado ou None
        """
        query = select(Prompt).where(
            Prompt.client_model_id == client_model_id,
            Prompt.codigo_ativo == codigo_ativo,
            Prompt.is_image == is_image,
            Prompt.ativo == True,  # noqa: E712
        )

        result = await self.__base_repository_prompt.get_db_session().execute(query)
        return result.unique().scalar_one_or_none()

    async def desativar_prompt(self, prompt_id: int) -> None:
        """
        Desativa um prompt existente.

        Args:
            prompt_id: ID do prompt a ser desativado
        """
        query = update(Prompt).where(Prompt.prompt_id == prompt_id).values(ativo=False)

        await self.__base_repository_prompt.get_db_session().execute(query)

    async def criar_prompt(self, dados: dict) -> Prompt:
        """
        Cria um novo prompt no banco de dados.

        Args:
            dados: Dicionário com os dados do prompt

        Returns:
            Prompt: Prompt criado
        """
        novo_prompt = Prompt(**dados)

        session = self.__base_repository_prompt.get_db_session()
        session.add(novo_prompt)
        await session.flush()  # Para obter o ID gerado
        await session.refresh(novo_prompt)

        return novo_prompt

    async def buscar_prompt_completo_por_id(self, prompt_id: int) -> Prompt | None:
        """
        Busca prompt por ID com todos os relacionamentos carregados.

        Args:
            prompt_id: ID do prompt

        Returns:
            Prompt | None: Prompt com relacionamentos ou None
        """

        query = (
            select(Prompt)
            .options(selectinload(Prompt.client_model).selectinload(ClientModel.client_ia))
            .options(selectinload(Prompt.model_schema))
            .where(Prompt.prompt_id == prompt_id)
        )

        result = await self.__base_repository_prompt.get_db_session().execute(query)
        return result.unique().scalar_one_or_none()

    def clear_cache(self) -> None:
        """Limpa todo o cache interno."""
        self._get_client_models_cache.cache_clear()
        self._get_mesas_cache.cache_clear()
        self._get_model_schemas_cache.cache_clear()
