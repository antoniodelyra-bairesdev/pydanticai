from dataclasses import dataclass, field
from enum import Enum
from io import BytesIO
from typing import Any, Callable, Optional

from xlsxwriter import Workbook


class Fmt:
    NEGRITO = {"bold": 1}
    CENTRALIZAR = {"align": "center"}
    DATA = {"num_format": "dd/mm/yyyy"}
    INTEIRO = {"num_format": "#,##0"}

    @staticmethod
    def DECIMAL(obrigatorias: int, opcionais: int = 0):
        return {
            "num_format": f"#,##0.{'0'*obrigatorias}{'#'*(opcionais if opcionais else 0)}"
        }


@dataclass
class Planilha:
    nome: str
    abas: list["Aba"]

    def gerar(self):
        buffer = BytesIO()
        xlsxwriter_workbook = Workbook(buffer, {"in_memory": True})
        fmt_title = xlsxwriter_workbook.add_format({**Fmt.NEGRITO, **Fmt.CENTRALIZAR})

        for aba in self.abas:
            xlsxwriter_aba = xlsxwriter_workbook.add_worksheet(aba.nome)
            col = 0

            for coluna in aba.colunas:
                formatacao = {}
                for formato in coluna.formatacao:
                    regras = formato if type(formato) == dict else {}
                    formatacao = {**formatacao, **regras}
                coluna._format = xlsxwriter_workbook.add_format(formatacao)
                xlsxwriter_aba.write(0, col, coluna.titulo, fmt_title)
                col += 1

            row = 1
            for linha in aba.dados:
                col = 0
                for dado in linha:
                    coluna = aba.colunas[col]
                    xlsxwriter_aba.write(row, col, dado, coluna._format)
                    col += 1
                row += 1

            xlsxwriter_aba.autofit()

        xlsxwriter_workbook.close()

        buffer.seek(0)
        return buffer


@dataclass
class Aba:
    nome: str
    colunas: list["Coluna"]
    dados: list[list[Any]]


@dataclass
class Coluna:
    titulo: str
    formatacao: list[dict[str, Any] | Fmt] = field(default_factory=list)

    _format: Any | None = None
