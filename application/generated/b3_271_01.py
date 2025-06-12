from dataclasses import dataclass, field
from xsdata.models.datatype import XmlDate

__NAMESPACE__ = "urn:b3.271.01 -.xsd"


@dataclass
class DateFormat15Choice:
    dt: XmlDate = field(
        metadata={
            "name": "Dt",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
        },
    )


@dataclass
class GenericIdentification1:
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    issr: str = field(
        metadata={
            "name": "Issr",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    schme_nm: str = field(
        metadata={
            "name": "SchmeNm",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
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
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class MarketIdentification3Choice:
    mkt_idr_cd: str = field(
        metadata={
            "name": "MktIdrCd",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
            "pattern": r"[A-Z0-9]{4,4}",
        },
    )


@dataclass
class SimpleIdentificationInformation:
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class AccountIdentification1:
    prtry: SimpleIdentificationInformation = field(
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
        },
    )


@dataclass
class OtherIdentification1:
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    tp: IdentificationSource3Choice = field(
        metadata={
            "name": "Tp",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
        },
    )


@dataclass
class PartyIdentification1Choice:
    prtry_id: GenericIdentification1 = field(
        metadata={
            "name": "PrtryId",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
        },
    )


@dataclass
class TradeLegBvmf20:
    class Meta:
        name = "TradeLegBVMF20"

    trad_id: str = field(
        metadata={
            "name": "TradId",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    trad_dt: DateFormat15Choice = field(
        metadata={
            "name": "TradDt",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
        },
    )
    otcsd: int = field(
        metadata={
            "name": "OTCSd",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
        },
    )


@dataclass
class AllocationBvmf46:
    class Meta:
        name = "AllocationBVMF46"

    no_me_ctrl_nb: int = field(
        metadata={
            "name": "NoMeCtrlNb",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
        },
    )
    acct_id: AccountIdentification1 = field(
        metadata={
            "name": "AcctId",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
        },
    )


@dataclass
class SecurityIdentificationBvmf4:
    class Meta:
        name = "SecurityIdentificationBVMF4"

    othr_id: OtherIdentification1 = field(
        metadata={
            "name": "OthrId",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
        },
    )
    plc_of_listg: MarketIdentification3Choice = field(
        metadata={
            "name": "PlcOfListg",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
        },
    )


@dataclass
class OtcfixedIncomeRelocationInstruction:
    class Meta:
        name = "OTCFixedIncomeRelocationInstruction"

    pty_id: PartyIdentification1Choice = field(
        metadata={
            "name": "PtyId",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
        },
    )
    fin_instrm_id: SecurityIdentificationBvmf4 = field(
        metadata={
            "name": "FinInstrmId",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
        },
    )
    undrlyg_fin_instrm_id: SecurityIdentificationBvmf4 = field(
        metadata={
            "name": "UndrlygFinInstrmId",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
        },
    )
    trad_leg_dtls: TradeLegBvmf20 = field(
        metadata={
            "name": "TradLegDtls",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
        },
    )
    allcn_dtls: AllocationBvmf46 = field(
        metadata={
            "name": "AllcnDtls",
            "type": "Element",
            "namespace": "urn:b3.271.01 -.xsd",
            "required": True,
        },
    )


@dataclass
class Document:
    class Meta:
        namespace = "urn:b3.271.01 -.xsd"

    otcfxd_incm_rlcn_instr: OtcfixedIncomeRelocationInstruction = field(
        metadata={
            "name": "OTCFxdIncmRlcnInstr",
            "type": "Element",
            "required": True,
        },
    )
