from dataclasses import dataclass
from datetime import date
from typing import Any, Literal
from uuid import uuid4
import config.database as db
import logging
import quickfix as fix

from config.environment import fix_config
from modules.auth.service import AuthServiceFactory
from modules.queue.service import QueueService
from modules.util.fix import field_value, __SOH__, header_field_value

from .base_application import BaseFIXApplicationSingleton
from ..service import B3ServiceFactory
from ..schema import EstadoVoiceEnum, RelatorioVoicePreTradeSchema
from ..model import B3Voice


class OrderEntryApplicationSingleton(BaseFIXApplicationSingleton):
    """[B]³ Order Entry FIX Application"""

    @classmethod
    def get_application(cls) -> "OrderEntryApplicationSingleton":
        if cls.application != None:
            app: Any = cls.application
            return app
        settings = fix_config("ORDER_ENTRY")
        fix_settings = fix.SessionSettings(settings.config_path, True)
        fix_store_factory = fix.PostgreSQLStoreFactory(fix_settings)
        fix_log_factory = fix.PostgreSQLLogFactory(fix_settings)
        cls.application = OrderEntryApplicationSingleton("ORDER_ENTRY", "N")
        cls.initiator = fix.SSLSocketInitiator(
            cls.application, fix_store_factory, fix_settings, fix_log_factory
        )
        return cls.application

    def onLogon(self, sessionID: fix.SessionID):
        super().onLogon(sessionID)

        async def executar():
            async with db.get_session(db.engine) as session, session.begin():
                authsvc = AuthServiceFactory.criarService(session)
                usuario = await authsvc.usuario_a_partir_de_email(
                    "_order_entry@icatuvanguarda.com.br"
                )
                if not usuario:
                    return
                service = B3ServiceFactory.criarService(session)
                await service.enviar_decisoes_nao_transmitidas(usuario)

        qs = QueueService()
        qs.enqueue(executar())

    def onMessage(self, message: fix.Message):
        tipo_mensagem = header_field_value(message, fix.MsgType())
        handlers = {
            fix.MsgType_BusinessMessageReject: self.rejeicao_mensagem,
            fix.MsgType_ExecutionReport: self.processar_relatorio_voice,
        }
        if tipo_mensagem in handlers:
            handlers[tipo_mensagem](message)

    def rejeicao_mensagem(self, message: fix.Message):
        sequencia_fix_referente = field_value(message, fix.RefSeqNum())
        if not sequencia_fix_referente:
            return
        codigo_erro = field_value(message, fix.BusinessRejectReason())
        detalhes = field_value(message, fix.Text())

        async def executar(sequencia_fix: str, codigo: str, detalhes: str):
            async with db.get_session(db.engine) as session, session.begin():
                service = B3ServiceFactory.criarService(session)
                await service.erro_envio_decisao_voice(
                    date.today(), codigo, detalhes, sequencia_fix=int(sequencia_fix)
                )

        qs = QueueService()
        qs.enqueue(executar(sequencia_fix_referente, codigo_erro, detalhes))

    def processar_relatorio_voice(self, message: fix.Message):
        voice = RelatorioVoicePreTradeSchema.from_fix_message(message)
        if not voice:
            return
        erro = field_value(message, fix.Text())

        async def executar(
            voice: RelatorioVoicePreTradeSchema, erro: str | None = None
        ):
            async with db.get_session(db.engine) as session, session.begin():
                authsvc = AuthServiceFactory.criarService(session)
                usuario = await authsvc.usuario_a_partir_de_email(
                    "_order_entry@icatuvanguarda.com.br"
                )
                if not usuario:
                    return
                service = B3ServiceFactory.criarService(session)
                await service.atualizar_informacoes_voice_pre_trade(
                    usuario, voice, erro
                )

        qs = QueueService()
        qs.enqueue(executar(voice, erro))

    def envio_decisao_voice(
        self,
        decisao: Literal["ACATO", "REJEIÇÃO"],
        voice: B3Voice,
        motivo_rejeicao="Rejeitado via sistema.",
    ):
        msg = fix.Message()
        hdr: fix.Header = msg.getHeader()
        hdr.setField(fix.MsgType(fix.MsgType_ExecutionAcknowledgement))
        # Isso deveria estar na .env
        # #TODO para quando voltar de férias
        hdr.setField(fix.SenderSubID("13015"))  # Usuário: Alan Corrêa

        msg.setField(fix.OrderID(voice.id_ordem))
        uuid = uuid4().hex[:26]
        msg.setField(fix.SecondaryOrderID(uuid))
        msg.setField(fix.ClOrdID(voice.id_ordem_secundario))
        msg.setField(
            fix.ExecAckStatus(
                fix.ExecAckStatus_ACCEPTED
                if decisao == "ACATO"
                else fix.ExecAckStatus_DONT_KNOW  # Deveria ser fix.ExecAckStatus_REJECTED, que também é mapeado para o valor '2'
            )
        )
        msg.setField(fix.ExecID(voice.id_execucao))
        msg.setField(fix.Symbol(voice.codigo_ativo))
        msg.setField(
            fix.Side(fix.Side_BUY if voice.vanguarda_compra else fix.Side_SELL)
        )
        msg.setField(fix.OrderQty(round(float(voice.quantidade), 8)))
        if decisao == "REJEIÇÃO":
            msg.setField(fix.Text(motivo_rejeicao))

        logging.info("Buscando sessão...")

        if not self.session:
            return

        logging.info("Buscando proxima sequência...")
        sessionMngr: fix.Session = self.initiator.getSession(self.session)
        sequencia_fix = sessionMngr.getExpectedSenderNum()

        logging.info("Enviando mensagem...")
        fix.Session.sendToTarget(msg, self.session)

        @dataclass
        class DadosMensagem:
            numero_sequencia: int
            uuid: str

        return DadosMensagem(numero_sequencia=sequencia_fix, uuid=uuid)
