"""
Unit tests para o DependenciasExternasClient
"""

from unittest.mock import AsyncMock, patch

import pytest
from _lib.DependenciasExternasClient import DependenciasExternasClient

# Constantes para testes
DEFAULT_TIMEOUT = 120
CUSTOM_TIMEOUT = 60


@pytest.mark.unit
class TestDependenciasExternasClient:
    @pytest.fixture
    def client(self, mock_airflow_variables):
        """Fixture para criar cliente com variables mockadas"""
        return DependenciasExternasClient()

    def test_client_initialization(self, client):
        """Testa se o cliente é inicializado corretamente"""
        assert client.api_base_url == "http://test-api.example.com"
        assert client._DependenciasExternasClient__timeout_in_seconds == DEFAULT_TIMEOUT

    def test_client_custom_timeout(self, mock_airflow_variables):
        """Testa inicialização com timeout customizado"""
        client = DependenciasExternasClient(timeout_in_seconds=CUSTOM_TIMEOUT)
        assert client._DependenciasExternasClient__timeout_in_seconds == CUSTOM_TIMEOUT

    @pytest.mark.asyncio
    async def test_post_success(self, client, mock_httpx_response):
        """Testa POST request bem-sucedido"""
        expected_response = {
            "success": True,
            "message": "2 arquivo(s) removido(s).",
            "removed_count": 2,
        }

        mock_response = mock_httpx_response(expected_response, 200)

        with patch("httpx.AsyncClient") as mock_client:
            mock_context = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_context
            mock_context.post.return_value = mock_response

            result = await client.post("/leitor-documentos/limpeza", {"max_age_hours": "24"})

            assert result == expected_response
            mock_context.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_with_query_params(self, client):
        """Testa POST com parâmetros de query"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_context = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_context
            mock_context.post.return_value.json.return_value = {"success": True}
            mock_context.post.return_value.raise_for_status.return_value = None

            await client.post("/test-endpoint", {"param1": "value1", "param2": "value2"})

            # Verifica se os parâmetros foram passados corretamente
            call_args = mock_context.post.call_args
            assert call_args[1]["params"] == {"param1": "value1", "param2": "value2"}

    @pytest.mark.asyncio
    async def test_post_with_custom_headers(self, client):
        """Testa POST com headers customizados"""
        custom_headers = {"Content-Type": "application/json", "X-Custom": "test"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_context = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_context
            mock_context.post.return_value.json.return_value = {"success": True}
            mock_context.post.return_value.raise_for_status.return_value = None

            await client.post("/test", headers=custom_headers)

            # Verifica se os headers foram passados
            call_args = mock_context.post.call_args
            assert call_args[1]["headers"] == custom_headers
