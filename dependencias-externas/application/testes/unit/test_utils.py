import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

from modules.leitor_documentos.utils import (
    format_duration,
    format_file_size,
    get_file_extension,
    sanitize_filename,
)


class TestUtils:
    """Testes unitários das funções utilitárias (isolados)"""

    def test_format_file_size_bytes(self):
        """Testa formatação de tamanho em bytes"""
        assert format_file_size(512) == "512 B"
        assert format_file_size(0) == "0 B"
        assert format_file_size(1023) == "1023 B"

    def test_format_file_size_kb(self):
        """Testa formatação de tamanho em KB"""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(2048) == "2.0 KB"

    def test_format_file_size_mb(self):
        """Testa formatação de tamanho em MB"""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1536 * 1024) == "1.5 MB"
        assert format_file_size(2.5 * 1024 * 1024) == "2.5 MB"

    def test_format_duration_milliseconds(self):
        """Testa formatação de duração em milissegundos"""
        assert format_duration(0.5) == "500ms"
        assert format_duration(0.123) == "123ms"
        assert format_duration(0.001) == "1ms"

    def test_format_duration_seconds(self):
        """Testa formatação de duração em segundos"""
        assert format_duration(1.5) == "1.5s"
        assert format_duration(30.7) == "30.7s"
        assert format_duration(59.9) == "59.9s"

    def test_format_duration_minutes(self):
        """Testa formatação de duração em minutos"""
        assert format_duration(90) == "1m 30.0s"
        assert format_duration(125.5) == "2m 5.5s"
        assert format_duration(180) == "3m 0.0s"

    def test_get_file_extension(self):
        """Testa extração de extensão de arquivo"""
        assert get_file_extension("documento.pdf") == "pdf"
        assert get_file_extension("ARQUIVO.PDF") == "pdf"
        assert get_file_extension("relatorio.docx") == "docx"

    def test_sanitize_filename(self):
        """Testa sanitização de nome de arquivo"""
        assert sanitize_filename("../../../etc/passwd") == "passwd"
        assert sanitize_filename("arquivo/perigoso\\nome") == "perigoso_nome"
        assert sanitize_filename("arquivo.normal.pdf") == "arquivo.normal.pdf"
        assert sanitize_filename("arquivo..malicioso") == "arquivomalicioso"


class TestUtilsEdgeCases:
    """Testes unitários para casos extremos das funções utilitárias"""

    def test_format_file_size_edge_cases(self):
        """Testa casos extremos na formatação de tamanho"""
        # Tamanhos muito grandes
        assert format_file_size(1024 * 1024 * 1024) == "1024.0 MB"  # 1GB

        # Tamanho negativo (caso improvável, mas defensivo)
        assert format_file_size(-100) == "-100 B"

    def test_format_duration_edge_cases(self):
        """Testa casos extremos na formatação de duração"""
        # Duração zero
        assert format_duration(0) == "0ms"

        # Duração muito pequena
        assert format_duration(0.0001) == "0ms"

        # Duração muito grande
        assert format_duration(7200) == "120m 0.0s"  # 2 horas

    def test_get_file_extension_edge_cases(self):
        """Testa casos extremos na extração de extensão"""
        # Arquivos com múltiplos pontos
        assert get_file_extension("arquivo.backup.pdf") == "pdf"

    def test_sanitize_filename_edge_cases(self):
        """Testa casos extremos na sanitização de nomes"""
        # Nome com apenas caracteres perigosos
        assert sanitize_filename("../../") == ""

        # Nome vazio
        assert sanitize_filename("") == ""

        # Nome com caracteres especiais mistos
        assert (
            sanitize_filename("arquivo@#$%^&*()nome.pdf") == "arquivo@#$%^&*()nome.pdf"
        )
