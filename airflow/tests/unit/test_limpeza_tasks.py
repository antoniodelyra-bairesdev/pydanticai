"""
Unit tests para as tasks da DAG de limpeza
"""

from unittest.mock import AsyncMock, patch

import pytest

# Constantes para testes
EXPECTED_REMOVED_COUNT = 3
DEFAULT_RETRIES = 2


@pytest.mark.unit
class TestLimpezaTasks:
    def test_task_exists_in_dag(self, dag_bag):
        """Verifica se a task existe na DAG"""
        dag = dag_bag.dags.get("limpeza_leitor_documentos")
        task = dag.get_task("executar_limpeza_leitor_documentos")

        assert task is not None
        assert task.task_id == "executar_limpeza_leitor_documentos"

    @patch("_lib.DependenciasExternasClient.DependenciasExternasClient")
    def test_executar_limpeza_success(self, mock_client_class, dag_bag, mock_airflow_variables):
        """Testa execução bem-sucedida da task de limpeza"""
        # Mock da resposta da API
        expected_response = {
            "success": True,
            "message": "3 arquivo(s) removido(s).",
            "removed_count": EXPECTED_REMOVED_COUNT,
        }

        # Configura o mock do cliente
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = expected_response
        mock_client_class.return_value = mock_client_instance

        # Mock do asyncio.run
        with patch("asyncio.run") as mock_asyncio_run:
            mock_asyncio_run.return_value = expected_response

            # Obtém a DAG e a task
            dag = dag_bag.dags.get("limpeza_leitor_documentos")
            task = dag.get_task("executar_limpeza_leitor_documentos")

            # Executa a task diretamente
            result = task.python_callable()

            # Verifica o resultado
            assert result["success"] is True
            assert result["removed_count"] == EXPECTED_REMOVED_COUNT
            assert result["message"] == "3 arquivo(s) removido(s)."

    @patch("_lib.DependenciasExternasClient.DependenciasExternasClient")
    def test_executar_limpeza_api_failure(
        self, mock_client_class, dag_bag, mock_airflow_variables
    ):
        """Testa comportamento quando API retorna falha"""
        # Mock da resposta de falha da API
        failure_response = {
            "success": False,
            "message": "Erro interno do servidor",
            "removed_count": 0,
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = failure_response
        mock_client_class.return_value = mock_client_instance

        with patch("asyncio.run") as mock_asyncio_run:
            mock_asyncio_run.return_value = failure_response

            dag = dag_bag.dags.get("limpeza_leitor_documentos")
            task = dag.get_task("executar_limpeza_leitor_documentos")

            # Deve lançar exceção quando success=False
            with pytest.raises(Exception, match="Falha na limpeza"):
                task.python_callable()

    @patch("_lib.DependenciasExternasClient.DependenciasExternasClient")
    def test_executar_limpeza_zero_files(self, mock_client_class, dag_bag, mock_airflow_variables):
        """Testa cenário onde nenhum arquivo é removido"""
        zero_files_response = {
            "success": True,
            "message": "0 arquivo(s) removido(s).",
            "removed_count": 0,
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = zero_files_response
        mock_client_class.return_value = mock_client_instance

        with patch("asyncio.run") as mock_asyncio_run:
            mock_asyncio_run.return_value = zero_files_response

            dag = dag_bag.dags.get("limpeza_leitor_documentos")
            task = dag.get_task("executar_limpeza_leitor_documentos")

            result = task.python_callable()

            # Deve funcionar normalmente mesmo com 0 arquivos
            assert result["success"] is True
            assert result["removed_count"] == 0

    @patch("_lib.DependenciasExternasClient.DependenciasExternasClient")
    def test_api_call_parameters(self, mock_client_class, dag_bag, mock_airflow_variables):
        """Verifica se a task executa corretamente"""
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = {"success": True, "removed_count": 1}
        mock_client_class.return_value = mock_client_instance

        with patch("asyncio.run") as mock_asyncio_run:
            mock_asyncio_run.return_value = {"success": True, "removed_count": 1}

            dag = dag_bag.dags.get("limpeza_leitor_documentos")
            task = dag.get_task("executar_limpeza_leitor_documentos")

            result = task.python_callable()

            # Verifica se a task executou e retornou resultado
            assert result["success"] is True
            assert result["removed_count"] == 1

            # Verifica se asyncio.run foi chamado
            mock_asyncio_run.assert_called_once()
