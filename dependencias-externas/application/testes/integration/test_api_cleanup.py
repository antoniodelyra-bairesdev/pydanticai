import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from main import app

# Cliente de teste do FastAPI
client = TestClient(app)

pytestmark = pytest.mark.integration


class TestAPICleanup:
    """Testes de integração para endpoints de limpeza da API"""

    def test_limpeza_endpoint_default(self):
        """Testa endpoint de limpeza com parâmetros padrão"""
        response = client.post("/leitor-documentos/limpeza")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "removed_count" in data
        assert isinstance(data["removed_count"], int)
        assert data["removed_count"] >= 0

    def test_limpeza_endpoint_custom_hours(self):
        """Testa endpoint de limpeza com parâmetro personalizado"""
        response = client.post("/leitor-documentos/limpeza?max_age_hours=12")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "removed_count" in data
        assert isinstance(data["removed_count"], int)

    def test_limpeza_endpoint_estrutura_resposta(self):
        """Testa estrutura da resposta do endpoint de limpeza"""
        response = client.post("/leitor-documentos/limpeza")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estrutura base
        assert "success" in data
        assert "message" in data
        assert "removed_count" in data
        assert data["success"] is True
        assert isinstance(data["message"], str)
        assert isinstance(data["removed_count"], int)
        assert data["removed_count"] >= 0

    def test_limpeza_endpoint_multiplas_chamadas(self):
        """Testa múltiplas chamadas ao endpoint de limpeza"""
        # Primeira chamada
        response1 = client.post("/leitor-documentos/limpeza")
        assert response1.status_code == 200
        
        # Segunda chamada (deve funcionar normalmente)
        response2 = client.post("/leitor-documentos/limpeza")
        assert response2.status_code == 200
        
        # Ambas devem retornar sucesso
        data1 = response1.json()
        data2 = response2.json()
        assert data1["success"] is True
        assert data2["success"] is True

    def test_limpeza_endpoint_diferentes_horarios(self):
        """Testa endpoint de limpeza com diferentes valores de horas"""
        # Testar com 1 hora
        response1 = client.post("/leitor-documentos/limpeza?max_age_hours=1")
        assert response1.status_code == 200
        
        # Testar com 24 horas
        response2 = client.post("/leitor-documentos/limpeza?max_age_hours=24")
        assert response2.status_code == 200
        
        # Testar com 168 horas (1 semana)
        response3 = client.post("/leitor-documentos/limpeza?max_age_hours=168")
        assert response3.status_code == 200
        
        # Todas devem retornar sucesso
        for response in [response1, response2, response3]:
            data = response.json()
            assert data["success"] is True
            assert "removed_count" in data 