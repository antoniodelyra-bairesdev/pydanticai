from pydantic import BaseModel as Schema

from modules.caracteristicas_fundos.types import FundoInfo


class ResponseSchema(Schema):
    fundos_sem_xml: list[FundoInfo]
