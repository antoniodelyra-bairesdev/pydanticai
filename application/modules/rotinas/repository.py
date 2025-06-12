from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, insert

from .model import AtualizacaoRotina, CURVA_DI


@dataclass
class RotinaRepository:
    db: AsyncSession

    async def ultima_atualizacao(
        self, id_rotina: int, data: date
    ) -> AtualizacaoRotina | None:
        result = await self.db.execute(
            select(AtualizacaoRotina).where(
                AtualizacaoRotina.id_rotina == id_rotina, AtualizacaoRotina.data == data
            )
        )
        return result.scalars().one_or_none()

    async def atualizar_rotina(
        self, id_rotina: int, data: date, *, commit: bool
    ):
        rotina = {
            "id_rotina": id_rotina,
            "data": data,
            "atualizacao": datetime.today(),
        }
        await self.db.execute(
            delete(AtualizacaoRotina).where(
                AtualizacaoRotina.id_rotina == id_rotina, AtualizacaoRotina.data == data
            )
        )
        await self.db.execute(insert(AtualizacaoRotina).values([rotina]))
        if commit:
            await self.db.commit()
        return self.db
