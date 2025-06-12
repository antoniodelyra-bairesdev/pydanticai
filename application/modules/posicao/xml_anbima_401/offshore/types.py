from typing import NamedTuple


class CodigosOpcao(NamedTuple):
    codigo_ativo_objeto: str
    codigo_serie: str


class CodigosFuturo(NamedTuple):
    codigo_ativo_objeto: str
    codigo_vencimento: str
