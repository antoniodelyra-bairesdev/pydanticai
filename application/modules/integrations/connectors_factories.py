from .connectors import IntegrationsIndicesConnector
from modules.integrations.enums import FontesDadosEnum
from modules.integrations.fornecedores.comdinheiro.apis.connector import (
    ComDinheiroApiConnector,
)


class IntegrationsIndicesConnectorFactory:
    def create(self, fonte_dados: FontesDadosEnum) -> IntegrationsIndicesConnector:
        if fonte_dados == FontesDadosEnum.COMDINHEIRO_API:
            return ComDinheiroApiConnector()

        raise ValueError(
            f'ConnectorFactory: Tipo de connector "{fonte_dados}" não suportado.'
        )
