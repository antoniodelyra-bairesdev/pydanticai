from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class XMLAnbima401Aluguel:
    class Meta:
        name = "aluguel"

    dtvencalug: str = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    txalug: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    indexadoralug: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    percalug: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )


@dataclass
class XMLAnbima401Acoes:
    class Meta:
        name = "acoes"

    isin: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    codativo: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    qtdisponivel: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    lote: int = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    qtgarantia: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valorfindisp: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valorfinemgar: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    tributos: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    puposicao: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    percprovcred: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    tpconta: int = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # C – Comprado
    # D – Doado
    # T – Tomado
    # V - Vendido
    classeoperacao: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    dtvencalug: str | None = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    txalug: Decimal | None = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    cnpjinter: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    cusip: str | None = field(
        default=None,
        metadata={"type": "Element", "required": True},
    )


@dataclass
class XMLAnbima401Opcoesacoes:
    class Meta:
        name = "opcoesacoes"

    isin: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    codativo: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    ativobase: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    qtdisponivel: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valorfinanceiro: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    precoexercicio: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    dtvencimento: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # C - Comprado (ponta títular)
    # V - Vendido (ponta lançadora)
    classeoperacao: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    tributos: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    puposicao: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    premio: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    percprovcred: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # 1 - Conta movimento
    # 2 - Conta investimento
    tpconta: int = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # S - Sim
    # N - Não
    hedge: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # 0 - Não faz parte de um hedge
    # 1 - Hedge de renda fixa
    # 2 - Hedge de renda variável
    tphedge: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    cusip: str | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class XMLAnbima401Opcoesderiv:
    class Meta:
        name = "opcoesderiv"

    isin: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # 1 - Disponível
    # 2 - Futuro
    mercado: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    ativo: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    serie: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # C - Call
    # P - Put
    callput: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    quantidade: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valorfinanceiro: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    tributos: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    precoexercicio: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    premio: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    dtvencimento: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # C - Comprado
    # V - Vendido
    classeoperacao: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    puposicao: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # S - Sim
    # N - Não
    hedge: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # 0 - Não faz parte de um hedge
    # 1 - Hedge de renda fixa
    # 2 - Hedge de renda variável
    tphedge: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class XMLAnbima401Caixa:
    class Meta:
        name = "caixa"

    isininstituicao: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    tpconta: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    saldo: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # AA - Alto
    # MA - Médio Alto
    # MM - Médio
    # BB - Baixo
    nivelrsc: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class XMLAnbima401Compromisso:
    class Meta:
        name = "compromisso"

    dtretorno: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    puretorno: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    indexadorcomp: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    perindexcomp: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    txoperacao: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # C - Compra com Revenda
    # V - Venda com Recompra
    classecomp: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class XMLAnbima401Cotas:
    class Meta:
        name = "cotas"

    isin: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    cnpjfundo: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    qtdisponivel: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    qtgarantia: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    puposicao: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    tributos: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # AA - Alto
    # MA - Médio Alto
    # MM - Médio
    # BB - Baixo
    nivelrsc: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class XMLAnbima401Debenture:
    class Meta:
        name = "debenture"

    isin: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    coddeb: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # S - Sim
    # N - Não
    debconv: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # S - Sim
    # N - Não
    debpartlucro: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # S - Sim
    # N - Não
    spe: str = field(
        metadata={
            "name": "SPE",
            "type": "Element",
            "required": True,
        },
    )
    dtemissao: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    dtoperacao: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    dtvencimento: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    cnpjemissor: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    qtdisponivel: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    qtgarantia: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    depgar: int = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    pucompra: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    puvencimento: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    puposicao: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    puemissao: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    principal: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    tributos: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valorfindisp: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valorfinemgar: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    coupom: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    indexador: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    percindex: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # N - Negociação
    # V - Vencimento
    caracteristica: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    percprovcred: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # C – Comprado
    # D – Doado
    # T – Tomado
    # V - Vendido
    classeoperacao: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    idinternoativo: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    compromisso: XMLAnbima401Compromisso | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    aluguel: XMLAnbima401Aluguel | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    # AA - Alto
    # MA - Médio Alto
    # MM - Médio
    # BB - Baixo
    nivelrsc: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    cusip: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class XMLAnbima401Despesas:
    class Meta:
        name = "despesas"

    txadm: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    tributos: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    perctaxaadm: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # S - Sim
    # N - Não
    txperf: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    vltxperf: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    perctxperf: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    percindex: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    outtax: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    indexador: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class XMLAnbima401Futuros:
    class Meta:
        name = "futuros"

    isin: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    ativo: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    cnpjcorretora: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    serie: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    quantidade: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    vltotalpos: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    tributos: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    dtvencimento: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    vlajuste: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # C - Comprado
    # V - Vendido
    classeoperacao: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # C - Comprado
    # V - Vendido
    hedge: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # 0 - Não faz parte de um hedge
    # 1 - Hedge de renda fixa
    # 2 - Hedge de renda variável
    tphedge: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class XMAnbima401Header:
    class Meta:
        name = "header"

    isin: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    cnpj: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    nome: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    dtposicao: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    nomeadm: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    cnpjadm: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    nomegestor: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    cnpjgestor: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    nomecustodiante: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    cnpjcustodiante: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valorcota: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    quantidade: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    patliq: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valorativos: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valorreceber: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valorpagar: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    vlcotasemitir: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    vlcotasresgatar: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    codanbid: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    tipofundo: int = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # AA - Alto
    # MA - Médio Alto
    # MM - Médio
    # BB - Baixo
    nivelrsc: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    cusip: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class XMLAnbima401Outrasdespesas:
    class Meta:
        name = "outrasdespesas"

    coddesp: int = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valor: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class XMLAnbima401Provisao:
    class Meta:
        name = "provisao"

    codprov: int = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # C - Provisão de crédito
    # D - Provisão de débito
    credeb: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    dt: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valor: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class XMLAnbima401Titprivado:
    class Meta:
        name = "titprivado"

    isin: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    codativo: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    dtemissao: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    dtoperacao: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    dtvencimento: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    cnpjemissor: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    qtdisponivel: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    qtgarantia: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    depgar: int = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    pucompra: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    puvencimento: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    puposicao: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    puemissao: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    principal: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    tributos: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valorfindisp: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valorfinemgar: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    coupom: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    indexador: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    percindex: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # N - Negociação
    # V - Vencimento
    caracteristica: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    percprovcred: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # C – Comprado
    # D – Doado
    # T – Tomado
    # V - Vendido
    classeoperacao: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    idinternoativo: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    compromisso: XMLAnbima401Compromisso | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    aluguel: XMLAnbima401Aluguel | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    # AA - Alto
    # MA - Médio Alto
    # MM - Médio
    # BB - Baixo
    nivelrsc: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    cusip: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class XMLAnbima401Titpublico:
    class Meta:
        name = "titpublico"

    isin: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    codativo: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    dtemissao: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    dtoperacao: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    dtvencimento: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    qtdisponivel: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    qtgarantia: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    depgar: int = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    pucompra: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    puvencimento: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    puposicao: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    puemissao: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    principal: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    tributos: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valorfindisp: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    valorfinemgar: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    coupom: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    indexador: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    percindex: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # N - Negociação
    # V - Vencimento
    caracteristica: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    percprovcred: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    # C – Comprado
    # D – Doado
    # T – Tomado
    # V - Vendido
    classeoperacao: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    idinternoativo: str = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    compromisso: XMLAnbima401Compromisso | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    aluguel: XMLAnbima401Aluguel | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    nivelrsc: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    cusip: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class XMLAnbima401Fundo:
    class Meta:
        name = "fundo"

    header: XMAnbima401Header = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    titpublico: list[XMLAnbima401Titpublico] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    titprivado: list[XMLAnbima401Titprivado] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    debenture: list[XMLAnbima401Debenture] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    acoes: list[XMLAnbima401Acoes] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    futuros: list[XMLAnbima401Futuros] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    opcoesacoes: list[XMLAnbima401Opcoesacoes] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    opcoesderiv: list[XMLAnbima401Opcoesderiv] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )

    caixa: list[XMLAnbima401Caixa] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    cotas: list[XMLAnbima401Cotas] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    despesas: XMLAnbima401Despesas | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    outrasdespesas: list[XMLAnbima401Outrasdespesas] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    provisao: list[XMLAnbima401Provisao] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class XMLAnbima401Posicao:
    class Meta:
        name = "arquivoposicao_4_01"

    fundo: XMLAnbima401Fundo = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )

    def get_pl_calculado(self) -> Decimal:
        pl: Decimal = (
            self.get_caixa()
            + self.get_net_ativos()
            + self.get_net_provisoes()
            - self.fundo.header.vlcotasemitir
            - self.fundo.header.vlcotasresgatar
        )
        return pl

    def get_caixa(self) -> Decimal:
        soma_caixa: Decimal = Decimal(0)
        for caixa in self.fundo.caixa:
            soma_caixa = soma_caixa + caixa.saldo

        return soma_caixa

    def get_net_provisoes(self) -> Decimal:
        net_provisoes: Decimal = Decimal(0)
        for provisao in self.fundo.provisao:
            if provisao.credeb == "C":
                net_provisoes = net_provisoes + provisao.valor
            elif provisao.credeb == "D":
                net_provisoes = net_provisoes - provisao.valor

        return net_provisoes

    def get_net_ativos(self) -> Decimal:
        net_ativos: Decimal = Decimal(
            self.get_net_titulos_publicos()
            + self.get_net_titulos_privados()
            + self.get_net_debentures()
            + self.get_net_acoes()
            + self.get_net_futuros()
            + self.get_net_opcoes_acoes()
            + self.get_net_opcoes_derivativos()
            + self.get_soma_cotas()
        )

        return net_ativos

    def get_net_titulos_publicos(self) -> Decimal:
        net_titulos_publicos: Decimal = Decimal(0)
        for titulo_publico in self.fundo.titpublico:
            if titulo_publico.classeoperacao == "C":
                net_titulos_publicos = (
                    net_titulos_publicos
                    + titulo_publico.valorfindisp
                    + titulo_publico.valorfinemgar
                    - titulo_publico.tributos
                )
            elif titulo_publico.classeoperacao == "V":
                net_titulos_publicos = (
                    net_titulos_publicos
                    + (titulo_publico.valorfindisp + titulo_publico.valorfinemgar) * -1
                    - titulo_publico.tributos
                )

        return net_titulos_publicos

    def get_net_titulos_privados(self) -> Decimal:
        net_titulos_privados: Decimal = Decimal(0)
        for titulo_privado in self.fundo.titprivado:
            if titulo_privado.classeoperacao == "C":
                net_titulos_privados = (
                    net_titulos_privados
                    + titulo_privado.valorfindisp
                    + titulo_privado.valorfinemgar
                )
            elif titulo_privado.classeoperacao == "V":
                net_titulos_privados = (
                    net_titulos_privados
                    + (titulo_privado.valorfindisp + titulo_privado.valorfinemgar) * -1
                )

        return net_titulos_privados

    def get_net_debentures(self) -> Decimal:
        net_debentures: Decimal = Decimal(0)
        for debenture in self.fundo.debenture:
            if debenture.classeoperacao == "C":
                net_debentures = (
                    net_debentures + debenture.valorfindisp + debenture.valorfinemgar
                )
            elif debenture.classeoperacao == "V":
                net_debentures = (
                    net_debentures
                    + (debenture.valorfindisp + debenture.valorfinemgar) * -1
                )

        return net_debentures

    def get_net_acoes(self) -> Decimal:
        net_acoes: Decimal = Decimal(0)
        for acao in self.fundo.acoes:
            if acao.classeoperacao == "C" or acao.classeoperacao == "D":
                net_acoes = net_acoes + acao.valorfindisp + acao.valorfinemgar
            elif acao.classeoperacao == "V":
                net_acoes = net_acoes + (acao.valorfindisp + acao.valorfinemgar) * -1

        return net_acoes

    def get_net_futuros(self) -> Decimal:
        net_futuros: Decimal = Decimal(0)
        for futuro in self.fundo.futuros:
            net_futuros = net_futuros + futuro.vlajuste

        return net_futuros

    def get_net_opcoes_acoes(self) -> Decimal:
        net_opcoes_acoes: Decimal = Decimal(0)
        for opcao_acao in self.fundo.opcoesacoes:
            if opcao_acao.classeoperacao == "C":
                net_opcoes_acoes = net_opcoes_acoes + opcao_acao.valorfinanceiro
            elif opcao_acao.classeoperacao == "V":
                net_opcoes_acoes = net_opcoes_acoes - opcao_acao.valorfinanceiro

        return net_opcoes_acoes

    def get_net_opcoes_derivativos(self) -> Decimal:
        net_opcoes_derivativos: Decimal = Decimal(0)
        for opcao_derivativo in self.fundo.opcoesderiv:
            if opcao_derivativo.classeoperacao == "C":
                net_opcoes_derivativos = (
                    net_opcoes_derivativos + opcao_derivativo.valorfinanceiro
                )
            elif opcao_derivativo.classeoperacao == "V":
                net_opcoes_derivativos = (
                    net_opcoes_derivativos - opcao_derivativo.valorfinanceiro
                )

        return net_opcoes_derivativos

    def get_soma_cotas(self) -> Decimal:
        soma_cotas: Decimal = Decimal(0)
        for cota in self.fundo.cotas:
            soma_cotas = (
                soma_cotas
                + (cota.puposicao * (cota.qtdisponivel + cota.qtgarantia))
                - cota.tributos
            )

        return soma_cotas

    def get_soma_outras_despesas(self) -> Decimal:
        soma_outras_despesas: Decimal = Decimal(0)
        for despesa in self.fundo.outrasdespesas:
            soma_outras_despesas = soma_outras_despesas + despesa.valor

        return soma_outras_despesas
