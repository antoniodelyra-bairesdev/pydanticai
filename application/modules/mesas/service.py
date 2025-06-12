from dataclasses import dataclass

from .repository import MesasRepository


@dataclass
class MesasService:
    mesas_repository: MesasRepository

    async def mesas(self):
        mesas = await self.mesas_repository.mesas()
        return [*mesas]
