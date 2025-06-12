from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from modules.caracteristicas_fundos.types import FundoInfo as CaracteristicasFundoInfo


@dataclass
class FundoInfo(CaracteristicasFundoInfo):
    nome_arq_xml_anbima_401: str


@dataclass
class AtivoPrecosFundos:
    codigo: str
    isin: str
    data: date
    precos_fundos: dict[Decimal, list[FundoInfo]]

    def append_fundo_precos_fundos(
        self, preco_unitario_posicao: Decimal, fundo_info: FundoInfo
    ) -> None:
        if self.precos_fundos.get(preco_unitario_posicao) is None:
            self.precos_fundos[preco_unitario_posicao] = [fundo_info]
        else:
            self.precos_fundos[preco_unitario_posicao].append(fundo_info)
