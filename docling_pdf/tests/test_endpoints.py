from fastapi.testclient import TestClient

from src.docling_pdf.main import app

client = TestClient(app)


class TestEndpoints:
    def test_root_endpoint(self):
        """Testa endpoint raiz"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "version" in data

    def test_health_check(self):
        """Testa health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_pdf_health_check(self):
        """Testa health check do router PDF"""
        response = client.get("/pdf/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_convert_without_file(self):
        """Testa conversão sem arquivo"""
        response = client.post("/pdf/convert")
        assert response.status_code == 422

    def test_convert_invalid_file_type(self):
        """Testa conversão com tipo de arquivo inválido"""
        files = {"file": ("test.txt", b"conteudo", "text/plain")}
        response = client.post("/pdf/convert", files=files)
        assert response.status_code == 400

    def test_cleanup_temp_files(self):
        """Testa limpeza de arquivos temporários"""
        response = client.post("/pdf/cleanup")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "removed_count" in data
