from abc import ABC, abstractmethod
from datetime import date

from modules.indices.model import IndiceCollection
from modules.indices.repository import IndicesRepository
from modules.rotinas.indices.coleta.schema import (
    ColetaIndiceCotacaoSchema,
)
from modules.moedas.model import Moeda
from modules.integrations.enums import FontesDadosEnum


class IntegrationsIndicesConnector(ABC):
    @abstractmethod
    async def fetch_indices_cotacoes_pontos(
        self,
        indices_repository: IndicesRepository | None,
        indices: IndiceCollection,
        data_inicio: date,
        data_fim: date,
        fonte_dado: FontesDadosEnum,
        moeda: Moeda,
    ) -> list[ColetaIndiceCotacaoSchema]:
        raise NotImplementedError
