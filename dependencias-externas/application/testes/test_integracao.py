import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)

# Caminhos para os arquivos de teste
SAMPLE_FILES_DIR = Path(__file__).parent / "sample_files"
PDF_FILE = SAMPLE_FILES_DIR / "exemplo.pdf"
DOCX_FILE = SAMPLE_FILES_DIR / "exemplo.docx"


class TestLeitorDocumentosEndpoints:
    """Testes de integração dos endpoints da API"""

    def test_health_endpoint(self):
        """Testa endpoint de health check"""
        response = client.get("/leitor-documentos/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Leitor de Documentos"

    def test_formatos_suportados_endpoint(self):
        """Testa endpoint de formatos suportados"""
        response = client.get("/leitor-documentos/formatos-suportados")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "formats" in data
        assert "pdf" in data["formats"]
        assert "docx" in data["formats"]

    def test_extrair_markdown_sem_arquivo(self):
        """Testa extração markdown sem arquivo"""
        response = client.post("/leitor-documentos/extrair-markdown")
        assert response.status_code == 422

    def test_extrair_dados_brutos_sem_arquivo(self):
        """Testa extração de dados brutos sem arquivo"""
        response = client.post("/leitor-documentos/extrair-dados-brutos")
        assert response.status_code == 422

    def test_extrair_imagens_sem_arquivo(self):
        """Testa extração de imagens sem arquivo"""
        response = client.post("/leitor-documentos/extrair-dados-imagens")
        assert response.status_code == 422

    def test_extrair_arquivo_invalido(self):
        """Testa extração com tipo de arquivo inválido"""
        files = {"file": ("test.xyz", b"conteudo", "application/octet-stream")}
        response = client.post("/leitor-documentos/extrair-markdown", files=files)
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "error" in data

    def test_extrair_pdf_markdown(self):
        """Testa extração de PDF para markdown"""
        if not PDF_FILE.exists():
            pytest.skip("Arquivo PDF de teste não encontrado")

        with open(PDF_FILE, "rb") as f:
            files = {"file": ("exemplo.pdf", f.read(), "application/pdf")}
            response = client.post("/leitor-documentos/extrair-markdown", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "metadata" in data
        assert data["data"]["format"] == "markdown"
        assert len(data["data"]["content"]) > 0
        assert data["metadata"]["file_size"] is not None
        assert data["metadata"]["extraction_time"] is not None

    def test_extrair_pdf_dados_brutos(self):
        """Testa extração de PDF para dados brutos"""
        if not PDF_FILE.exists():
            pytest.skip("Arquivo PDF de teste não encontrado")

        with open(PDF_FILE, "rb") as f:
            files = {"file": ("exemplo.pdf", f.read(), "application/pdf")}
            response = client.post("/leitor-documentos/extrair-dados-brutos", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "metadata" in data
        assert data["data"]["format"] == "raw"
        assert len(data["data"]["content"]) > 0

    def test_extrair_pdf_imagens(self):
        """Testa extração de imagens do PDF"""
        if not PDF_FILE.exists():
            pytest.skip("Arquivo PDF de teste não encontrado")

        with open(PDF_FILE, "rb") as f:
            files = {"file": ("exemplo.pdf", f.read(), "application/pdf")}
            response = client.post("/leitor-documentos/extrair-dados-imagens", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "metadata" in data
        assert data["data"]["format"] == "images"

    def test_extrair_docx_markdown(self):
        """Testa extração de DOCX para markdown"""
        if not DOCX_FILE.exists():
            pytest.skip("Arquivo DOCX de teste não encontrado")

        with open(DOCX_FILE, "rb") as f:
            files = {"file": ("exemplo.docx", f.read(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = client.post("/leitor-documentos/extrair-markdown", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "metadata" in data
        assert data["data"]["format"] == "markdown"
        assert len(data["data"]["content"]) > 0

    def test_extrair_docx_dados_brutos(self):
        """Testa extração de DOCX para dados brutos"""
        if not DOCX_FILE.exists():
            pytest.skip("Arquivo DOCX de teste não encontrado")

        with open(DOCX_FILE, "rb") as f:
            files = {"file": ("exemplo.docx", f.read(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = client.post("/leitor-documentos/extrair-dados-brutos", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "metadata" in data
        assert data["data"]["format"] == "raw"
        assert len(data["data"]["content"]) > 0

    def test_extrair_docx_imagens(self):
        """Testa extração de imagens do DOCX"""
        if not DOCX_FILE.exists():
            pytest.skip("Arquivo DOCX de teste não encontrado")

        with open(DOCX_FILE, "rb") as f:
            files = {"file": ("exemplo.docx", f.read(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = client.post("/leitor-documentos/extrair-dados-imagens", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "metadata" in data
        assert data["data"]["format"] == "images"

    def test_extrair_com_extractor_preferido(self):
        """Testa extração com extractor preferido"""
        if not PDF_FILE.exists():
            pytest.skip("Arquivo PDF de teste não encontrado")

        with open(PDF_FILE, "rb") as f:
            files = {"file": ("exemplo.pdf", f.read(), "application/pdf")}
            params = {"extrator_preferido": "PypdfExtractor"}
            response = client.post("/leitor-documentos/extrair-markdown", files=files, params=params)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["extractor_used"] == "pypdf"

    def test_extrair_com_extractor_inexistente(self):
        """Testa extração com extractor inexistente"""
        if not PDF_FILE.exists():
            pytest.skip("Arquivo PDF de teste não encontrado")

        with open(PDF_FILE, "rb") as f:
            files = {"file": ("exemplo.pdf", f.read(), "application/pdf")}
            params = {"extrator_preferido": "ExtractorInexistente"}
            response = client.post("/leitor-documentos/extrair-markdown", files=files, params=params)

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "error" in data

    def test_limpeza_endpoint(self):
        """Testa endpoint de limpeza"""
        response = client.post("/leitor-documentos/limpeza")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "removed_count" in data
        assert isinstance(data["removed_count"], int)

    def test_limpeza_com_parametro(self):
        """Testa endpoint de limpeza com parâmetro personalizado"""
        response = client.post("/leitor-documentos/limpeza?max_age_hours=12")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "removed_count" in data

    def test_limpeza_parametro_invalido(self):
        """Testa endpoint de limpeza com parâmetro inválido"""
        response = client.post("/leitor-documentos/limpeza?max_age_hours=0")
        assert response.status_code == 422

    def test_arquivo_muito_grande(self):
        """Testa upload de arquivo muito grande"""
        # Criar um arquivo grande simulado
        large_content = b"x" * (51 * 1024 * 1024)  # 51MB
        files = {"file": ("large.pdf", large_content, "application/pdf")}
        response = client.post("/leitor-documentos/extrair-markdown", files=files)

        assert response.status_code == 413
        data = response.json()
        assert data["success"] is False
        assert "error" in data

    def test_metadados_formatados(self):
        """Testa se os metadados estão formatados corretamente"""
        if not PDF_FILE.exists():
            pytest.skip("Arquivo PDF de teste não encontrado")

        with open(PDF_FILE, "rb") as f:
            files = {"file": ("exemplo.pdf", f.read(), "application/pdf")}
            response = client.post("/leitor-documentos/extrair-markdown", files=files)

        assert response.status_code == 200
        data = response.json()
        metadata = data["metadata"]
        
        # Verificar se file_size está formatado (não é um número)
        assert isinstance(metadata["file_size"], str)
        assert "MB" in metadata["file_size"] or "KB" in metadata["file_size"] or "B" in metadata["file_size"]
        
        # Verificar se extraction_time está formatado
        assert isinstance(metadata["extraction_time"], str)
        assert "s" in metadata["extraction_time"] or "ms" in metadata["extraction_time"]
        
        # Verificar outros campos
        assert isinstance(metadata["character_count"], int)
        assert isinstance(metadata["extractor_used"], str)
        assert metadata["character_count"] > 0
        assert len(metadata["extractor_used"]) > 0 