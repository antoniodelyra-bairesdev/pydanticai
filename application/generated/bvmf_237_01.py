from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

__NAMESPACE__ = "urn:bvmf.237.01.xsd"


class AffirmationStatus1Code(Enum):
    AFFI = "AFFI"
    NAFI = "NAFI"


@dataclass
class GenericIdentification1:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
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
            "namespace": "urn:bvmf.237.01.xsd",
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
            "namespace": "urn:bvmf.237.01.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


class Side3Code(Enum):
    BUYI = "BUYI"
    SELL = "SELL"


@dataclass
class SimpleIdentificationInformation:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
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
            "namespace": "urn:bvmf.237.01.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class AccountIdentification1:
    prtry: Optional[SimpleIdentificationInformation] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
            "required": True,
        },
    )


@dataclass
class AffirmationStatus7Choice:
    cd: Optional[AffirmationStatus1Code] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
            "required": True,
        },
    )


@dataclass
class OrderBvmf47:
    class Meta:
        name = "OrderBVMF47"

    trad_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "TradId",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    sd: Optional[Side3Code] = field(
        default=None,
        metadata={
            "name": "Sd",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
            "required": True,
        },
    )


@dataclass
class PartyIdentification2Choice:
    prtry_id: Optional[GenericIdentification1] = field(
        default=None,
        metadata={
            "name": "PrtryId",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
            "required": True,
        },
    )


@dataclass
class EarlySettlementDetailsBvmf20:
    class Meta:
        name = "EarlySettlementDetailsBVMF20"

    acct_id: Optional[AccountIdentification1] = field(
        default=None,
        metadata={
            "name": "AcctId",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
            "required": True,
        },
    )
    brkr_dealr_otcreq_tp: Optional[int] = field(
        default=None,
        metadata={
            "name": "BrkrDealrOTCReqTp",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
            "required": True,
        },
    )
    conf_req_tp: Optional[int] = field(
        default=None,
        metadata={
            "name": "ConfReqTp",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
            "required": True,
        },
    )


@dataclass
class StatusAndReason10:
    affirm_sts: Optional[AffirmationStatus7Choice] = field(
        default=None,
        metadata={
            "name": "AffirmSts",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
            "required": True,
        },
    )
    addtl_rsn_inf: Optional[str] = field(
        default=None,
        metadata={
            "name": "AddtlRsnInf",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
            "min_length": 1,
            "max_length": 210,
        },
    )


@dataclass
class OtcfixedIncomeBrokerDealerStatusAdvice:
    class Meta:
        name = "OTCFixedIncomeBrokerDealerStatusAdvice"

    id: Optional[TransactiontIdentification4] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
            "required": True,
        },
    )
    pty_id: Optional[PartyIdentification2Choice] = field(
        default=None,
        metadata={
            "name": "PtyId",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
            "required": True,
        },
    )
    brkr_dealr_inf: Optional[EarlySettlementDetailsBvmf20] = field(
        default=None,
        metadata={
            "name": "BrkrDealrInf",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
            "required": True,
        },
    )
    trad_leg_dtls: List[OrderBvmf47] = field(
        default_factory=list,
        metadata={
            "name": "TradLegDtls",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
            "min_occurs": 1,
            "max_occurs": 2,
        },
    )
    brkr_dealr_sts: Optional[StatusAndReason10] = field(
        default=None,
        metadata={
            "name": "BrkrDealrSts",
            "type": "Element",
            "namespace": "urn:bvmf.237.01.xsd",
            "required": True,
        },
    )


@dataclass
class Document:
    class Meta:
        namespace = "urn:bvmf.237.01.xsd"

    otcfxd_incm_brkr_dealr_sts_advc: Optional[
        OtcfixedIncomeBrokerDealerStatusAdvice
    ] = field(
        default=None,
        metadata={
            "name": "OTCFxdIncmBrkrDealrStsAdvc",
            "type": "Element",
            "required": True,
        },
    )
