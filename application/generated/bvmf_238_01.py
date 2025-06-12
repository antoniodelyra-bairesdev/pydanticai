from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from xsdata.models.datatype import XmlDate, XmlDateTime

__NAMESPACE__ = "urn:bvmf.238.01.xsd"


@dataclass
class AllocationBvmf27:
    class Meta:
        name = "AllocationBVMF27"

    frnt_fmly_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "FrntFmlyId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 71,
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
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    cetipnb: Optional[str] = field(
        default=None,
        metadata={
            "name": "CETIPNb",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    addtl_desc: Optional[str] = field(
        default=None,
        metadata={
            "name": "AddtlDesc",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )


class EventFrequency6Code(Enum):
    DAIL = "DAIL"
    ONDE = "ONDE"


@dataclass
class FinancialInstrumentAttributesBvmf63:
    class Meta:
        name = "FinancialInstrumentAttributesBVMF63"

    sgmt: Optional[int] = field(
        default=None,
        metadata={
            "name": "Sgmt",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    mkt: Optional[int] = field(
        default=None,
        metadata={
            "name": "Mkt",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    tckr_symb: Optional[str] = field(
        default=None,
        metadata={
            "name": "TckrSymb",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )


@dataclass
class FinancialInstrumentAttributesBvmf7:
    class Meta:
        name = "FinancialInstrumentAttributesBVMF7"

    dstrbtn_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "DstrbtnId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class GenericIdentification19:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
            "pattern": r"[A-Z0-9]{4,4}",
        },
    )


@dataclass
class PartyInformationBvmf2:
    class Meta:
        name = "PartyInformationBVMF2"

    shrt_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "ShrtNm",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 20,
        },
    )


@dataclass
class Rate2:
    rate: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Rate",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
            "total_digits": 11,
            "fraction_digits": 10,
        },
    )


@dataclass
class RestrictedBvmf2ActiveOrHistoricCurrencyAnd4DecimalAmount:
    class Meta:
        name = "RestrictedBVMF2ActiveOrHistoricCurrencyAnd4DecimalAmount"

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "total_digits": 19,
            "fraction_digits": 4,
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
class SecurityIdentificationBvmf21:
    class Meta:
        name = "SecurityIdentificationBVMF21"

    isin: Optional[str] = field(
        default=None,
        metadata={
            "name": "ISIN",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "pattern": r"[A-Z0-9]{12,12}",
        },
    )
    tckr_symb: Optional[str] = field(
        default=None,
        metadata={
            "name": "TckrSymb",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
            "min_length": 1,
            "max_length": 6,
        },
    )
    mtrty_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "MtrtyDt",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


class StatementUpdateType1Code(Enum):
    COMP = "COMP"
    DELT = "DELT"


@dataclass
class TechnicalReserveBvmf1:
    class Meta:
        name = "TechnicalReserveBVMF1"

    tech_rsrv_ind: Optional[int] = field(
        default=None,
        metadata={
            "name": "TechRsrvInd",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    oprn_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "OprnDt",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    cetipnb: Optional[str] = field(
        default=None,
        metadata={
            "name": "CETIPNb",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )


@dataclass
class AllocationBvmf31:
    class Meta:
        name = "AllocationBVMF31"

    selic_ctrl_nb: Optional[int] = field(
        default=None,
        metadata={
            "name": "SelicCtrlNb",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    brkr_dealr_selic_ctrl_nb: Optional[int] = field(
        default=None,
        metadata={
            "name": "BrkrDealrSelicCtrlNb",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    no_me_ctrl_nb: Optional[int] = field(
        default=None,
        metadata={
            "name": "NoMeCtrlNb",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    brkr_dealr_no_me_ctrl_nb: Optional[int] = field(
        default=None,
        metadata={
            "name": "BrkrDealrNoMeCtrlNb",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    qty: Optional[FinancialInstrumentQuantity1Choice] = field(
        default=None,
        metadata={
            "name": "Qty",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    sts_cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "StsCd",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 10,
        },
    )
    orgnl_no_me_ctrl_nb: Optional[int] = field(
        default=None,
        metadata={
            "name": "OrgnlNoMeCtrlNb",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    qty: Optional[FinancialInstrumentQuantity1Choice] = field(
        default=None,
        metadata={
            "name": "Qty",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )


@dataclass
class PartyIdentification10Choice:
    prtry_id: Optional[GenericIdentification19] = field(
        default=None,
        metadata={
            "name": "PrtryId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )


@dataclass
class ReportParameters1:
    frqcy: Optional[EventFrequency6Code] = field(
        default=None,
        metadata={
            "name": "Frqcy",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    rpt_nb: Optional[str] = field(
        default=None,
        metadata={
            "name": "RptNb",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "pattern": r"[0-9]{5}",
        },
    )
    rpt_dt_and_tm: Optional[DateAndDateTimeChoice] = field(
        default=None,
        metadata={
            "name": "RptDtAndTm",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    actvty_ind: bool = field(
        default=True,
        metadata={
            "name": "ActvtyInd",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    net_pos_id: str = field(
        default="XXXX",
        metadata={
            "name": "NetPosId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    upd_tp: StatementUpdateType1Code = field(
        default=StatementUpdateType1Code.COMP,
        metadata={
            "name": "UpdTp",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )


@dataclass
class TradeLegBvmf14:
    class Meta:
        name = "TradeLegBVMF14"

    trad_dt: Optional[DateFormat15Choice] = field(
        default=None,
        metadata={
            "name": "TradDt",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    sttlm_dt: Optional[DateFormat15Choice] = field(
        default=None,
        metadata={
            "name": "SttlmDt",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    trad_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "TradId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    qty: Optional[FinancialInstrumentQuantity1Choice] = field(
        default=None,
        metadata={
            "name": "Qty",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    orgnl_qty: Optional[FinancialInstrumentQuantity1Choice] = field(
        default=None,
        metadata={
            "name": "OrgnlQty",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    unit_val: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "UnitVal",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "total_digits": 19,
            "fraction_digits": 6,
        },
    )
    trad_rate: Optional[Rate2] = field(
        default=None,
        metadata={
            "name": "TradRate",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    deal_pric: Optional[
        RestrictedBvmf2ActiveOrHistoricCurrencyAnd4DecimalAmount
    ] = field(
        default=None,
        metadata={
            "name": "DealPric",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    canc_trad_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "CancTradId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "min_length": 1,
            "max_length": 35,
        },
    )
    tx_dt_tm: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "TxDtTm",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    instrm_rstrctn_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "InstrmRstrctnInd",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )


@dataclass
class AllocationBvmf25:
    class Meta:
        name = "AllocationBVMF25"

    pty_id: Optional[PartyIdentification10Choice] = field(
        default=None,
        metadata={
            "name": "PtyId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    pty_frnt_fmly_id: Optional[AllocationBvmf27] = field(
        default=None,
        metadata={
            "name": "PtyFrntFmlyId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    offerng_pty_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OfferngPtyId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class AllocationBvmf26:
    class Meta:
        name = "AllocationBVMF26"

    trad_regn_orgn: Optional[str] = field(
        default=None,
        metadata={
            "name": "TradRegnOrgn",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "min_length": 1,
            "max_length": 50,
        },
    )
    trad_exctn_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "TradExctnId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "min_length": 1,
            "max_length": 35,
        },
    )
    brkr_dealr_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "BrkrDealrId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "min_length": 1,
            "max_length": 35,
        },
    )
    slf_allcn_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "slfAllcnInd",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    trad_leg_sts_cd: Optional[int] = field(
        default=None,
        metadata={
            "name": "TradLegStsCd",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    fnl_allcn_sts: Optional[int] = field(
        default=None,
        metadata={
            "name": "FnlAllcnSts",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    cntr_pty_id: Optional[PartyIdentification10Choice] = field(
        default=None,
        metadata={
            "name": "CntrPtyId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    cntr_pty_frnt_fmly: Optional[AllocationBvmf27] = field(
        default=None,
        metadata={
            "name": "CntrPtyFrntFmly",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    offerng_cntr_pty_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OfferngCntrPtyId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "min_length": 1,
            "max_length": 35,
        },
    )
    mtchd_oprn_idr: Optional[str] = field(
        default=None,
        metadata={
            "name": "MtchdOprnIdr",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "min_length": 1,
            "max_length": 35,
        },
    )
    tradr_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "TradrId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "min_length": 1,
            "max_length": 50,
        },
    )
    opn_fld: List[str] = field(
        default_factory=list,
        metadata={
            "name": "OpnFld",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "max_occurs": 4,
            "min_length": 1,
            "max_length": 20,
        },
    )


@dataclass
class AllocationBvmf29:
    class Meta:
        name = "AllocationBVMF29"

    acct_id: Optional[AccountIdentification1] = field(
        default=None,
        metadata={
            "name": "AcctId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    qty: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Qty",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
            "total_digits": 18,
            "fraction_digits": 17,
        },
    )


@dataclass
class AllocationBvmf30:
    class Meta:
        name = "AllocationBVMF30"

    acct_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "AcctNm",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "min_length": 0,
            "max_length": 100,
        },
    )
    otcscty_acct_tp: Optional[int] = field(
        default=None,
        metadata={
            "name": "OTCSctyAcctTp",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    ctdn_id: Optional[PartyIdentification10Choice] = field(
        default=None,
        metadata={
            "name": "CtdnId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    otcctdn_id: Optional[PartyIdentification10Choice] = field(
        default=None,
        metadata={
            "name": "OTCCtdnId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    ctdn_nm: Optional[PartyInformationBvmf2] = field(
        default=None,
        metadata={
            "name": "CtdnNm",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )


@dataclass
class AllocationBvmf34:
    class Meta:
        name = "AllocationBVMF34"

    selic_ctrl_nb: Optional[int] = field(
        default=None,
        metadata={
            "name": "SelicCtrlNb",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    brkr_dealr_selic_ctrl_nb: Optional[int] = field(
        default=None,
        metadata={
            "name": "BrkrDealrSelicCtrlNb",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    no_me_ctrl_nb: Optional[int] = field(
        default=None,
        metadata={
            "name": "NoMeCtrlNb",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    brkr_dealr_no_me_ctrl_nb: Optional[int] = field(
        default=None,
        metadata={
            "name": "BrkrDealrNoMeCtrlNb",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    qty: Optional[FinancialInstrumentQuantity1Choice] = field(
        default=None,
        metadata={
            "name": "Qty",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    sts_cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "StsCd",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
            "min_length": 1,
            "max_length": 10,
        },
    )
    cntr_pty_acct: Optional[AccountIdentification1] = field(
        default=None,
        metadata={
            "name": "CntrPtyAcct",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    orgnl_no_me_ctrl_nb: Optional[int] = field(
        default=None,
        metadata={
            "name": "OrgnlNoMeCtrlNb",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
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
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    plc_of_listg: Optional[MarketIdentification3Choice] = field(
        default=None,
        metadata={
            "name": "PlcOfListg",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )


@dataclass
class AllocationBvmf28:
    class Meta:
        name = "AllocationBVMF28"

    cmon_allcn_dtls: Optional[AllocationBvmf29] = field(
        default=None,
        metadata={
            "name": "CmonAllcnDtls",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    prvd_allcn_dtls: Optional[AllocationBvmf30] = field(
        default=None,
        metadata={
            "name": "PrvdAllcnDtls",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    rcrd_dtls: List[AllocationBvmf31] = field(
        default_factory=list,
        metadata={
            "name": "RcrdDtls",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    fnl_invstr_dtls: List[InvestorInformationBvmf1] = field(
        default_factory=list,
        metadata={
            "name": "FnlInvstrDtls",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    tech_rsrv_inf: Optional[TechnicalReserveBvmf1] = field(
        default=None,
        metadata={
            "name": "TechRsrvInf",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    cbioinf: Optional[Cbiobvmf1] = field(
        default=None,
        metadata={
            "name": "CBIOInf",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    firm_grnt_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "FirmGrntInd",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    blckd_asst_inf: Optional[BlockedAssetBvmf1] = field(
        default=None,
        metadata={
            "name": "BlckdAsstInf",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )


@dataclass
class AllocationBvmf33:
    class Meta:
        name = "AllocationBVMF33"

    cmon_allcn_dtls: Optional[AllocationBvmf29] = field(
        default=None,
        metadata={
            "name": "CmonAllcnDtls",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    prvd_allcn_dtls: Optional[AllocationBvmf30] = field(
        default=None,
        metadata={
            "name": "PrvdAllcnDtls",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    fnl_invstr_dtls: List[InvestorInformationBvmf1] = field(
        default_factory=list,
        metadata={
            "name": "FnlInvstrDtls",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    firm_grnt_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "FirmGrntInd",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )


@dataclass
class OtcfixedIncomeAllocationDetailsReport:
    class Meta:
        name = "OTCFixedIncomeAllocationDetailsReport"

    rpt_params: Optional[ReportParameters1] = field(
        default=None,
        metadata={
            "name": "RptParams",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    id: Optional[TransactiontIdentification4] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    pty_id: Optional[PartyIdentification1Choice] = field(
        default=None,
        metadata={
            "name": "PtyId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    ctdn_id: Optional[PartyIdentification1Choice] = field(
        default=None,
        metadata={
            "name": "CtdnId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    fin_instrm_id: Optional[SecurityIdentificationBvmf4] = field(
        default=None,
        metadata={
            "name": "FinInstrmId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    fin_instrm_attrbts_inf: Optional[
        FinancialInstrumentAttributesBvmf63
    ] = field(
        default=None,
        metadata={
            "name": "FinInstrmAttrbtsInf",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    undrlyg_fin_instrm_id: Optional[SecurityIdentificationBvmf4] = field(
        default=None,
        metadata={
            "name": "UndrlygFinInstrmId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    undrlyg_scty_id: Optional[SecurityIdentificationBvmf21] = field(
        default=None,
        metadata={
            "name": "UndrlygSctyId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    undrlyg_fin_instrm_attrbts: Optional[
        FinancialInstrumentAttributesBvmf7
    ] = field(
        default=None,
        metadata={
            "name": "UndrlygFinInstrmAttrbts",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )
    trad_leg_dtls: Optional[TradeLegBvmf14] = field(
        default=None,
        metadata={
            "name": "TradLegDtls",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    allcn_ptcps_id: Optional[AllocationBvmf25] = field(
        default=None,
        metadata={
            "name": "AllcnPtcpsId",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    allcn_inf: Optional[AllocationBvmf26] = field(
        default=None,
        metadata={
            "name": "AllcnInf",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
            "required": True,
        },
    )
    allcn_dtls: List[AllocationBvmf28] = field(
        default_factory=list,
        metadata={
            "name": "AllcnDtls",
            "type": "Element",
            "namespace": "urn:bvmf.238.01.xsd",
        },
    )


@dataclass
class Document:
    class Meta:
        namespace = "urn:bvmf.238.01.xsd"

    otcfxd_incm_allcn_dtls_rpt: Optional[
        OtcfixedIncomeAllocationDetailsReport
    ] = field(
        default=None,
        metadata={
            "name": "OTCFxdIncmAllcnDtlsRpt",
            "type": "Element",
            "required": True,
        },
    )
