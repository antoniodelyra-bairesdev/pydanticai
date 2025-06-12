from typing import ClassVar, Literal
import quickfix as fix
import logging

from config.environment import fix_config, SessaoFIXType

from modules.queue.service import QueueService
from modules.util.fix import log_msg


class BaseFIXApplicationSingleton(fix.Application):
    """FIX Application"""

    session_type: SessaoFIXType
    session: fix.SessionID | None = None
    application: ClassVar["BaseFIXApplicationSingleton | None"] = None
    initiator: fix.Initiator
    reset_seq_num_flag: None | Literal["Y", "N"]

    @classmethod
    def get_application(cls):
        raise NotImplementedError(
            "Você deve implementar a regra de implementação da singleton!"
        )

    def __init__(
        self,
        tipo_sessao: SessaoFIXType,
        reset_seq_num_flag: None | Literal["Y", "N"] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.session_type = tipo_sessao
        self.reset_seq_num_flag = reset_seq_num_flag

    def onCreate(self, sessionID: fix.SessionID):
        logging.info(
            f"{self.__class__.__name__} onCreate : Session (%s)" % sessionID.toString()
        )
        return

    def onLogon(self, sessionID: fix.SessionID):
        self.session = sessionID
        logging.info(
            f"{self.__class__.__name__} Successful Logon to session '%s'."
            % sessionID.toString()
        )
        return

    def onLogout(self, sessionID: fix.SessionID):
        self.session = None
        logging.info(
            f"{self.__class__.__name__} Session (%s) logout !" % sessionID.toString()
        )
        return

    def toAdmin(self, message: fix.Message, _: fix.SessionID):
        header: fix.Header = message.getHeader()
        field: fix.FieldBase = header.getField(fix.MsgType())
        if field.getString() == fix.MsgType_Logon:
            settings = fix_config(self.session_type)
            message.setField(fix.Username(settings.user))
            message.setField(fix.Password(settings.password))
            if self.reset_seq_num_flag:
                message.setField(fix.ResetSeqNumFlag(self.reset_seq_num_flag == "Y"))
            logging.info(f"{self.__class__.__name__} (Admin) SENT -> [LOGIN MESSAGE]")
            return
        log_msg(message, f"{self.__class__.__name__} (Admin) SENT ->")
        return

    def fromAdmin(self, message: fix.Message, _: fix.SessionID):
        log_msg(message, f"{self.__class__.__name__} (Admin) RCVD <-")
        return

    def toApp(self, message: fix.Message, _: fix.SessionID):
        log_msg(message, f"{self.__class__.__name__} (App) SENT ->")
        return

    def fromApp(self, message: fix.Message, _: fix.SessionID):
        logging.info("MESSAGE RECEIVED AT APPLICATION LEVEL!")
        log_msg(message, f"{self.__class__.__name__} (App) RCVD <-")
        self.onMessage(message)
        return

    def onMessage(self, _: fix.Message):
        raise NotImplementedError(
            "Você deve implementar seu próprio handler onMessage!"
        )
