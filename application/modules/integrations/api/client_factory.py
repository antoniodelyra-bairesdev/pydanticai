from dataclasses import dataclass

from modules.integrations.enums import FontesDadosEnum
from modules.integrations.api.client import IntegrationApiClient
from modules.integrations.fornecedores.comdinheiro.apis.client import (
    ComDinheiroApiClient,
)


@dataclass
class IntegrationApiClientFactory:
    @staticmethod
    def create(fonte_dados: FontesDadosEnum) -> IntegrationApiClient:
        if fonte_dados == FontesDadosEnum.COMDINHEIRO_API:
            return ComDinheiroApiClient()

        raise ValueError(
            f'ClientFactory: Tipo de client "{fonte_dados}" não suportado.'
        )
