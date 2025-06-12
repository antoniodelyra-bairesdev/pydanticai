from datetime import date

from ..types import Ativo


class CotaFundo(Ativo):
    def __init__(
        self,
        isin: str | None,
        codigo_britech: str,
        cnpj: str,
        quantidade: float | None,
        preco_unitario: float,
        patrimonio_liquido: float | None,
        is_externo: bool | None,
        nivel_risco: str | None,
        data_referente: date,
    ):
        self.isin = isin
        self.codigo = f"{isin} | {cnpj}"
        self.codigo_britech = codigo_britech
        self.cnpj = cnpj
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.patrimonio_liquido = patrimonio_liquido
        self.is_externo = is_externo
        self.nivel_risco = nivel_risco
        self.data_referente = data_referente

    def __eq__(self: "CotaFundo", other: "CotaFundo") -> bool:
        return (
            self.isin == other.isin
            and self.codigo == other.codigo
            and self.codigo_britech == other.codigo_britech
            and self.cnpj == other.cnpj
            and self.data_referente == other.data_referente
        )

    def __repr__(self) -> str:
        return f"CotaFundo(data_referente='{self.data_referente}', isin='{self.isin}', codigo='{self.codigo}', codigo_britech='{self.codigo_britech}', cnpj='{self.cnpj}', quantidade='{self.quantidade}', preco_unitario='{self.preco_unitario}', patrimonio_liquido='{self.patrimonio_liquido}', is_externo='{self.is_externo}', nivel_risco='{self.nivel_risco}')"
