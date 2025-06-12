from dataclasses import dataclass


@dataclass
class FundoInfo:
    codigo_britech: str
    codigo_administrador: str
    cnpj: str
    nome: str
    tipo_cota: str
    custodiante: str
