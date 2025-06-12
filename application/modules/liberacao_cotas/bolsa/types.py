from dataclasses import dataclass
from datetime import date
from typing import NamedTuple, Literal

from modules.posicao.xml_anbima_401.enums import Tags
from modules.liberacao_cotas.types import Ativo


@dataclass
class Acao(Ativo):
    data_referente: date | None
    preco_unitario: float | None
    tamanho_lote: int | float | None

    def __eq__(self: "Acao", other: "Acao") -> bool:
        return (
            self.isin == other.isin
            and self.data_referente == other.data_referente
            and self.codigo == other.codigo
            and self.preco_unitario == other.preco_unitario
        )

    def __repr__(self) -> str:
        return f"Acao(data_referente={self.data_referente}, isin={self.isin}, codigo={self.codigo}, preco_unitario={self.preco_unitario}, tamanho_lote={self.tamanho_lote})"

    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class Futuro(Ativo):
    data_referente: date | None
    ativo_objeto: Ativo
    codigo_vencimento: str | None
    preco_unitario: float | None
    tamanho_lote: int | float | None

    def __init__(
        self,
        isin: str | None,
        ativo_objeto: Ativo,
        data_referente: date | None,
        codigo_vencimento: str | None,
        preco_unitario: float | None,
        tamanho_lote: int | float | None,
    ):
        self.isin = isin
        self.codigo = (
            ativo_objeto.codigo + codigo_vencimento
            if codigo_vencimento is not None
            else ativo_objeto.codigo
        )
        self.tamanho_lote = tamanho_lote

        self.data_referente = data_referente
        self.ativo_objeto = ativo_objeto
        self.codigo_vencimento = codigo_vencimento
        self.preco_unitario = preco_unitario

    def __eq__(self: "Futuro", other: "Futuro") -> bool:
        return (
            self.isin == other.isin
            and self.data_referente == other.data_referente
            and self.codigo == other.codigo
            and self.preco_unitario == other.preco_unitario
        )

    def __repr__(self) -> str:
        return f"Futuro(data_referente={self.data_referente}, isin={self.isin}, codigo={self.codigo}, preco_unitario={self.preco_unitario}, tamanho_lote={self.tamanho_lote}, codigo_vencimento={self.codigo_vencimento}, ativo_objeto={self.ativo_objeto}"

    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class Opcao(Ativo):
    data_referente: date
    ativo_objeto: Ativo
    codigo_serie: str
    preco_unitario: float | None
    preco_exercicio: float
    tamanho_lote: int | float | None
    tipo: Literal["C", "P"]

    def __init__(
        self,
        isin: str | None,
        ativo_objeto: Ativo,
        data_referente: date,
        codigo_serie: str,
        preco_unitario: float | None,
        preco_exercicio: float,
        tamanho_lote: int | float | None,
        tipo: Literal["C", "P"],
    ):
        self.isin = isin
        self.codigo = ativo_objeto.codigo + codigo_serie
        self.tamanho_lote = tamanho_lote

        self.data_referente = data_referente
        self.ativo_objeto = ativo_objeto
        self.codigo_serie = codigo_serie
        self.preco_unitario = preco_unitario
        self.preco_exercicio = preco_exercicio
        self.tipo = tipo

    def __eq__(self: "Opcao", other: "Opcao") -> bool:
        return (
            self.isin == other.isin
            and self.data_referente == other.data_referente
            and self.codigo == other.codigo
            and self.preco_exercicio == other.preco_exercicio
            and self.preco_unitario == other.preco_unitario
            and self.tipo == other.tipo
        )

    def __repr__(self) -> str:
        return f"Opcao(data_referente={self.data_referente}, isin={self.isin}, codigo={self.codigo}, preco_unitario={self.preco_unitario}, tamanho_lote={self.tamanho_lote}, codigo_serie={self.codigo_serie}, preco_exercicio={self.preco_exercicio}, tipo={self.tipo}, opativo_objeto={self.ativo_objeto})"

    def __str__(self) -> str:
        return self.__repr__()


class CodigosOpcao(NamedTuple):
    codigo_ativo_objeto: str
    codigo_serie: str


class CodigosFuturo(NamedTuple):
    codigo_ativo_objeto: str
    codigo_vencimento: str


@dataclass
class OffshoreLinhaDEPARADerivativo:
    xml_tag: Literal[
        Tags.FUTUROS,
        Tags.OPCOESDERIV,
        Tags.OPCOESACOES,
    ]
    xml_codigo_ativo_objeto: str
    bloomberg_codigo_ativo_objeto: str
    tamanho_lote: int | None
