from dataclasses import dataclass
from datetime import date
from ..types import AtivoRendaFixa


@dataclass
class LinhaDEPARACreditoPrivado:
    codigo_cetip: str
    id_titulo: str
    id_serie: str
    tipo: str
    isin: str | None


@dataclass
class LinhaDEPARARendaFixaMarcadaNaCurva:
    id_interno_ativo: str
    ativo: str
    data_vencimento: date
    id_serie: str


@dataclass
class FundoPrecoTituloPrivado:
    fundo_codigo_britech: str
    titulo_credito_privado: AtivoRendaFixa

    def __eq__(
        self: "FundoPrecoTituloPrivado", other: "FundoPrecoTituloPrivado"
    ) -> bool:
        return (
            self.fundo_codigo_britech == other.fundo_codigo_britech
            and self.titulo_credito_privado == other.titulo_credito_privado
        )
