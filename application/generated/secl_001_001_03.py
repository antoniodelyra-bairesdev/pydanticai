from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from xsdata.models.datatype import XmlDate, XmlDateTime

__NAMESPACE__ = "urn:secl.001.001.03.xsd"


@dataclass
class ActiveCurrencyAndAmount:
    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
            "total_digits": 18,
            "fraction_digits": 5,
        },
    )
    ccy: Optional[str] = field(
        default=None,
        metadata={
            "name": "Ccy",
            "type": "Attribute",
            "required": True,
            "pattern": r"[A-Z]{3,3}",
        },
    )


@dataclass
class ActiveOrHistoricCurrencyAnd13DecimalAmount:
    value: Decimal = field(
        metadata={
            "required": True,
            "total_digits": 18,
            "fraction_digits": 13,
        },
    )
    ccy: str = field(
        metadata={
            "name": "Ccy",
            "type": "Attribute",
            "required": True,
            "pattern": r"[A-Z]{3,3}",
        },
    )


@dataclass
class ActiveOrHistoricCurrencyAndAmount:
    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
            "total_digits": 18,
            "fraction_digits": 5,
        },
    )
    ccy: Optional[str] = field(
        default=None,
        metadata={
            "name": "Ccy",
            "type": "Attribute",
            "required": True,
            "pattern": r"[A-Z]{3,3}",
        },
    )


@dataclass
class AmountAndDirection27:
    amt: str = field(
        default="0",
        metadata={
            "name": "Amt",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


class ClearingAccountType1Code(Enum):
    CLIE = "CLIE"
    HOUS = "HOUS"
    LIPR = "LIPR"


@dataclass
class DateFormat15Choice:
    dt: XmlDate = field(
        metadata={
            "name": "Dt",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class FinancialInstrumentQuantity1Choice:
    unit: Decimal = field(
        metadata={
            "name": "Unit",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
            "total_digits": 18,
            "fraction_digits": 17,
        },
    )


@dataclass
class GenericIdentification29:
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    issr: str = field(
        metadata={
            "name": "Issr",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    schme_nm: str = field(
        metadata={
            "name": "SchmeNm",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class IdentificationSource3Choice:
    prtry: str = field(
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class MarketIdentification1Choice:
    mkt_idr_cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "MktIdrCd",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
            "pattern": r"[A-Z0-9]{4,4}",
        },
    )


class MarketType2Code(Enum):
    EXCH = "EXCH"
    OTCO = "OTCO"


class MarketType5Code(Enum):
    OTCO = "OTCO"
    EXCH = "EXCH"


class Side1Code(Enum):
    BUYI = "BUYI"
    SELL = "SELL"


@dataclass
class SupplementaryDataContents1:
    supl_secl_001_001_03_element: Optional[object] = field(
        default=None,
        metadata={
            "type": "Wildcard",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
        },
    )


class TradeType1Code(Enum):
    LKTR = "LKTR"
    OOBK = "OOBK"
    GUTR = "GUTR"


class TradingCapacity5Code(Enum):
    AGEN = "AGEN"
    PRIN = "PRIN"
    RISP = "RISP"


@dataclass
class AmountAndDirection21:
    amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "Amt",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class MarketIdentification21:
    id: MarketIdentification1Choice = field(
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class MarketType8Choice:
    cd: Optional[MarketType2Code] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class MarketType9Choice:
    cd: Optional[MarketType5Code] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class OtherIdentification1:
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    tp: IdentificationSource3Choice = field(
        metadata={
            "name": "Tp",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class PartyIdentification35Choice:
    prtry_id: GenericIdentification29 = field(
        metadata={
            "name": "PrtryId",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class PriceRateOrAmountChoice:
    amt: ActiveOrHistoricCurrencyAnd13DecimalAmount = field(
        metadata={
            "name": "Amt",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class SecuritiesAccount18:
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    tp: ClearingAccountType1Code = field(
        default=ClearingAccountType1Code.CLIE,
        metadata={
            "name": "Tp",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class Settlement1:
    sttlm_amt: Optional[AmountAndDirection27] = field(
        default=None,
        metadata={
            "name": "SttlmAmt",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class SupplementaryDataEnvelope1:
    cnts: Optional[SupplementaryDataContents1] = field(
        default=None,
        metadata={
            "name": "Cnts",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class MarketIdentification20:
    tp: MarketType8Choice = field(
        metadata={
            "name": "Tp",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class Price4:
    val: PriceRateOrAmountChoice = field(
        metadata={
            "name": "Val",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class SecurityIdentification14:
    othr_id: OtherIdentification1 = field(
        metadata={
            "name": "OthrId",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class SupplementaryData1:
    plc_and_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "PlcAndNm",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "min_length": 1,
            "max_length": 350,
        },
    )
    envlp: Optional[SupplementaryDataEnvelope1] = field(
        default=None,
        metadata={
            "name": "Envlp",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class TradeLeg8:
    trad_leg_id: str = field(
        metadata={
            "name": "TradLegId",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    trad_id: str = field(
        metadata={
            "name": "TradId",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    trad_exctn_id: str = field(
        metadata={
            "name": "TradExctnId",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    trad_dt: XmlDateTime = field(
        metadata={
            "name": "TradDt",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )
    sttlm_dt: DateFormat15Choice = field(
        metadata={
            "name": "SttlmDt",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )
    fin_instrm_id: SecurityIdentification14 = field(
        metadata={
            "name": "FinInstrmId",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )
    buy_sell_ind: Side1Code = field(
        metadata={
            "name": "BuySellInd",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )
    trad_qty: FinancialInstrumentQuantity1Choice = field(
        metadata={
            "name": "TradQty",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )
    deal_pric: Price4 = field(
        metadata={
            "name": "DealPric",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )
    plc_of_trad: MarketIdentification20 = field(
        metadata={
            "name": "PlcOfTrad",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )
    plc_of_listg: MarketIdentification21 = field(
        metadata={
            "name": "PlcOfListg",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )
    trad_tp: TradeType1Code = field(
        metadata={
            "name": "TradTp",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )
    tradg_pty: PartyIdentification35Choice = field(
        metadata={
            "name": "TradgPty",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )
    trad_regn_orgn: str = field(
        metadata={
            "name": "TradRegnOrgn",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 50,
        },
    )
    tradg_cpcty: TradingCapacity5Code = field(
        default=TradingCapacity5Code.PRIN,
        metadata={
            "name": "TradgCpcty",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )
    grss_amt: Optional[AmountAndDirection21] = field(
        default=None,
        metadata={
            "name": "GrssAmt",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
        },
    )


@dataclass
class TradeLegNotificationV03:
    clr_mmb: PartyIdentification35Choice = field(
        metadata={
            "name": "ClrMmb",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )
    clr_acct: SecuritiesAccount18 = field(
        metadata={
            "name": "ClrAcct",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )
    trad_leg_dtls: TradeLeg8 = field(
        metadata={
            "name": "TradLegDtls",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )
    sttlm_dtls: Settlement1 = field(
        metadata={
            "name": "SttlmDtls",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
            "required": True,
        },
    )
    splmtry_data: List[SupplementaryData1] = field(
        default_factory=list,
        metadata={
            "name": "SplmtryData",
            "type": "Element",
            "namespace": "urn:secl.001.001.03.xsd",
        },
    )


@dataclass
class Document:
    class Meta:
        namespace = "urn:secl.001.001.03.xsd"

    trad_leg_ntfctn: TradeLegNotificationV03 = field(
        metadata={
            "name": "TradLegNtfctn",
            "type": "Element",
            "required": True,
        },
    )
