from dataclasses import dataclass
from typing import Literal

from modules.posicao.xml_anbima_401.enums import Tags


@dataclass
class DeParaLinhaOffshoreAtivo:
    xml_tag: Literal[
        Tags.FUTUROS,
        Tags.OPCOESDERIV,
        Tags.OPCOESACOES,
    ]
    xml_codigo_ativo_objeto: str
    bloomberg_codigo_ativo_objeto: str
    tamanho_lote: int | None


@dataclass
class DeParaLinhaOffshoreBond:
    id_serie_britech: str
    isin: str
    nome_ativo: str
