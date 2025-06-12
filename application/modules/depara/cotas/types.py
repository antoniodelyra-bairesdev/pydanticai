from dataclasses import dataclass


@dataclass
class LinhaDeparaCotaFundo:
    id_carteira: str
    codigo_britech_fundo_espelho: str | None
    apelido_fundo: str
    nome_fundo: str
    tipo: str
    cnpj: str | None
    isin: str
    codigo_interface: str | None
