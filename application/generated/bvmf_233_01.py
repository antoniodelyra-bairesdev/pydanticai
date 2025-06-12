from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from xsdata.models.datatype import XmlDate

__NAMESPACE__ = "urn:bvmf.233.01.xsd"


@dataclass
class AllocationBvmf24:
    class Meta:
        name = "AllocationBVMF24"

    fnl_allcn_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "FnlAllcnInd",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )
    allcn_req_tp: Optional[int] = field(
        default=None,
        metadata={
            "name": "AllcnReqTp",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )
    opn_fld: List[str] = field(
        default_factory=list,
        metadata={
            "name": "OpnFld",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "max_occurs": 4,
            "min_length": 1,
            "max_length": 20,
        },
    )


@dataclass
class BlockedAssetBvmf1:
    class Meta:
        name = "BlockedAssetBVMF1"

    blckd_asst_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "BlckdAsstInd",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
        },
    )
    cetipnb: Optional[str] = field(
        default=None,
        metadata={
            "name": "CETIPNb",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "min_length": 1,
            "max_length": 64,
        },
    )


@dataclass
class Cbiobvmf1:
    class Meta:
        name = "CBIOBVMF1"

    buyr_tp_ind: Optional[int] = field(
        default=None,
        metadata={
            "name": "BuyrTpInd",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
        },
    )
    addtl_desc: Optional[str] = field(
        default=None,
        metadata={
            "name": "AddtlDesc",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "min_length": 1,
            "max_length": 128,
        },
    )


@dataclass
class DateAndDateTimeChoice:
    dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "Dt",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )


@dataclass
class FinancialInstrumentQuantity1Choice:
    unit: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Unit",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
            "total_digits": 18,
            "fraction_digits": 17,
        },
    )


@dataclass
class GenericIdentification1:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
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
            "namespace": "urn:bvmf.233.01.xsd",
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
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class GenericIdentificationBvmf10:
    class Meta:
        name = "GenericIdentificationBVMF10"

    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
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
            "namespace": "urn:bvmf.233.01.xsd",
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
            "namespace": "urn:bvmf.233.01.xsd",
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
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class TechnicalReserveBvmf1:
    class Meta:
        name = "TechnicalReserveBVMF1"

    tech_rsrv_ind: Optional[int] = field(
        default=None,
        metadata={
            "name": "TechRsrvInd",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
        },
    )
    oprn_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "OprnDt",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
        },
    )
    cetipnb: Optional[str] = field(
        default=None,
        metadata={
            "name": "CETIPNb",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "min_length": 1,
            "max_length": 64,
        },
    )


@dataclass
class TransactiontIdentification4:
    tx_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "TxId",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
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
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )


@dataclass
class InvestorInformationBvmf1:
    class Meta:
        name = "InvestorInformationBVMF1"

    invstr_fnl_doc_id: Optional[GenericIdentificationBvmf10] = field(
        default=None,
        metadata={
            "name": "InvstrFnlDocId",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )
    qty: Optional[FinancialInstrumentQuantity1Choice] = field(
        default=None,
        metadata={
            "name": "Qty",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )


@dataclass
class OrderBvmf14:
    class Meta:
        name = "OrderBVMF14"

    trad_dt: Optional[DateAndDateTimeChoice] = field(
        default=None,
        metadata={
            "name": "TradDt",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )
    trad_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "TradId",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
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
            "namespace": "urn:bvmf.233.01.xsd",
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
            "namespace": "urn:bvmf.233.01.xsd",
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
            "namespace": "urn:bvmf.233.01.xsd",
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
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )


@dataclass
class AllocationBvmf23:
    class Meta:
        name = "AllocationBVMF23"

    acct_id: Optional[AccountIdentification1] = field(
        default=None,
        metadata={
            "name": "AcctId",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )
    qty: Optional[FinancialInstrumentQuantity1Choice] = field(
        default=None,
        metadata={
            "name": "Qty",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )
    allcn_inf: List[InvestorInformationBvmf1] = field(
        default_factory=list,
        metadata={
            "name": "AllcnInf",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
        },
    )
    tech_rsrv_inf: Optional[TechnicalReserveBvmf1] = field(
        default=None,
        metadata={
            "name": "TechRsrvInf",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
        },
    )
    cbioinf: Optional[Cbiobvmf1] = field(
        default=None,
        metadata={
            "name": "CBIOInf",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
        },
    )
    firm_grnt_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "FirmGrntInd",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
        },
    )
    blckd_asst_inf: Optional[BlockedAssetBvmf1] = field(
        default=None,
        metadata={
            "name": "BlckdAsstInf",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
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
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )
    plc_of_listg: Optional[MarketIdentification3Choice] = field(
        default=None,
        metadata={
            "name": "PlcOfListg",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )


@dataclass
class OtcfixedIncomeAllocationInstruction:
    class Meta:
        name = "OTCFixedIncomeAllocationInstruction"

    id: Optional[TransactiontIdentification4] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )
    pty_id: Optional[PartyIdentification2Choice] = field(
        default=None,
        metadata={
            "name": "PtyId",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )
    fin_instrm_id: Optional[SecurityIdentificationBvmf4] = field(
        default=None,
        metadata={
            "name": "FinInstrmId",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )
    trad_leg_dtls: Optional[OrderBvmf14] = field(
        default=None,
        metadata={
            "name": "TradLegDtls",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )
    allcn_inf: Optional[AllocationBvmf24] = field(
        default=None,
        metadata={
            "name": "AllcnInf",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
            "required": True,
        },
    )
    allcn_dtls: List[AllocationBvmf23] = field(
        default_factory=list,
        metadata={
            "name": "AllcnDtls",
            "type": "Element",
            "namespace": "urn:bvmf.233.01.xsd",
        },
    )


@dataclass
class Document:
    class Meta:
        namespace = "urn:bvmf.233.01.xsd"

    otcfxd_incm_allcn_instr: Optional[
        OtcfixedIncomeAllocationInstruction
    ] = field(
        default=None,
        metadata={
            "name": "OTCFxdIncmAllcnInstr",
            "type": "Element",
            "required": True,
        },
    )
