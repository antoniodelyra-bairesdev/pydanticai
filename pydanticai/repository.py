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
"""

from typing import Sequence, Optional
from sqlalchemy import select

from .model import Prompt, ClientModel, ModelSchema
from modules.repository import BaseRepository


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
        query = select(ClientModel).order_by(ClientModel.ordenacao, ClientModel.model_nm)

        result = await self.__base_repository_client_model.get_db_session().execute(query)
        return result.unique().scalars().all()

    async def buscar_modelo_por_nome(self, model_name: str) -> Optional[ClientModel]:
        """
        Busca um modelo específico pelo nome.

        Args:
            model_name: Nome do modelo

        Returns:
            Optional[ClientModel]: Modelo encontrado ou None
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

    async def buscar_schema_por_nome(self, schema_name: str) -> Optional[ModelSchema]:
        """
        Busca um schema específico pelo nome.

        Args:
            schema_name: Nome do schema

        Returns:
            Optional[ModelSchema]: Schema encontrado ou None
        """
        query = select(ModelSchema).where(ModelSchema.model_nm == schema_name)

        result = await self.__base_repository_model_schema.get_db_session().execute(query)
        return result.unique().scalar_one_or_none()
