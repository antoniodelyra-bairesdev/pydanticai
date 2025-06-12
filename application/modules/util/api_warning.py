from typing import Any
from pydantic import BaseModel as Schema


class APIWarning(Schema):
    tipo_id: str
    id: str
    mensagens: list[Any]

    def __eq__(self: "APIWarning", other: "APIWarning") -> bool:
        return self.tipo_id == other.tipo_id and self.id == other.id
