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


class TestAPIValidation:
    """Testes de integração para validação e tratamento de erros da API"""

    def test_extrair_markdown_sem_arquivo(self):
        """Testa endpoint de extração markdown sem enviar arquivo"""
        response = client.post("/leitor-documentos/extrair-markdown")
        assert response.status_code == 422

    def test_extrair_dados_brutos_sem_arquivo(self):
        """Testa endpoint de extração de dados brutos sem enviar arquivo"""
        response = client.post("/leitor-documentos/extrair-dados-brutos")
        assert response.status_code == 422

    def test_extrair_imagens_sem_arquivo(self):
        """Testa endpoint de extração de imagens sem enviar arquivo"""
        response = client.post("/leitor-documentos/extrair-dados-imagens")
        assert response.status_code == 422

    def test_extrair_arquivo_extensao_invalida(self):
        """Testa upload de arquivo com extensão não suportada"""
        files = {"file": ("documento.txt", b"conteudo texto", "text/plain")}
        response = client.post("/leitor-documentos/extrair-markdown", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["success"] is False
        assert "error" in data["detail"]
        assert "error_code" in data["detail"]
        assert data["detail"]["error_code"] == "FILE_VALIDATION_ERROR"

    def test_extrair_arquivo_muito_grande(self):
        """Testa upload de arquivo muito grande"""
        # Criar arquivo simulado muito grande (51MB)
        large_content = b"x" * (51 * 1024 * 1024)
        files = {"file": ("documento_grande.pdf", large_content, "application/pdf")}
        response = client.post("/leitor-documentos/extrair-markdown", files=files)
        
        assert response.status_code == 413
        data = response.json()
        assert data["detail"]["success"] is False
        assert data["detail"]["error_code"] == "FILE_SIZE_ERROR"

    def test_extrair_com_ferramenta_inexistente(self):
        """Testa extração com ferramenta inexistente"""
        # Usar um arquivo PDF válido para testar a validação da ferramenta
        files = {"file": ("exemplo.pdf", b"conteudo pdf", "application/pdf")}
        params = {"ferramenta_extracao": "ferramenta_inexistente"}
        response = client.post("/leitor-documentos/extrair-markdown", files=files, params=params)
        
        assert response.status_code == 422

    def test_extrair_arquivo_vazio(self):
        """Testa tratamento de arquivo vazio"""
        files = {"file": ("vazio.pdf", b"", "application/pdf")}
        response = client.post("/leitor-documentos/extrair-markdown", files=files)
        
        # Pode dar erro de validação ou de extração dependendo da implementação
        assert response.status_code in [400, 500]
        data = response.json()
        assert data["detail"]["success"] is False

    def test_extrair_arquivo_malformado(self):
        """Testa tratamento de arquivo malformado"""
        # Arquivo com extensão PDF mas conteúdo inválido
        files = {"file": ("malformado.pdf", b"este nao e um pdf valido", "application/pdf")}
        response = client.post("/leitor-documentos/extrair-markdown", files=files)
        
        # Deve dar erro de extração
        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["success"] is False
        assert data["detail"]["error_code"] == "EXTRACTION_ERROR"

    def test_error_response_structure(self):
        """Testa estrutura consistente das respostas de erro"""
        # Teste com arquivo inválido
        files = {"file": ("arquivo.txt", b"conteudo", "text/plain")}
        response = client.post("/leitor-documentos/extrair-markdown", files=files)
        
        assert response.status_code == 400
        data = response.json()
        
        # Verificar estrutura do erro
        assert "success" in data["detail"]
        assert "error" in data["detail"]
        assert "error_code" in data["detail"]
        assert data["detail"]["success"] is False
        assert isinstance(data["detail"]["error"], str)
        assert isinstance(data["detail"]["error_code"], str)

    def test_limpeza_endpoint_invalid_hours_too_low(self):
        """Testa endpoint de limpeza com valor muito baixo"""
        response = client.post("/leitor-documentos/limpeza?max_age_hours=0")
        
        assert response.status_code == 422

    def test_limpeza_endpoint_invalid_hours_too_high(self):
        """Testa endpoint de limpeza com valor muito alto"""
        response = client.post("/leitor-documentos/limpeza?max_age_hours=200")
        
        assert response.status_code == 422

    def test_unicode_filename_handling(self):
        """Testa tratamento de nomes de arquivo com caracteres especiais"""
        files = {"file": ("documento_çom_açentos_中文.pdf", b"conteudo", "application/pdf")}
        response = client.post("/leitor-documentos/extrair-markdown", files=files)
        
        # Deve aceitar nomes Unicode (pode dar erro de extração, mas não de validação)
        assert response.status_code in [200, 500]
        data = response.json()
        
        if response.status_code == 200:
            # Se funcionou, verificar que o nome está nos metadados
            assert "documento_çom_açentos_中文.pdf" in data["metadata"]["filename"]
        else:
            # Se deu erro, deve ser erro de extração, não de validação
            assert data["detail"]["error_code"] == "EXTRACTION_ERROR"

    def test_method_not_allowed(self):
        """Testa que métodos não permitidos retornam erro"""
        # GET não deve ser permitido nos endpoints de extração
        response = client.get("/leitor-documentos/extrair-markdown")
        assert response.status_code == 405  # Method Not Allowed
