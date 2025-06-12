from dataclasses import dataclass, field
from typing import Optional
from xsdata.models.datatype import XmlDate

__NAMESPACE__ = "urn:bvmf.235.02.xsd"


@dataclass
class DateAndDateTimeChoice:
    dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "Dt",
            "type": "Element",
            "namespace": "urn:bvmf.235.02.xsd",
            "required": True,
        },
    )


@dataclass
class FinancialInstrumentAttributesBvmf32:
    class Meta:
        name = "FinancialInstrumentAttributesBVMF32"

    sgmt: Optional[int] = field(
        default=None,
        metadata={
            "name": "Sgmt",
            "type": "Element",
            "namespace": "urn:bvmf.235.02.xsd",
            "required": True,
        },
    )
    mkt: Optional[int] = field(
        default=None,
        metadata={
            "name": "Mkt",
            "type": "Element",
            "namespace": "urn:bvmf.235.02.xsd",
            "required": True,
        },
    )


@dataclass
class GenericIdentification1:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:bvmf.235.02.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    issr: Optional[str] = field(
        default=None,
        metadata={
            "name": "Issr",
            "type": "Element",
            "namespace": "urn:bvmf.235.02.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    schme_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "SchmeNm",
            "type": "Element",
            "namespace": "urn:bvmf.235.02.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class OrderBvmf46:
    class Meta:
        name = "OrderBVMF46"

    trad_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "TradId",
            "type": "Element",
            "namespace": "urn:bvmf.235.02.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class TransactiontIdentification4:
    tx_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "TxId",
            "type": "Element",
            "namespace": "urn:bvmf.235.02.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class PartyIdentification2Choice:
    prtry_id: Optional[GenericIdentification1] = field(
        default=None,
        metadata={
            "name": "PrtryId",
            "type": "Element",
            "namespace": "urn:bvmf.235.02.xsd",
            "required": True,
        },
    )


@dataclass
class OtcfixedIncomeReconciliationAllocationRequest:
    class Meta:
        name = "OTCFixedIncomeReconciliationAllocationRequest"

    id: Optional[TransactiontIdentification4] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:bvmf.235.02.xsd",
            "required": True,
        },
    )
    pty_id: Optional[PartyIdentification2Choice] = field(
        default=None,
        metadata={
            "name": "PtyId",
            "type": "Element",
            "namespace": "urn:bvmf.235.02.xsd",
        },
    )
    ctdn_id: Optional[PartyIdentification2Choice] = field(
        default=None,
        metadata={
            "name": "CtdnId",
            "type": "Element",
            "namespace": "urn:bvmf.235.02.xsd",
        },
    )
    fin_instrm_attrbts: Optional[FinancialInstrumentAttributesBvmf32] = field(
        default=None,
        metadata={
            "name": "FinInstrmAttrbts",
            "type": "Element",
            "namespace": "urn:bvmf.235.02.xsd",
            "required": True,
        },
    )
    trad_dt: Optional[DateAndDateTimeChoice] = field(
        default=None,
        metadata={
            "name": "TradDt",
            "type": "Element",
            "namespace": "urn:bvmf.235.02.xsd",
            "required": True,
        },
    )
    trad_leg_dtls: Optional[OrderBvmf46] = field(
        default=None,
        metadata={
            "name": "TradLegDtls",
            "type": "Element",
            "namespace": "urn:bvmf.235.02.xsd",
        },
    )


@dataclass
class Document:
    class Meta:
        namespace = "urn:bvmf.235.02.xsd"

    otcfxd_incm_rcncltn_allcn_req: Optional[
        OtcfixedIncomeReconciliationAllocationRequest
    ] = field(
        default=None,
        metadata={
            "name": "OTCFxdIncmRcncltnAllcnReq",
            "type": "Element",
            "required": True,
        },
    )
