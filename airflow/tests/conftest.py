"""
Configuração do pytest para testes do Airflow.
Este arquivo contém fixtures e configurações compartilhadas entre todos os testes.
"""

import os
import sys
import tempfile
from unittest.mock import patch

import pytest

from airflow import settings
from airflow.models import DagBag
from airflow.utils.db import initdb

# Adiciona o diretório de plugins ao Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plugins"))

# Configuração do Airflow para testes
os.environ.setdefault("AIRFLOW__CORE__UNIT_TEST_MODE", "True")
os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")
os.environ.setdefault("AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS", "False")

# Usa banco em memória para testes
temp_db = tempfile.NamedTemporaryFile(delete=False)
os.environ.setdefault("AIRFLOW__DATABASE__SQL_ALCHEMY_CONN", f"sqlite:///{temp_db.name}")


@pytest.fixture(scope="session", autouse=True)
def setup_airflow_db():
    """Inicializa banco de dados do Airflow para testes"""
    # Força reconfiguração
    settings.configure_orm()
    # Inicializa banco de dados
    initdb()
    yield
    # Cleanup após os testes
    temp_db.close()
    try:
        os.unlink(temp_db.name)
    except:
        pass


@pytest.fixture(scope="session")
def dag_bag():
    """Carrega todas as DAGs para testes"""
    dag_folder = os.path.join(os.path.dirname(__file__), "..", "dags")
    return DagBag(dag_folder=dag_folder, include_examples=False)


@pytest.fixture
def mock_airflow_variables():
    """Mock das Airflow Variables para testes"""
    variables = {
        "dependencias_externas_base_url": "http://test-api.example.com",
        "api_vang_base_url": "http://test-vang-api.example.com",
        "api_vang_x_api_key": "test-api-key-123",
    }

    with patch("airflow.models.Variable.get") as mock_var:
        mock_var.side_effect = lambda key, default_var=None: variables.get(key, default_var)
        yield mock_var


@pytest.fixture
def mock_httpx_response():
    """Fixture para criar responses HTTP mockados"""

    def _create_response(json_data, status_code=200):
        response_mock = type("MockResponse", (), {})()
        response_mock.json = lambda: json_data
        response_mock.status_code = status_code
        response_mock.raise_for_status = (
            lambda: None
            if status_code < 400
            else (_ for _ in ()).throw(Exception(f"HTTP {status_code}"))
        )
        return response_mock

    return _create_response
