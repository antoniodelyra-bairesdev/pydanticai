from typing import Any
from urllib.parse import urljoin

import httpx

from airflow.models import Variable


class DependenciasExternasClient:
    """
    Cliente para APIs de dependências externas.

    Cliente simplificado para fazer requests POST sem autenticação.
    Utiliza a URL base configurada na variável 'dependencias_externas_base_url'.
    """

    def __init__(self, timeout_in_seconds: int = 120):
        self.__timeout_in_seconds: int = timeout_in_seconds
        self.api_base_url: str = Variable.get("dependencias_externas_base_url")

    async def post(
        self,
        endpoint: str,
        query_params: dict[str, str] | None = None,
        json_body: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Faz uma requisição POST para o endpoint especificado.

        Args:
            endpoint: Endpoint da API (ex: '/leitor-documentos/limpeza')
            query_params: Parâmetros de query opcionais
            json_body: Corpo da requisição em formato JSON
            headers: Headers adicionais opcionais

        Returns:
            Resposta da API como dicionário

        Raises:
            httpx.HTTPStatusError: Se a requisição falhar
        """
        _headers: dict[str, str] = headers or {}

        if not endpoint:
            raise ValueError("Endpoint não pode ser None ou vazio")
        full_url = urljoin(f"{self.api_base_url}/", endpoint)

        async with httpx.AsyncClient(timeout=self.__timeout_in_seconds) as client:
            response = await client.post(
                full_url, params=query_params, headers=_headers, json=json_body
            )

        response.raise_for_status()
        data = response.json()
        return data
