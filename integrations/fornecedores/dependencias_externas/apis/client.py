from os import getenv

from fastapi import UploadFile
from httpx import AsyncClient, Response
from modules.exceptions import EnvVariableMissingException
from modules.integrations.api.client import IntegrationApiClient
from modules.integrations.api.exceptions import IntegrationApiClientNotOpenException


class LeitorDocumentosApiClient(IntegrationApiClient):
    __client: AsyncClient | None
    __base_url: str
    _timeout_in_seconds: int

    def __init__(self, timeout_in_seconds: int = 120):
        self.__client = None
        self._timeout_in_seconds = timeout_in_seconds

        env_base_url: str | None = getenv("DEPENDENCIAS_EXTERNAS_API_BASE_URL")
        if env_base_url is None:
            raise EnvVariableMissingException(env_variable_name="DEPENDENCIAS_EXTERNAS_API_BASE_URL")

        self.__base_url = env_base_url

    async def post_with_file(
        self,
        endpoint: str,
        arquivo: UploadFile,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        """
        Envia arquivo via POST para o endpoint especificado.

        Args:
            endpoint: Endpoint da API
            arquivo: Arquivo a ser enviado
            params: Parâmetros de query string
            headers: Headers HTTP

        Returns:
            Response: Resposta da requisição

        Raises:
            ValueError: Se arquivo for inválido
            IntegrationApiClientNotOpenException: Se client não estiver aberto
            Exception: Para outros erros de requisição
        """
        # Validações
        if not arquivo.filename:
            raise ValueError("Arquivo deve ter um nome")

        if self.__client is None or self.__client.is_closed:
            raise IntegrationApiClientNotOpenException(api_name="LeitorDocumentosAPI")

        try:
            # Preparar arquivo para upload
            file_content = await arquivo.read()
            files = {"file": (arquivo.filename, file_content, arquivo.content_type)}

            # Headers padrão
            if headers is None:
                headers = {}

            # Não definir Content-Type para multipart/form-data - httpx vai definir automaticamente
            default_headers = {
                "accept": "application/json",
            }
            default_headers.update(headers)

            response: Response = await self.__client.post(
                super()._get_endpoint_tratado(endpoint),
                headers=default_headers,
                params=params,
                files=files,
            )

            # Verificar se a resposta foi bem-sucedida
            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Erro ao enviar arquivo: {str(e)}")

    async def post(
        self,
        endpoint: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        body: dict[str, str] | None = None,
    ) -> Response:
        """Método POST padrão não implementado para este client."""
        raise NotImplementedError("Use post_with_file para envio de arquivos")

    async def get(
        self,
        endpoint: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        """Método GET não implementado para este client."""
        raise NotImplementedError("Este client é específico para upload de arquivos")

    async def close(self) -> None:
        if self.__client and not self.__client.is_closed:
            await self.__client.aclose()

    async def __aenter__(self) -> "LeitorDocumentosApiClient":
        if self.__client is None or self.__client.is_closed:
            self.__client = AsyncClient(base_url=self.__base_url, timeout=self._timeout_in_seconds)

        return self

    async def __aexit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> bool:
        await self.close()
        return False
