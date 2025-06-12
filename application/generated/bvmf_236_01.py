from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

__NAMESPACE__ = "urn:bvmf.236.01.xsd"


@dataclass
class GenericIdentification1:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:bvmf.236.01.xsd",
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
            "namespace": "urn:bvmf.236.01.xsd",
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
            "namespace": "urn:bvmf.236.01.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class IdentificationSource3Choice:
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:bvmf.236.01.xsd",
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
            "namespace": "urn:bvmf.236.01.xsd",
            "required": True,
            "pattern": r"[A-Z0-9]{4,4}",
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
            "namespace": "urn:bvmf.236.01.xsd",
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
            "namespace": "urn:bvmf.236.01.xsd",
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
            "namespace": "urn:bvmf.236.01.xsd",
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
            "namespace": "urn:bvmf.236.01.xsd",
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
            "namespace": "urn:bvmf.236.01.xsd",
            "required": True,
        },
    )


@dataclass
class OtherIdentification1:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:bvmf.236.01.xsd",
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
            "namespace": "urn:bvmf.236.01.xsd",
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
            "namespace": "urn:bvmf.236.01.xsd",
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
            "namespace": "urn:bvmf.236.01.xsd",
            "required": True,
        },
    )
    brkr_dealr_otcreq_tp: Optional[int] = field(
        default=None,
        metadata={
            "name": "BrkrDealrOTCReqTp",
            "type": "Element",
            "namespace": "urn:bvmf.236.01.xsd",
            "required": True,
        },
    )
    conf_req_tp: Optional[int] = field(
        default=None,
        metadata={
            "name": "ConfReqTp",
            "type": "Element",
            "namespace": "urn:bvmf.236.01.xsd",
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
            "namespace": "urn:bvmf.236.01.xsd",
            "required": True,
        },
    )
    plc_of_listg: Optional[MarketIdentification3Choice] = field(
        default=None,
        metadata={
            "name": "PlcOfListg",
            "type": "Element",
            "namespace": "urn:bvmf.236.01.xsd",
            "required": True,
        },
    )


@dataclass
class OtcfixedIncomeBrokerDealerInstruction:
    class Meta:
        name = "OTCFixedIncomeBrokerDealerInstruction"

    id: Optional[TransactiontIdentification4] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:bvmf.236.01.xsd",
            "required": True,
        },
    )
    pty_id: Optional[PartyIdentification2Choice] = field(
        default=None,
        metadata={
            "name": "PtyId",
            "type": "Element",
            "namespace": "urn:bvmf.236.01.xsd",
            "required": True,
        },
    )
    brkr_dealr_inf: Optional[EarlySettlementDetailsBvmf20] = field(
        default=None,
        metadata={
            "name": "BrkrDealrInf",
            "type": "Element",
            "namespace": "urn:bvmf.236.01.xsd",
            "required": True,
        },
    )
    trad_leg_dtls: List[OrderBvmf47] = field(
        default_factory=list,
        metadata={
            "name": "TradLegDtls",
            "type": "Element",
            "namespace": "urn:bvmf.236.01.xsd",
            "min_occurs": 1,
            "max_occurs": 2,
        },
    )
    fin_instrm_id: Optional[SecurityIdentificationBvmf4] = field(
        default=None,
        metadata={
            "name": "FinInstrmId",
            "type": "Element",
            "namespace": "urn:bvmf.236.01.xsd",
            "required": True,
        },
    )


@dataclass
class Document:
    class Meta:
        namespace = "urn:bvmf.236.01.xsd"

    otcfxd_incm_brkr_dealr_instr: Optional[
        OtcfixedIncomeBrokerDealerInstruction
    ] = field(
        default=None,
        metadata={
            "name": "OTCFxdIncmBrkrDealrInstr",
            "type": "Element",
            "required": True,
        },
    )
