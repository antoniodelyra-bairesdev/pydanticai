import quickfix as fix
import logging

from enum import IntEnum

from modules.util.string import __SOH__


class CustomFieldIDs(IntEnum):
    MessageID = 9225
    XMLContent = 20001
    XMLContentLen = 20002


def fix_MessageID(*args):
    return fix.StringField(CustomFieldIDs.MessageID, *args)


def fix_XMLContent(*args):
    return fix.StringField(CustomFieldIDs.XMLContent, *args)


def fix_XMLContentLen(*args):
    return fix.StringField(CustomFieldIDs.XMLContentLen, *args)


def log_msg(message: fix.Message, prefix: str = ""):
    msg = message.toString().replace(__SOH__, "|")
    logging.info(f"{prefix} {msg}")


def header_field_value(msg: fix.Message, field: fix.FieldBase):
    header: fix.Header = msg.getHeader()
    if header.isSetField(field.getField()):
        header.getField(field)
        return str(field.getString())
    else:
        return ""


def field_value(msg: fix.Message | fix.Group, field: fix.FieldBase):
    if msg.isSetField(field.getField()):
        msg.getField(field)
        return str(field.getString())
    else:
        return ""
