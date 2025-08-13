from modules.integrations.enums import FontesDadosEnum
from modules.integrations.fornecedores.comdinheiro.apis.connector import ComDinheiroApiConnector
from modules.integrations.fornecedores.dependencias_externas.apis.connector import (
    LeitorDocumentosApiConnector,
)

from .connectors import DocumentConnector, IntegrationsIndicesConnector


class IntegrationsIndicesConnectorFactory:
    def create(self, fonte_dados: FontesDadosEnum) -> IntegrationsIndicesConnector:
        if fonte_dados == FontesDadosEnum.COMDINHEIRO_API:
            return ComDinheiroApiConnector()

        raise ValueError(f'ConnectorFactory: Tipo de connector "{fonte_dados}" não suportado.')


class DocumentConnectorFactory:
    def create(self, fonte_dados: FontesDadosEnum) -> DocumentConnector:
        """
        Cria um connector de documentos baseado na ferramenta de extração.

        Args:
            fonte_dados: Fonte de dados a ser usada para extração

        Returns:
            DocumentConnector: Connector apropriado para a ferramenta

        Raises:
            ValueError: Se ferramenta não for suportada
        """
        if fonte_dados == FontesDadosEnum.DEPENDENCIAS_EXTERNAS:
            return LeitorDocumentosApiConnector()

        raise ValueError(f'ConnectorFactory: Tipo de connector "{fonte_dados}" não suportado.')
