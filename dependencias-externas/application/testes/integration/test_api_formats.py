import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from main import app

# Cliente de teste do FastAPI
client = TestClient(app)

pytestmark = pytest.mark.integration


class TestAPIFormats:
    """Testes de integração para endpoints de formatos suportados"""

    def test_formatos_suportados_endpoint_pdf(self):
        """Testa endpoint de formatos suportados para PDF"""
        response = client.get("/leitor-documentos/formatos-suportados?extensao=pdf")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "formats" in data
        assert "pdf" in data["formats"]

        pdf_extractors = data["formats"]["pdf"]
        assert len(pdf_extractors) >= 2

        extractor_names = [e["name"] for e in pdf_extractors]
        assert "docling_pdf" in extractor_names
        assert "pypdf" in extractor_names

    def test_formatos_suportados_endpoint_docx(self):
        """Testa endpoint de formatos suportados para DOCX"""
        response = client.get("/leitor-documentos/formatos-suportados?extensao=docx")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "formats" in data
        assert "docx" in data["formats"]

        docx_extractors = data["formats"]["docx"]
        assert len(docx_extractors) >= 2

        extractor_names = [e["name"] for e in docx_extractors]
        assert "docling_docx" in extractor_names
        assert "docx2txt" in extractor_names

    def test_formatos_suportados_extensao_invalida(self):
        """Testa endpoint de formatos suportados com extensão inválida"""
        response = client.get("/leitor-documentos/formatos-suportados?extensao=xyz")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "formats" in data
        # Deve retornar lista vazia para extensão não suportada
        assert len(data["formats"].get("xyz", [])) == 0

    def test_formatos_suportados_estrutura_resposta(self):
        """Testa estrutura da resposta do endpoint de formatos suportados"""
        response = client.get("/leitor-documentos/formatos-suportados?extensao=pdf")
        assert response.status_code == 200

        data = response.json()

        # Verificar estrutura base
        assert "success" in data
        assert "formats" in data
        assert data["success"] is True
        assert isinstance(data["formats"], dict)

        # Verificar estrutura dos extractors
        pdf_extractors = data["formats"]["pdf"]
        for extractor in pdf_extractors:
            assert "name" in extractor
            assert "extensions" in extractor
            assert isinstance(extractor["name"], str)
            assert isinstance(extractor["extensions"], list)
            assert len(extractor["name"]) > 0
            assert len(extractor["extensions"]) > 0

    def test_formatos_suportados_case_insensitive(self):
        """Testa que o endpoint funciona com extensões em diferentes casos"""
        # Testar com extensão em maiúsculas
        response_upper = client.get(
            "/leitor-documentos/formatos-suportados?extensao=PDF"
        )
        assert response_upper.status_code == 200

        # Testar com extensão em minúsculas
        response_lower = client.get(
            "/leitor-documentos/formatos-suportados?extensao=pdf"
        )
        assert response_lower.status_code == 200
