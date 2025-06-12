from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional
from xsdata.models.datatype import XmlDate, XmlDateTime

__NAMESPACE__ = "urn:SUPL.secl.001.001.03.xsd"


@dataclass
class FinancialInstrumentAttributesBvmf63:
    class Meta:
        name = "FinancialInstrumentAttributesBVMF63"

    sgmt: Optional[int] = field(
        default=None,
        metadata={
            "name": "Sgmt",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
        },
    )
    mkt: Optional[int] = field(
        default=None,
        metadata={
            "name": "Mkt",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
        },
    )
    tckr_symb: Optional[str] = field(
        default=None,
        metadata={
            "name": "TckrSymb",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    pmt_tp: Optional[int] = field(
        default=None,
        metadata={
            "name": "PmtTp",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class IdentificationSource3Choice:
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class MarketIdentification3Choice:
    mkt_idr_cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "MktIdrCd",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
            "pattern": r"[A-Z0-9]{4,4}",
        },
    )


@dataclass
class Rate2:
    rate: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Rate",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
            "total_digits": 11,
            "fraction_digits": 10,
        },
    )


@dataclass
class SecurityIdentificationBvmf21:
    class Meta:
        name = "SecurityIdentificationBVMF21"

    isin: Optional[str] = field(
        default=None,
        metadata={
            "name": "ISIN",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "pattern": r"[A-Z0-9]{12,12}",
        },
    )
    tckr_symb: Optional[str] = field(
        default=None,
        metadata={
            "name": "TckrSymb",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    selic_cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "SelicCd",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "min_length": 1,
            "max_length": 6,
        },
    )
    mtrty_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "MtrtyDt",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
        },
    )


@dataclass
class OtherIdentification1:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    tp: Optional[IdentificationSource3Choice] = field(
        default=None,
        metadata={
            "name": "Tp",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class SecurityIdentificationBvmf4:
    class Meta:
        name = "SecurityIdentificationBVMF4"

    othr_id: Optional[OtherIdentification1] = field(
        default=None,
        metadata={
            "name": "OthrId",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
        },
    )
    plc_of_listg: Optional[MarketIdentification3Choice] = field(
        default=None,
        metadata={
            "name": "PlcOfListg",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class TradeLegBvmf13:
    class Meta:
        name = "TradeLegBVMF13"

    plc_and_nm: str = field(
        init=False,
        default="//Document/TradLegNtfctn/TradLegDtls",
        metadata={
            "name": "PlcAndNm",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 350,
        },
    )
    fin_instrm_attrbts_inf: Optional[
        FinancialInstrumentAttributesBvmf63
    ] = field(
        default=None,
        metadata={
            "name": "FinInstrmAttrbtsInf",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
        },
    )
    undrlyg_scty_id: Optional[SecurityIdentificationBvmf21] = field(
        default=None,
        metadata={
            "name": "UndrlygSctyId",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
        },
    )
    undrlyg_fin_instrm_id: Optional[SecurityIdentificationBvmf4] = field(
        default=None,
        metadata={
            "name": "UndrlygFinInstrmId",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
        },
    )
    trad_rate: Optional[Rate2] = field(
        default=None,
        metadata={
            "name": "TradRate",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
        },
    )
    slf_allcn_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "slfAllcnInd",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
        },
    )
    frnt_fmly_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "FrntFmlyId",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 71,
        },
    )
    offerng_pty_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OfferngPtyId",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "min_length": 1,
            "max_length": 35,
        },
    )
    trad_leg_sts_cd: Optional[int] = field(
        default=None,
        metadata={
            "name": "TradLegStsCd",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
        },
    )
    canc_trad_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "CancTradId",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "min_length": 1,
            "max_length": 35,
        },
    )
    addtl_inf: Optional[str] = field(
        default=None,
        metadata={
            "name": "AddtlInf",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "min_length": 1,
            "max_length": 80,
        },
    )
    mtchd_oprn_idr: Optional[str] = field(
        default=None,
        metadata={
            "name": "MtchdOprnIdr",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "min_length": 1,
            "max_length": 35,
        },
    )
    tradr_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "TradrId",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "min_length": 1,
            "max_length": 50,
        },
    )
    opn_fld: List[str] = field(
        default_factory=list,
        metadata={
            "name": "OpnFld",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "max_occurs": 4,
            "min_length": 1,
            "max_length": 20,
        },
    )
    tx_dt_tm: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "TxDtTm",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
        },
    )
    instrm_rstrctn_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "InstrmRstrctnInd",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
        },
    )


@dataclass
class TradeLegNotificationV03Sd:
    class Meta:
        name = "TradeLegNotificationV03SD"

    trad_leg_dtls_xtnsn: Optional[TradeLegBvmf13] = field(
        default=None,
        metadata={
            "name": "TradLegDtlsXtnsn",
            "type": "Element",
            "namespace": "urn:SUPL.secl.001.001.03.xsd",
            "required": True,
        },
    )


@dataclass
class Document:
    class Meta:
        namespace = "urn:SUPL.secl.001.001.03.xsd"

    trad_leg_ntfctn_v03_sd: Optional[TradeLegNotificationV03Sd] = field(
        default=None,
        metadata={
            "name": "TradLegNtfctnV03SD",
            "type": "Element",
            "required": True,
        },
    )
