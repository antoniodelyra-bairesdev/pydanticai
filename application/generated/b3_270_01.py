from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from xsdata.models.datatype import XmlDate

__NAMESPACE__ = "urn:b3.270.01 -.xsd"


class AffirmationStatus1Code(Enum):
    AFFI = "AFFI"
    NAFI = "NAFI"


@dataclass
class AllocationBvmf47:
    class Meta:
        name = "AllocationBVMF47"

    no_me_ctrl_nb: Optional[int] = field(
        default=None,
        metadata={
            "name": "NoMeCtrlNb",
            "type": "Element",
            "namespace": "urn:b3.270.01 -.xsd",
            "required": True,
        },
    )


@dataclass
class DateFormat15Choice:
    dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "Dt",
            "type": "Element",
            "namespace": "urn:b3.270.01 -.xsd",
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
            "namespace": "urn:b3.270.01 -.xsd",
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
            "namespace": "urn:b3.270.01 -.xsd",
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
            "namespace": "urn:b3.270.01 -.xsd",
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
            "namespace": "urn:b3.270.01 -.xsd",
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
            "namespace": "urn:b3.270.01 -.xsd",
            "required": True,
            "pattern": r"[A-Z0-9]{4,4}",
        },
    )


@dataclass
class AffirmationStatus7Choice:
    cd: Optional[AffirmationStatus1Code] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:b3.270.01 -.xsd",
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
            "namespace": "urn:b3.270.01 -.xsd",
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
            "namespace": "urn:b3.270.01 -.xsd",
            "required": True,
        },
    )


@dataclass
class PartyIdentification1Choice:
    prtry_id: Optional[GenericIdentification1] = field(
        default=None,
        metadata={
            "name": "PrtryId",
            "type": "Element",
            "namespace": "urn:b3.270.01 -.xsd",
            "required": True,
        },
    )


@dataclass
class TradeLegBvmf20:
    class Meta:
        name = "TradeLegBVMF20"

    trad_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "TradId",
            "type": "Element",
            "namespace": "urn:b3.270.01 -.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    trad_dt: Optional[DateFormat15Choice] = field(
        default=None,
        metadata={
            "name": "TradDt",
            "type": "Element",
            "namespace": "urn:b3.270.01 -.xsd",
            "required": True,
        },
    )
    otcsd: Optional[int] = field(
        default=None,
        metadata={
            "name": "OTCSd",
            "type": "Element",
            "namespace": "urn:b3.270.01 -.xsd",
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
            "namespace": "urn:b3.270.01 -.xsd",
            "required": True,
        },
    )
    plc_of_listg: Optional[MarketIdentification3Choice] = field(
        default=None,
        metadata={
            "name": "PlcOfListg",
            "type": "Element",
            "namespace": "urn:b3.270.01 -.xsd",
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
            "namespace": "urn:b3.270.01 -.xsd",
            "required": True,
        },
    )


@dataclass
class OtcfixedIncomeAllocationAcceptanceOrRejection:
    class Meta:
        name = "OTCFixedIncomeAllocationAcceptanceOrRejection"

    ctdn_id: Optional[PartyIdentification1Choice] = field(
        default=None,
        metadata={
            "name": "CtdnId",
            "type": "Element",
            "namespace": "urn:b3.270.01 -.xsd",
            "required": True,
        },
    )
    fin_instrm_id: Optional[SecurityIdentificationBvmf4] = field(
        default=None,
        metadata={
            "name": "FinInstrmId",
            "type": "Element",
            "namespace": "urn:b3.270.01 -.xsd",
            "required": True,
        },
    )
    undrlyg_fin_instrm_id: Optional[SecurityIdentificationBvmf4] = field(
        default=None,
        metadata={
            "name": "UndrlygFinInstrmId",
            "type": "Element",
            "namespace": "urn:b3.270.01 -.xsd",
            "required": True,
        },
    )
    trad_leg_dtls: Optional[TradeLegBvmf20] = field(
        default=None,
        metadata={
            "name": "TradLegDtls",
            "type": "Element",
            "namespace": "urn:b3.270.01 -.xsd",
            "required": True,
        },
    )
    allcn_dtls: Optional[AllocationBvmf47] = field(
        default=None,
        metadata={
            "name": "AllcnDtls",
            "type": "Element",
            "namespace": "urn:b3.270.01 -.xsd",
            "required": True,
        },
    )
    allcn_req_sts: Optional[StatusAndReason10] = field(
        default=None,
        metadata={
            "name": "AllcnReqSts",
            "type": "Element",
            "namespace": "urn:b3.270.01 -.xsd",
            "required": True,
        },
    )


@dataclass
class Document:
    class Meta:
        namespace = "urn:b3.270.01 -.xsd"

    otcfxd_incm_allcn_instr: Optional[
        OtcfixedIncomeAllocationAcceptanceOrRejection
    ] = field(
        default=None,
        metadata={
            "name": "OTCFxdIncmAllcnInstr",
            "type": "Element",
            "required": True,
        },
    )
