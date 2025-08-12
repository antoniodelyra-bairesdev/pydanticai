import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from main import app

# Cliente de teste do FastAPI
client = TestClient(app)

# Caminhos para os arquivos de teste
SAMPLE_FILES_DIR = Path(__file__).parent.parent / "sample_files"
PDF_SAMPLE = SAMPLE_FILES_DIR / "exemplo.pdf"
DOCX_SAMPLE = SAMPLE_FILES_DIR / "exemplo.docx"

pytestmark = pytest.mark.integration


class TestAPIExtraction:
    """Testes de integração para endpoints de extração da API"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Verifica se os arquivos de exemplo existem"""
        self.pdf_exists = PDF_SAMPLE.exists()
        self.docx_exists = DOCX_SAMPLE.exists()

        if not SAMPLE_FILES_DIR.exists():
            pytest.skip("Diretório sample_files não encontrado")

    def test_extrair_pdf_markdown_docling(self):
        """Testa extração de PDF para markdown usando Docling"""
        if not self.pdf_exists:
            pytest.skip("Arquivo PDF de exemplo não encontrado")

        with open(PDF_SAMPLE, "rb") as f:
            files = {"file": ("exemplo.pdf", f.read(), "application/pdf")}
            response = client.post("/leitor-documentos/extrair-markdown", files=files)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "data" in data
        assert "metadata" in data

        # Verificar dados da extração
        extraction_data = data["data"]
        assert extraction_data["format"] == "markdown"
        assert extraction_data["extractor_used"] == "docling_pdf"
        assert len(extraction_data["content"]) > 0

        # Verificar metadados
        metadata = data["metadata"]
        assert "file_size" in metadata
        assert "extraction_time" in metadata
        assert "character_count" in metadata
        assert "extractor_used" in metadata
        assert "created_at" in metadata
        assert "filename" in metadata
        assert metadata["filename"] == "exemplo.pdf"
        assert metadata["character_count"] > 0

    def test_extrair_pdf_markdown_pypdf(self):
        """Testa extração de PDF para markdown usando pypdf (deve dar erro)"""
        if not self.pdf_exists:
            pytest.skip("Arquivo PDF de exemplo não encontrado")

        with open(PDF_SAMPLE, "rb") as f:
            files = {"file": ("exemplo.pdf", f.read(), "application/pdf")}
            params = {"ferramenta_extracao": "pypdf"}
            response = client.post(
                "/leitor-documentos/extrair-markdown", files=files, params=params
            )

        # pypdf não implementa extract_to_markdown
        assert response.status_code == 501
        data = response.json()
        assert data["detail"]["success"] is False
        assert data["detail"]["error_code"] == "NOT_IMPLEMENTED"

    def test_extrair_pdf_dados_brutos_docling(self):
        """Testa extração de dados brutos de PDF usando Docling"""
        if not self.pdf_exists:
            pytest.skip("Arquivo PDF de exemplo não encontrado")

        with open(PDF_SAMPLE, "rb") as f:
            files = {"file": ("exemplo.pdf", f.read(), "application/pdf")}
            response = client.post(
                "/leitor-documentos/extrair-dados-brutos", files=files
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        extraction_data = data["data"]
        assert extraction_data["format"] == "raw"
        assert extraction_data["extractor_used"] == "docling_pdf"
        assert len(extraction_data["content"]) > 0

    def test_extrair_pdf_dados_brutos_pypdf(self):
        """Testa extração de dados brutos de PDF usando pypdf"""
        if not self.pdf_exists:
            pytest.skip("Arquivo PDF de exemplo não encontrado")

        with open(PDF_SAMPLE, "rb") as f:
            files = {"file": ("exemplo.pdf", f.read(), "application/pdf")}
            params = {"ferramenta_extracao": "pypdf"}
            response = client.post(
                "/leitor-documentos/extrair-dados-brutos", files=files, params=params
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        extraction_data = data["data"]
        assert extraction_data["format"] == "raw"
        assert extraction_data["extractor_used"] == "pypdf"

    def test_extrair_pdf_imagens_pypdf(self):
        """Testa extração de imagens de PDF usando pypdf (deve dar erro)"""
        if not self.pdf_exists:
            pytest.skip("Arquivo PDF de exemplo não encontrado")

        with open(PDF_SAMPLE, "rb") as f:
            files = {"file": ("exemplo.pdf", f.read(), "application/pdf")}
            params = {"ferramenta_extracao": "pypdf"}
            response = client.post(
                "/leitor-documentos/extrair-dados-imagens", files=files, params=params
            )

        # pypdf não implementa extract_image_data
        assert response.status_code == 501
        data = response.json()
        assert data["detail"]["success"] is False
        assert data["detail"]["error_code"] == "NOT_IMPLEMENTED"

    def test_extrair_docx_markdown_docling(self):
        """Testa extração de DOCX para markdown usando Docling"""
        if not self.docx_exists:
            pytest.skip("Arquivo DOCX de exemplo não encontrado")

        with open(DOCX_SAMPLE, "rb") as f:
            files = {
                "file": (
                    "exemplo.docx",
                    f.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            }
            response = client.post("/leitor-documentos/extrair-markdown", files=files)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        extraction_data = data["data"]
        assert extraction_data["format"] == "markdown"
        assert extraction_data["extractor_used"] == "docling_docx"
        assert len(extraction_data["content"]) > 0

    def test_extrair_docx_markdown_docx2txt(self):
        """Testa extração de DOCX para markdown usando docx2txt (deve dar erro)"""
        if not self.docx_exists:
            pytest.skip("Arquivo DOCX de exemplo não encontrado")

        with open(DOCX_SAMPLE, "rb") as f:
            files = {
                "file": (
                    "exemplo.docx",
                    f.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            }
            params = {"ferramenta_extracao": "docx2txt"}
            response = client.post(
                "/leitor-documentos/extrair-markdown", files=files, params=params
            )

        # docx2txt não implementa extract_to_markdown
        assert response.status_code == 501
        data = response.json()
        assert data["detail"]["success"] is False
        assert data["detail"]["error_code"] == "NOT_IMPLEMENTED"

    def test_extrair_docx_dados_brutos_docling(self):
        """Testa extração de dados brutos de DOCX usando Docling"""
        if not self.docx_exists:
            pytest.skip("Arquivo DOCX de exemplo não encontrado")

        with open(DOCX_SAMPLE, "rb") as f:
            files = {
                "file": (
                    "exemplo.docx",
                    f.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            }
            response = client.post(
                "/leitor-documentos/extrair-dados-brutos", files=files
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        extraction_data = data["data"]
        assert extraction_data["format"] == "raw"
        assert extraction_data["extractor_used"] == "docling_docx"
        assert len(extraction_data["content"]) > 0

    def test_extrair_docx_dados_brutos_docx2txt(self):
        """Testa extração de dados brutos de DOCX usando docx2txt"""
        if not self.docx_exists:
            pytest.skip("Arquivo DOCX de exemplo não encontrado")

        with open(DOCX_SAMPLE, "rb") as f:
            files = {
                "file": (
                    "exemplo.docx",
                    f.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            }
            params = {"ferramenta_extracao": "docx2txt"}
            response = client.post(
                "/leitor-documentos/extrair-dados-brutos", files=files, params=params
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        extraction_data = data["data"]
        assert extraction_data["format"] == "raw"
        assert extraction_data["extractor_used"] == "docx2txt"

    def test_extrair_docx_imagens_docx2txt(self):
        """Testa extração de imagens de DOCX usando docx2txt (deve dar erro)"""
        if not self.docx_exists:
            pytest.skip("Arquivo DOCX de exemplo não encontrado")

        with open(DOCX_SAMPLE, "rb") as f:
            files = {
                "file": (
                    "exemplo.docx",
                    f.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            }
            params = {"ferramenta_extracao": "docx2txt"}
            response = client.post(
                "/leitor-documentos/extrair-dados-imagens", files=files, params=params
            )

        # docx2txt não implementa extract_image_data
        assert response.status_code == 501
        data = response.json()
        assert data["detail"]["success"] is False
        assert data["detail"]["error_code"] == "NOT_IMPLEMENTED"

    def test_metadados_formatacao(self):
        """Testa se os metadados estão sendo formatados corretamente"""
        if not self.pdf_exists:
            pytest.skip("Arquivo PDF de exemplo não encontrado")

        with open(PDF_SAMPLE, "rb") as f:
            files = {"file": ("exemplo.pdf", f.read(), "application/pdf")}
            response = client.post("/leitor-documentos/extrair-markdown", files=files)

        assert response.status_code == 200
        data = response.json()
        metadata = data["metadata"]

        # Verificar formatação do tamanho do arquivo
        file_size = metadata["file_size"]
        assert isinstance(file_size, str)
        assert any(unit in file_size for unit in ["B", "KB", "MB"])

        # Verificar formatação do tempo de extração
        extraction_time = metadata["extraction_time"]
        assert isinstance(extraction_time, str)
        assert any(unit in extraction_time for unit in ["ms", "s", "m"])

        # Verificar outros campos
        assert isinstance(metadata["character_count"], int)
        assert metadata["character_count"] > 0
        assert isinstance(metadata["extractor_used"], str)
        assert len(metadata["extractor_used"]) > 0
        assert isinstance(metadata["created_at"], str)

    def test_extrair_pdf_markdown_llmwhisperer(self):
        """Testa extração de PDF para markdown usando LLMWhisperer"""
        if not self.pdf_exists:
            pytest.skip("Arquivo PDF de exemplo não encontrado")

        with open(PDF_SAMPLE, "rb") as f:
            files = {"file": ("exemplo.pdf", f.read(), "application/pdf")}
            params = {"ferramenta_extracao": "llmwhisperer"}
            response = client.post(
                "/leitor-documentos/extrair-markdown", files=files, params=params
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "data" in data
        assert "metadata" in data

        # Verificar dados da extração
        extraction_data = data["data"]
        assert extraction_data["format"] == "markdown"
        assert extraction_data["extractor_used"] == "llmwhisperer_pdf"
        assert len(extraction_data["content"]) > 0

        # Verificar metadados
        metadata = data["metadata"]
        assert "file_size" in metadata
        assert "extraction_time" in metadata
        assert "character_count" in metadata
        assert "extractor_used" in metadata
        assert "created_at" in metadata
        assert "filename" in metadata
        assert metadata["filename"] == "exemplo.pdf"
        assert metadata["character_count"] > 0
        assert metadata["extractor_used"] == "llmwhisperer_pdf"

    def test_extrair_pdf_dados_brutos_llmwhisperer(self):
        """Testa extração de dados brutos de PDF usando LLMWhisperer"""
        if not self.pdf_exists:
            pytest.skip("Arquivo PDF de exemplo não encontrado")

        with open(PDF_SAMPLE, "rb") as f:
            files = {"file": ("exemplo.pdf", f.read(), "application/pdf")}
            params = {"ferramenta_extracao": "llmwhisperer"}
            response = client.post(
                "/leitor-documentos/extrair-dados-brutos", files=files, params=params
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        extraction_data = data["data"]
        assert extraction_data["format"] == "raw"
        assert extraction_data["extractor_used"] == "llmwhisperer_pdf"
        assert len(extraction_data["content"]) > 0

    def test_extrair_pdf_imagens_llmwhisperer(self):
        """Testa extração de imagens de PDF usando LLMWhisperer"""
        if not self.pdf_exists:
            pytest.skip("Arquivo PDF de exemplo não encontrado")

        with open(PDF_SAMPLE, "rb") as f:
            files = {"file": ("exemplo.pdf", f.read(), "application/pdf")}
            params = {"ferramenta_extracao": "llmwhisperer"}
            response = client.post(
                "/leitor-documentos/extrair-dados-imagens", files=files, params=params
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        extraction_data = data["data"]
        assert extraction_data["format"] == "images"
        assert extraction_data["extractor_used"] == "llmwhisperer_pdf"
        assert len(extraction_data["content"]) > 0

    def test_extrair_docx_markdown_llmwhisperer(self):
        """Testa extração de DOCX para markdown usando LLMWhisperer"""
        if not self.docx_exists:
            pytest.skip("Arquivo DOCX de exemplo não encontrado")

        with open(DOCX_SAMPLE, "rb") as f:
            files = {
                "file": (
                    "exemplo.docx",
                    f.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            }
            params = {"ferramenta_extracao": "llmwhisperer"}
            response = client.post(
                "/leitor-documentos/extrair-markdown", files=files, params=params
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        extraction_data = data["data"]
        assert extraction_data["format"] == "markdown"
        assert extraction_data["extractor_used"] == "llmwhisperer_docx"
        assert len(extraction_data["content"]) > 0

    def test_extrair_docx_dados_brutos_llmwhisperer(self):
        """Testa extração de dados brutos de DOCX usando LLMWhisperer"""
        if not self.docx_exists:
            pytest.skip("Arquivo DOCX de exemplo não encontrado")

        with open(DOCX_SAMPLE, "rb") as f:
            files = {
                "file": (
                    "exemplo.docx",
                    f.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            }
            params = {"ferramenta_extracao": "llmwhisperer"}
            response = client.post(
                "/leitor-documentos/extrair-dados-brutos", files=files, params=params
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        extraction_data = data["data"]
        assert extraction_data["format"] == "raw"
        assert extraction_data["extractor_used"] == "llmwhisperer_docx"
        assert len(extraction_data["content"]) > 0

    def test_extrair_docx_imagens_llmwhisperer(self):
        """Testa extração de imagens de DOCX usando LLMWhisperer"""
        if not self.docx_exists:
            pytest.skip("Arquivo DOCX de exemplo não encontrado")

        with open(DOCX_SAMPLE, "rb") as f:
            files = {
                "file": (
                    "exemplo.docx",
                    f.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            }
            params = {"ferramenta_extracao": "llmwhisperer"}
            response = client.post(
                "/leitor-documentos/extrair-dados-imagens", files=files, params=params
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        extraction_data = data["data"]
        assert extraction_data["format"] == "images"
        assert extraction_data["extractor_used"] == "llmwhisperer_docx"
        assert len(extraction_data["content"]) > 0
