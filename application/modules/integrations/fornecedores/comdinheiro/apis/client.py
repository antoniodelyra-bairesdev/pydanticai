from os import getenv
from httpx import AsyncClient, Response

from modules.integrations.api.client import (
    IntegrationApiClient,
)
from modules.integrations.api.exceptions import IntegrationApiClientNotOpenException
from modules.exceptions import EnvVariableMissingException


class ComDinheiroApiClient(IntegrationApiClient):
    __client: AsyncClient | None
    __base_url: str
    __username: str
    __password: str
    _timeout_in_seconds: int

    def __init__(self, timeout_in_seconds: int = 60):
        self.__client = None
        self._timeout_in_seconds = timeout_in_seconds

        env_base_url: str | None = getenv("COMDINHEIRO_API_COMDINHEIRO_BASE_URL")
        if env_base_url is None:
            raise EnvVariableMissingException(
                env_variable_name="COMDINHEIRO_API_COMDINHEIRO_BASE_URL"
            )

        env_username: str | None = getenv("COMDINHEIRO_API_COMDINHEIRO_USERNAME")
        if env_username is None:
            raise EnvVariableMissingException(
                env_variable_name="COMDINHEIRO_API_COMDINHEIRO_USERNAME"
            )

        env_password: str | None = getenv("COMDINHEIRO_API_COMDINHEIRO_PASSWORD")
        if env_password is None:
            raise EnvVariableMissingException(
                env_variable_name="COMDINHEIRO_API_COMDINHEIRO_PASSWORD"
            )

        self.__base_url = env_base_url
        self.__username = env_username
        self.__password = env_password

    async def post(
        self,
        endpoint: str,
        params: dict[str, str] | None,
        headers: dict[str, str],
        body: dict[str, str],
    ) -> Response:
        if self.__client is None or self.__client.is_closed:
            raise IntegrationApiClientNotOpenException(api_name="ComDinheiroAPI")

        payload_data = {
            "username": self.__username,
            "password": self.__password,
            **body,
        }

        response: Response = await self.__client.post(
            super()._get_endpoint_tratado(endpoint),
            headers=headers,
            params=params,
            data=payload_data,
        )

        return response

    async def get(
        self,
        endpoint: str,
        params: dict[str, str],
        headers: dict[str, str],
    ) -> Response:
        raise NotImplementedError

    async def close(self) -> None:
        if self.__client and not self.__client.is_closed:
            await self.__client.aclose()

        return None

    async def __aenter__(self) -> IntegrationApiClient:
        if self.__client is None or self.__client.is_closed:
            self.__client = AsyncClient(
                base_url=self.__base_url, timeout=self._timeout_in_seconds
            )

        return self

    async def __aexit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> bool:
        await self.close()

        return False
