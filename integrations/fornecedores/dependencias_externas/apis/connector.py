from fastapi import UploadFile
from httpx import Response
from modules.integrations.api.client import IntegrationApiClient
from modules.integrations.api.client_factory import IntegrationApiClientFactory
from modules.integrations.connectors import DocumentConnector
from modules.integrations.enums import FerramentaExtracaoEnum, FontesDadosEnum, TipoExtracaoEnum


class LeitorDocumentosApiConnector(DocumentConnector):
    __client: IntegrationApiClient

    def __init__(self):
        self.__client = IntegrationApiClientFactory.create(
            fonte_dados=FontesDadosEnum.DEPENDENCIAS_EXTERNAS
        )

    async def extract_document_content(
        self,
        arquivo: UploadFile,
        ferramenta_extracao: FerramentaExtracaoEnum,
        tipo_extracao: TipoExtracaoEnum,
    ) -> str:
        """
        Extrai conteúdo de um documento usando a API do Leitor de Documentos.

        Args:
            arquivo: Arquivo enviado via upload
            ferramenta_extracao: Ferramenta a ser usada para extração
            tipo_extracao: Tipo de extração desejado

        Returns:
            str: Conteúdo extraído do documento

        Raises:
            ValueError: Se combinação não for suportada
            Exception: Para outros erros de processamento
        """
        # Determinar endpoint e parâmetros baseado no tipo de extração
        endpoint, params = self._get_endpoint_and_params(ferramenta_extracao, tipo_extracao)

        async with self.__client as client:
            response: Response = await client.post_with_file(
                endpoint=endpoint,
                arquivo=arquivo,
                params=params,
            )
            response.raise_for_status()

        # Processar resposta
        return self._process_response(response)

    def _get_endpoint_and_params(
        self, ferramenta: FerramentaExtracaoEnum, tipo: TipoExtracaoEnum
    ) -> tuple[str, dict[str, str] | None]:
        """
        Determina endpoint e parâmetros baseado no tipo de extração.

        Args:
            ferramenta: Ferramenta de extração
            tipo: Tipo de extração

        Returns:
            tuple: (endpoint, params)
        """
        if tipo == TipoExtracaoEnum.MARKDOWN:
            # Parâmetro ferramenta_extracao é opcional para markdown
            params = {"ferramenta_extracao": ferramenta.value} if ferramenta else None
            return "/leitor-documentos/extrair-markdown", params

        elif tipo == TipoExtracaoEnum.DADOS_BRUTOS:
            # Parâmetro ferramenta_extracao é opcional para dados brutos
            params = {"ferramenta_extracao": ferramenta.value} if ferramenta else None
            return "/leitor-documentos/extrair-dados-brutos", params

        elif tipo == TipoExtracaoEnum.IMAGENS:
            # Parâmetro ferramenta_extracao é opcional para imagens
            params = {"ferramenta_extracao": ferramenta.value} if ferramenta else None
            return "/leitor-documentos/extrair-dados-imagens", params

        else:
            raise ValueError(f"Tipo de extração '{tipo.value}' não suportado")

    def _process_response(self, response: Response) -> str:
        """
        Processa a resposta da API e extrai o conteúdo.

        Args:
            response: Resposta da requisição HTTP

        Returns:
            str: Conteúdo extraído

        Raises:
            ValueError: Se estrutura da resposta for inválida
        """
        response_data = response.json()

        # Verificar se a resposta tem a estrutura esperada
        if not isinstance(response_data, dict):
            raise ValueError("Resposta não é um objeto JSON válido")

        # Verificar se tem o campo 'data'
        if "data" not in response_data:
            raise ValueError("Resposta não contém campo 'data'")

        # Verificar se tem o campo 'content' dentro de 'data'
        if "content" not in response_data["data"]:
            raise ValueError("Resposta não contém campo 'data.content'")

        # Retornar o conteúdo extraído
        return str(response_data["data"]["content"])
