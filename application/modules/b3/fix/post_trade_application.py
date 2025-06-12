from datetime import datetime
import logging
from random import randint
import quickfix as fix
import traceback
import config.database as db

from config.environment import fix_config
from typing import Any

from .base_application import BaseFIXApplicationSingleton

from modules.auth.service import AuthServiceFactory
from modules.b3.schema import (
    EnvioAlocacoesPostTrade,
    RelatorioVoicePostTradeSchema,
    RejeicaoVoicePostTradeSchema,
)
from modules.b3.service import B3ServiceFactory
from modules.queue.service import QueueService
from modules.util.fix import (
    fix_XMLContentLen,
    header_field_value,
    field_value,
    fix_MessageID,
    fix_XMLContent,
)

from generated.bvmf_234_01 import Document as BVMF_234_01
from xsdata.formats.dataclass.parsers import XmlParser
from xml.etree import ElementTree


class PostTradeApplicationSingleton(BaseFIXApplicationSingleton):
    """[B]³ Post Trade FIX Application"""

    @classmethod
    def get_application(cls) -> "PostTradeApplicationSingleton":
        if cls.application != None:
            app: Any = cls.application
            return app
        settings = fix_config("POST_TRADE")
        fix_settings = fix.SessionSettings(settings.config_path, True)
        fix_store_factory = fix.PostgreSQLStoreFactory(fix_settings)
        fix_log_factory = fix.PostgreSQLLogFactory(fix_settings)
        cls.application = PostTradeApplicationSingleton("POST_TRADE")
        cls.initiator = fix.SocketInitiator(
            cls.application, fix_store_factory, fix_settings, fix_log_factory
        )
        return cls.application

    def onLogon(self, sessionID: fix.SessionID):
        super().onLogon(sessionID)

        async def executar():
            async with db.get_session(db.engine) as session, session.begin():
                authsvc = AuthServiceFactory.criarService(session)
                usuario = await authsvc.usuario_a_partir_de_email(
                    "_post_trade@icatuvanguarda.com.br"
                )
                if not usuario:
                    return
                service = B3ServiceFactory.criarService(session)
                await service.enviar_alocacoes_nao_transmitidas(usuario)

        qs = QueueService()
        qs.enqueue(executar())

    def onMessage(self, message: fix.Message):
        tipo_mensagem = header_field_value(message, fix.MsgType())
        if tipo_mensagem != fix.MsgType_XMLnonFIX:
            return
        tipo_mensagem_xml = field_value(message, fix_MessageID())
        handlers = {"bvmf.234.01": self.relatorio_alocacoes}
        if tipo_mensagem_xml in handlers:
            handlers[tipo_mensagem_xml](message)

    def relatorio_alocacoes(self, message: fix.Message):
        try:
            xml = field_value(message, fix_XMLContent())
            documento = ElementTree.fromstring(xml).find(
                "{urn:bvmf.234.01.xsd}Document"
            )
            if documento == None:
                return
            corpo = ElementTree.tostring(documento, encoding="unicode")
            objeto = XmlParser().from_string(corpo, BVMF_234_01)

            relatorio = RelatorioVoicePostTradeSchema.from_xsdata(objeto)
            rejeicao = RejeicaoVoicePostTradeSchema.from_xsdata(objeto)

            infos = relatorio if relatorio else rejeicao
            if not infos:
                return

            async def executar(
                infos: RelatorioVoicePostTradeSchema | RejeicaoVoicePostTradeSchema,
            ):
                async with db.get_session(db.engine) as session, session.begin():
                    authsvc = AuthServiceFactory.criarService(session)
                    usuario = await authsvc.usuario_a_partir_de_email(
                        "_post_trade@icatuvanguarda.com.br"
                    )
                    if not usuario:
                        return
                    service = B3ServiceFactory.criarService(session)
                    if type(infos) == RelatorioVoicePostTradeSchema:
                        await service.atualizar_informacoes_voice_post_trade(
                            usuario, infos
                        )
                    elif type(infos) == RejeicaoVoicePostTradeSchema:
                        await service.erro_envio_alocacao_voice(infos)

            qs = QueueService()
            qs.enqueue(executar(infos))
        except Exception as exc:
            logging.error(traceback.print_exception(exc))

    def gerar_uuid_mensagem(self, horario: datetime):
        # Formato solicitado pela [B]³
        return (
            "00020967"
            + horario.strftime("%Y%m%d")
            + "".join([str(randint(0, 9)) for _ in range(19)])
        )

    def enviar_alocacoes(self, informacoes_envio: EnvioAlocacoesPostTrade):
        msg = fix.Message()
        hdr: fix.Header = msg.getHeader()
        hdr.setField(fix.MsgType("n"))
        hdr.setField(fix.DeliverToSubID("B3"))

        uuid_msg = self.gerar_uuid_mensagem(informacoes_envio.horario)

        msg.setField(fix.ClOrdID(uuid_msg))
        # Campo fix.TransactTime, do tipo fix.UtcTimeStampField. O quickfix não consegue processar
        # os dados corretamente então precisamos informá-los manualmente.
        msg.setField(
            fix.StringField(
                60,
                informacoes_envio.horario.strftime("%Y%m%d-%H:%M:%S.")
                + str(int(informacoes_envio.horario.microsecond / 1000)).rjust(3, "0"),
            )
        )

        # Precisamos utilizar desta forma em vez de instanciar um grupo de repetição fix.NoPartyIds.
        # Como é uma mensagem customizada da [B]³, fora do padrão do QuickFIX, temos que criar o
        # grupo e configurá-lo na mão desta forma.

        # Confesso que não gastei mais tempo do que já gastei para explorar mais a fundo.

        # Precisamos do ID do grupo de repetição: NoPartyIds;
        # Precisamos do ID do campo delimitador;
        # Um campo delimitador dentro de um grupo de repetição é o que aparece PRIMEIRO no grupo:
        # - Neste caso, é o campo PartyIDSource

        # O valor passado para esse campo será descartado, estamos interessados somente no valor da tag
        group_tag: int = fix.NoPartyIDs(1).getTag()
        # O valor passado para esse campo será descartado, estamos interessados somente no valor da tag
        delimiter_tag: int = fix.PartyIDSource("0").getTag()

        group = fix.Group(group_tag, delimiter_tag)
        group.setField(fix.PartyIDSource(fix.PartyIDSource_PROPRIETARY))
        group.setField(fix.PartyID("20967"))
        group.setField(fix.PartyRole(fix.PartyRole_CLIENT_ID))
        msg.addGroup(group)

        mensagem_xml = informacoes_envio.to_xml_str(uuid_msg)

        msg.setField(fix_XMLContentLen(str(len(mensagem_xml))))
        msg.setField(fix_XMLContent(mensagem_xml))
        msg.setField(fix_MessageID("bvmf.233.01"))

        if not self.session:
            return

        fix.Session.sendToTarget(msg, self.session)

        return uuid_msg, mensagem_xml
