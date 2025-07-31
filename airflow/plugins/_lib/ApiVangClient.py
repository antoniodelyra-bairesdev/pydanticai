from typing import Any

import httpx
from airflow.models import Variable


class ApiVangClient:
    def __init__(self, timeout_in_seconds: int = 120):
        self.__timeout_in_seconds: int = timeout_in_seconds
        self.api_base_url: str = Variable.get("api_vang_base_url")
        self.x_api_key: str = Variable.get("api_vang_x_api_key")

    async def get(
        self,
        endpoint: str,
        query_params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ):
        _headers: dict[str, str] = self.__get_headers(headers)

        url_parts = [self.api_base_url.rstrip("/")]
        url_parts.append(endpoint.lstrip("/"))

        full_url = "/".join(filter(None, url_parts))

        async with httpx.AsyncClient(timeout=self.__timeout_in_seconds) as client:
            response = await client.get(full_url, params=query_params, headers=_headers)

        response.raise_for_status()
        data = response.json()
        return data

    async def post(
        self,
        endpoint: str,
        query_params: dict[str, str] | None = None,
        json_body: Any | None = None,
        headers: dict[str, str] | None = None,
    ):
        _headers: dict[str, str] = self.__get_headers(headers)

        url_parts = [self.api_base_url.rstrip("/")]
        url_parts.append(endpoint.lstrip("/"))

        full_url = "/".join(filter(None, url_parts))

        async with httpx.AsyncClient(timeout=self.__timeout_in_seconds) as client:
            response = await client.post(
                full_url, params=query_params, headers=_headers, json=json_body
            )

        response.raise_for_status()
        data = response.json()
        return data

    def __get_headers(self, headers: dict[str, str] | None = None) -> dict[str, str]:
        default_header: dict[str, str] = {"x-user-token": self.x_api_key}

        if headers is None:
            return default_header

        merged_headers = default_header.copy()
        merged_headers.update(headers)
        return merged_headers
