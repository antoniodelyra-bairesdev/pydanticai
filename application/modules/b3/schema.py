import logging
import quickfix as fix
import quickfix44

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import IntEnum
from typing import Literal
from pydantic import BaseModel as Schema

from generated.bvmf_234_01 import Document as BVMF_234_01

from modules.util.fix import field_value
from modules.util.string import __ENTER__

from .model import B3RegistroNoMe, B3Voice, CasamentoAlocacaoB3Voice


class EstadoVoiceEnum(IntEnum):
    AGUARDANDO = 0
    ACATADO = 1
    CANCELADO = 2
    REJEITADO = 3
    ALOCADO = 4


class RelatorioVoicePreTradeSchema(Schema):
    id_ordem: str
    id_ordem_secundario: str
    id_trader: str

    id_execucao: str

    codigo_ativo: str
    vanguarda_compra: bool
    preco_unitario: Decimal
    quantidade: Decimal
    data_negociacao: date
    data_liquidacao: date
    contraparte_b3_mesa_id: int

    status: EstadoVoiceEnum

    @staticmethod
    def from_fix_message(message: fix.Message):
        id_mesa_corretora = ""
        num_dados_contraparte = field_value(message, fix.NoContraBrokers())
        if num_dados_contraparte == "1":
            infos_corretora = quickfix44.ExecutionReport.NoContraBrokers()
            message.getGroup(1, infos_corretora)
            id_mesa_corretora = field_value(infos_corretora, fix.ContraBroker())
        status = field_value(message, fix.ExecType())
        status_map = {
            # Pendente/Ação rejeitada (pode tentar novamente)
            fix.ExecType_PENDING_NEW: EstadoVoiceEnum.AGUARDANDO,
            fix.ExecType_REJECTED: EstadoVoiceEnum.AGUARDANDO,
            # Negócio fechado
            fix.ExecType_TRADE: EstadoVoiceEnum.ACATADO,
            # Estados que não permitem continuidade
            fix.ExecType_CANCELED: EstadoVoiceEnum.CANCELADO,
            fix.ExecType_EXPIRED: EstadoVoiceEnum.CANCELADO,
            fix.ExecType_DONE_FOR_DAY: EstadoVoiceEnum.CANCELADO,
            fix.ExecType_SUSPENDED: EstadoVoiceEnum.CANCELADO,
            # Envio rejeitado
            fix.ExecType_REJECTED: EstadoVoiceEnum.REJEITADO,
        }
        if status not in status_map:
            return logging.info(f"Status {status} não mapeado no voice ")
        return RelatorioVoicePreTradeSchema(
            id_ordem=field_value(message, fix.OrderID()),
            id_ordem_secundario=field_value(message, fix.ClOrdID()),
            id_trader=field_value(message, fix.RegistID())
            or field_value(message, fix.SecondaryOrderID()),
            id_execucao=field_value(message, fix.ExecID()),
            codigo_ativo=field_value(message, fix.Symbol()),
            vanguarda_compra=field_value(message, fix.Side()) == fix.Side_BUY,
            preco_unitario=Decimal(field_value(message, fix.Price()) or 0),
            quantidade=Decimal(field_value(message, fix.OrderQty()) or 0),
            data_negociacao=date.today(),
            data_liquidacao=date.today(),
            contraparte_b3_mesa_id=int(id_mesa_corretora or 0),
            status=status_map[status],
        )


class StatusRegistroNoMeEnum(IntEnum):
    Pendente_Confirmação_Custodiante = 1
    Pendente_Confirmação_Contraparte_Custodiante = 2
    Rejeitado_pelo_Custodiante = 3
    Rejeitado_pela_Contraparte_Custodiante = 4
    Confirmado_pelo_Custodiante = 5
    Disponível_para_Registro = 6
    Pendente_de_Realocação_da_Contraparte = 7
    Realocado = 8
    Pendente_de_Realocação = 9


class EnvioDecisaoPreTradeSchema(Schema):
    id: int
    erro: str | None
    enviado_em: datetime


class EnvioAlocacoesPostTradeSchema(Schema):
    id: str
    enviado_em: datetime
    erro: str | None = None
    sucesso_em: datetime | None = None


class VoiceDetalhesSchema(Schema):
    id: int
    id_ordem: str
    id_ordem_secundario: str
    id_trader: str
    id_execucao: str
    codigo_ativo: str
    id_instrumento: str | None
    id_instrumento_subjacente: str | None
    vanguarda_compra: bool
    preco_unitario: Decimal
    quantidade: Decimal
    data_negociacao: date
    data_liquidacao: date
    contraparte_b3_mesa_id: int | None
    contraparte_b3_corretora_nome: str | None
    horario_recebimento_order_entry: datetime | None
    horario_recebimento_post_trade: datetime | None
    aprovado_em: datetime | None
    cancelado_em: datetime | None
    casamento: list[int] | None
    envios_pre_trade: list[datetime]
    envios_post_trade: list[datetime]

    @staticmethod
    def from_model(voice: B3Voice):
        return VoiceDetalhesSchema(
            id=voice.id,
            id_ordem=voice.id_ordem,
            id_ordem_secundario=voice.id_ordem_secundario,
            id_trader=voice.id_trader,
            id_execucao=voice.id_execucao,
            codigo_ativo=voice.codigo_ativo,
            id_instrumento=voice.id_instrumento,
            id_instrumento_subjacente=voice.id_instrumento_subjacente,
            vanguarda_compra=voice.vanguarda_compra,
            preco_unitario=voice.preco_unitario,
            quantidade=voice.quantidade,
            data_negociacao=voice.data_negociacao,
            data_liquidacao=voice.data_liquidacao,
            contraparte_b3_mesa_id=voice.contraparte_b3_mesa_id,
            contraparte_b3_corretora_nome=voice.contraparte_b3_corretora_nome,
            horario_recebimento_order_entry=voice.horario_recebimento_order_entry,
            horario_recebimento_post_trade=voice.horario_recebimento_post_trade,
            aprovado_em=voice.aprovado_em,
            cancelado_em=voice.cancelado_em,
            casamento=(
                [pivot.alocacao_id for pivot in voice.casamento.pivot_alocacoes]
                if voice.casamento
                else None
            ),
            envios_pre_trade=[envio.enviado_em for envio in voice.envios_pre_trade],
            envios_post_trade=[envio.enviado_em for envio in voice.envios_post_trade],
        )


class VoiceSchema(Schema):
    id_trader: str
    envios_pre_trade: list[EnvioDecisaoPreTradeSchema] = []
    envios_post_trade: list[EnvioAlocacoesPostTradeSchema] = []
    horario_recebimento_post_trade: datetime | None = None

    @staticmethod
    def from_model(voice: B3Voice):
        return VoiceSchema(
            id_trader=voice.id_trader,
            horario_recebimento_post_trade=voice.horario_recebimento_post_trade,
            envios_post_trade=[
                EnvioAlocacoesPostTradeSchema(
                    id=envio.id,
                    erro=envio.detalhes_erro,
                    enviado_em=envio.enviado_em,
                    sucesso_em=envio.sucesso_em,
                )
                for envio in voice.envios_post_trade
            ],
            envios_pre_trade=[
                EnvioDecisaoPreTradeSchema(
                    id=envio.id, erro=envio.detalhes_erro, enviado_em=envio.enviado_em
                )
                for envio in voice.envios_pre_trade
            ],
        )


class CasamentoAlocacaoB3VoiceSchema(Schema):
    casado_em: datetime
    voice: VoiceSchema

    @staticmethod
    def from_model(casamento: CasamentoAlocacaoB3Voice):
        return CasamentoAlocacaoB3VoiceSchema(
            casado_em=casamento.casado_em, voice=VoiceSchema.from_model(casamento.voice)
        )


class DetalhesRegistroNoMeSchema(Schema):
    alocacao_id: int
    numero_controle: str
    data: date
    recebido_em: datetime
    posicao_custodia: bool | None = None
    posicao_custodia_em: datetime | None = None
    posicao_custodia_contraparte: bool | None = None
    posicao_custodia_contraparte_em: datetime | None = None

    @staticmethod
    def from_model(registro: B3RegistroNoMe):
        return DetalhesRegistroNoMeSchema(
            alocacao_id=registro.alocacao_id,
            numero_controle=registro.numero_controle,
            data=registro.data,
            recebido_em=registro.recebido_em,
            posicao_custodia=registro.posicao_custodia,
            posicao_custodia_em=registro.posicao_custodia_em,
            posicao_custodia_contraparte=registro.posicao_custodia_contraparte,
            posicao_custodia_contraparte_em=registro.posicao_custodia_contraparte_em,
        )


class RegistroNoMeSchema(Schema):
    numero_controle: str
    status: StatusRegistroNoMeEnum


class AlocacaoPostTradeSchema(Schema):
    cetip: str
    registro_nome: RegistroNoMeSchema | None
    quantidade: Decimal


class StatusVoicePostTradeEnum(IntEnum):
    Novo = 1
    Pendente_Alocação = 2
    Pendente_Confirmação = 3
    Pendente_Alocação_Contraparte = 4
    Pendente_Confirmação_Contraparte = 5
    Pendente_Intermediação = 6
    Alocação_completa = 7
    Cancelado = 8
    Cancelado_no_sistema_de_negociação = 9
    Expirado = 10


class RejeicaoVoicePostTradeSchema(Schema):
    id_msg: str
    id_trader: str
    detalhes_erro: str

    @staticmethod
    def from_xsdata(objeto: BVMF_234_01):
        corpo = objeto.otcfxd_incm_allcn_sts_advc
        if (
            not corpo.id
            or not corpo.id.tx_id
            or not corpo.allcn_req_sts
            or not corpo.allcn_req_sts.addtl_rsn_inf
            or corpo.allcn_req_sts.affirm_sts.cd.value != "NAFI"
        ):
            return None
        return RejeicaoVoicePostTradeSchema(
            id_msg=corpo.id.tx_id,
            id_trader=corpo.trad_leg_dtls.trad_id,
            detalhes_erro=corpo.allcn_req_sts.addtl_rsn_inf,
        )


class RelatorioVoicePostTradeSchema(Schema):
    id_trader: str

    codigo_ativo: str
    id_instrumento: str
    id_instrumento_subjacente: str | None

    vanguarda_compra: bool
    preco_unitario: Decimal
    quantidade: Decimal

    data_negociacao: date
    data_liquidacao: date

    contraparte_b3_corretora_nome: str

    alocacoes: list[AlocacaoPostTradeSchema]
    status: StatusVoicePostTradeEnum

    @staticmethod
    def from_xsdata(objeto: BVMF_234_01):
        corpo = objeto.otcfxd_incm_allcn_sts_advc
        if (
            not corpo.undrlyg_scty_id
            or not corpo.undrlyg_scty_id.tckr_symb
            or not corpo.allcn_inf
            or not corpo.allcn_inf.cntr_pty_frnt_fmly
            or not corpo.allcn_inf.trad_leg_sts_cd
            or (
                corpo.allcn_inf.trad_leg_sts_cd
                not in {status.value for status in StatusVoicePostTradeEnum}
            )
            or not corpo.trad_leg_dtls.unit_val
            or not corpo.trad_leg_dtls.qty
            or not corpo.trad_leg_dtls.sttlm_dt
        ):
            return None

        return RelatorioVoicePostTradeSchema(
            data_negociacao=corpo.trad_leg_dtls.trad_dt.dt.to_date(),
            id_trader=corpo.trad_leg_dtls.trad_id,
            codigo_ativo=corpo.undrlyg_scty_id.tckr_symb,
            id_instrumento=corpo.fin_instrm_id.othr_id.id,
            id_instrumento_subjacente=(
                corpo.undrlyg_fin_instrm_id.othr_id.id
                if corpo.undrlyg_fin_instrm_id
                else None
            ),
            vanguarda_compra=corpo.trad_leg_dtls.sd.value == "BUYI",
            contraparte_b3_corretora_nome=corpo.allcn_inf.cntr_pty_frnt_fmly.frnt_fmly_id,
            preco_unitario=corpo.trad_leg_dtls.unit_val,
            quantidade=corpo.trad_leg_dtls.qty.unit,
            data_liquidacao=corpo.trad_leg_dtls.sttlm_dt.dt.to_date(),
            status=StatusVoicePostTradeEnum(corpo.allcn_inf.trad_leg_sts_cd),
            alocacoes=[
                AlocacaoPostTradeSchema(
                    cetip=detalhe_alocacao.cmon_allcn_dtls.acct_id.prtry.id,
                    registro_nome=(
                        RegistroNoMeSchema(
                            numero_controle=str(registro.no_me_ctrl_nb),
                            status=StatusRegistroNoMeEnum(int(registro.sts_cd)),
                        )
                        if registro.no_me_ctrl_nb
                        else None
                    ),
                    quantidade=registro.qty.unit,
                )
                for detalhe_alocacao in corpo.allcn_dtls
                for registro in detalhe_alocacao.rcrd_dtls
                if int(registro.sts_cd)
                in {code.value for code in StatusRegistroNoMeEnum}
            ],
        )


@dataclass
class VoiceSimulacaoCasamento:
    id: int
    ativo: str
    lado_operacao: Literal["C", "V"]
    quantidade: Decimal
    preco: Decimal
    horario: datetime
    data_negociacao: date
    data_liquidacao: date
    corretora: str


@dataclass
class AlocacaoSimulacaoCasamento:
    id: int
    fundo_cnpj: str
    ativo: str
    lado_operacao: Literal["C", "V"]
    quantidade: Decimal
    preco: Decimal
    horario: datetime
    data_negociacao: date
    data_liquidacao: date
    corretora: str
    boleta_id: int
    voice_id: int | None = None


@dataclass
class InfosMinimasAlocacao:
    id: int
    cetip: str
    quantidade: Decimal


@dataclass
class InfosMinimasRegistroNoMe:
    numero_controle: str
    cetip: str
    quantidade: Decimal
    alocacao_id: int | None


class EnvioAlocacaoSchema(Schema):
    cetip: str
    quantidade: Decimal


class EmailVoiceSchema(Schema):
    id_trader: str
    codigo_ativo: str
    side: Literal["C", "V"]
    preco_unitario: Decimal
    quantidade: Decimal
    nome_contraparte: str

    def html(self):
        return f"""<div>
            <em>Informações do voice</em>
            <ul>
                <li>ID Trade: <b>{self.id_trader}</b></li>
                <li>Código ativo: <b>{self.codigo_ativo}</b></li>
                <li>Lado da operação: <b>{self.side}</b></li>
                <li>Preço unitário: <b>{self.preco_unitario}</b></li>
                <li>Quantidade: <b>{self.quantidade}</b></li>
                <li>Contraparte: <b>{self.nome_contraparte}</b></li>
            </ul>
        </div>"""


class EnvioAlocacoesPostTrade(Schema):
    id_instrumento: str
    data_negociacao: date
    id_trade: str
    vanguarda_compra: bool
    horario: datetime

    alocacoes: list[EnvioAlocacaoSchema]

    def to_xml_str(self, uuid: str):
        def fmt_cetip(cetip: str):
            limpa = cetip.replace(".", "").replace("-", "")
            return f"{limpa[0:5]}.{limpa[5:7]}-{limpa[7:8]}"

        return f"""<?xml version="1.0" encoding="utf-8"?>
<PayloadBVMF>
    <AppHdr xmlns="urn:iso:std:iso:20022:tech:xsd:head.001.001.01"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="urn:iso:std:iso:20022:tech:xsd:head.001.001.01 head.001.001.01.xsd">
        <BizMsgIdr>{uuid}</BizMsgIdr>
        <MsgDefIdr>bvmf.233.01</MsgDefIdr>
        <CreDt>{self.horario.isoformat()}Z</CreDt>
        <Fr>
            <OrgId>
                <Id>
                    <OrgId>
                        <Othr>
                            <Id>39-20967</Id>
                            <SchmeNm>
                                <Prtry>39</Prtry>
                            </SchmeNm>
                            <Issr>40</Issr>
                        </Othr>
                    </OrgId>
                </Id>
            </OrgId>
        </Fr>
        <To>
            <OrgId>
                <Id>
                    <OrgId>
                        <Othr>
                            <Id>B3</Id>
                            <SchmeNm>
                                <Prtry>39</Prtry>
                            </SchmeNm>
                            <Issr>40</Issr>
                        </Othr>
                    </OrgId>
                </Id>
            </OrgId>
        </To>
    </AppHdr>
    <Document xmlns="urn:bvmf.233.01.xsd"
        xsi:schemaLocation="urn:bvmf.233.01.xsd bvmf.233.01.xsd"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <OTCFxdIncmAllcnInstr>
            <Id>
                <TxId>{uuid}</TxId>
            </Id>
            <PtyId>
                <PrtryId>
                    <Id>39-20967</Id>
                    <Issr>40</Issr>
                    <SchmeNm>39</SchmeNm>
                </PrtryId>
            </PtyId>
            <FinInstrmId>
                <OthrId>
                    <Id>{self.id_instrumento}</Id>
                    <Tp>
                        <Prtry>8</Prtry>
                    </Tp>
                </OthrId>
                <PlcOfListg>
                    <MktIdrCd>BVMF</MktIdrCd>
                </PlcOfListg>
            </FinInstrmId>
            <TradLegDtls>
                <TradDt>
                    <Dt>{self.data_negociacao.strftime('%Y-%m-%d')}</Dt>
                </TradDt>
                <TradId>{self.id_trade}</TradId>
                <Sd>{'BUYI' if self.vanguarda_compra else 'SELL'}</Sd>
            </TradLegDtls>
            <AllcnInf>
                <FnlAllcnInd>true</FnlAllcnInd>
                <AllcnReqTp>1</AllcnReqTp>
            </AllcnInf>
            {__ENTER__.join([f'''
            <AllcnDtls>
                <AcctId>
                    <Prtry>
                        <Id>{fmt_cetip(quebra.cetip)}</Id>
                    </Prtry>
                </AcctId>
                <Qty>
                    <Unit>{quebra.quantidade}</Unit>
                </Qty>
            </AllcnDtls>
'''
            for quebra in self.alocacoes
            ])}
        </OTCFxdIncmAllcnInstr>
    </Document>
</PayloadBVMF>"""
