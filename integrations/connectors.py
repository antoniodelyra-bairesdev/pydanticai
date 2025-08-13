from abc import ABC, abstractmethod
from datetime import date

from fastapi import UploadFile
from modules.indices.model import IndiceCollection
from modules.indices.repository import IndicesRepository
from modules.integrations.enums import FerramentaExtracaoEnum, FontesDadosEnum, TipoExtracaoEnum
from modules.moedas.model import Moeda
from modules.rotinas.indices.coleta.schema import ColetaIndiceCotacaoSchema


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


class DocumentConnector(ABC):
    @abstractmethod
    async def extract_document_content(
        self,
        arquivo: UploadFile,
        ferramenta_extracao: FerramentaExtracaoEnum,
        tipo_extracao: TipoExtracaoEnum,
    ) -> str:
        """
        Extrai conteúdo de um documento usando a ferramenta e tipo especificados.

        Args:
            arquivo: Arquivo enviado via upload
            ferramenta_extracao: Ferramenta a ser usada para extração
            tipo_extracao: Tipo de extração desejado

        Returns:
            str: Conteúdo extraído do documento

        Raises:
            ValueError: Se combinação de ferramenta e tipo não for suportada
            Exception: Para outros erros de processamento
        """
        raise NotImplementedError
