from abc import ABC, abstractmethod
from httpx import Response


class IntegrationApiClient(ABC):
    @abstractmethod
    async def get(
        self,
        endpoint: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        raise NotImplementedError

    @abstractmethod
    async def post(
        self,
        endpoint: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        body: dict[str, str] | None = None,
    ) -> Response:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self: "IntegrationApiClient") -> "IntegrationApiClient":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        raise NotImplementedError

    def _get_endpoint_tratado(self, endpoint_str: str) -> str:
        return endpoint_str.replace("/", "", 1)
