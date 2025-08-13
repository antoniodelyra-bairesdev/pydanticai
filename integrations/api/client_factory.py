from dataclasses import dataclass

from modules.integrations.api.client import IntegrationApiClient
from modules.integrations.enums import FontesDadosEnum
from modules.integrations.fornecedores.comdinheiro.apis.client import ComDinheiroApiClient
from modules.integrations.fornecedores.dependencias_externas.apis.client import (
    LeitorDocumentosApiClient,
)


@dataclass
class IntegrationApiClientFactory:
    @staticmethod
    def create(fonte_dados: FontesDadosEnum) -> IntegrationApiClient:
        if fonte_dados == FontesDadosEnum.COMDINHEIRO_API:
            return ComDinheiroApiClient()

        elif fonte_dados == FontesDadosEnum.DEPENDENCIAS_EXTERNAS:
            return LeitorDocumentosApiClient()

        raise ValueError(
            f'ClientFactory: Tipo de client "{fonte_dados}" não suportado.'
        )
