from dataclasses import dataclass

from sqlalchemy import select

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm.strategy_options import contains_eager

from .model import FundoMesaAssociacao, Mesa

from modules.fundos.model import Fundo, FundoDocumento


@dataclass
class MesasRepository:
    db: AsyncSession

    async def mesas(self):
        result = await self.db.execute(
            select(Mesa)
            .outerjoin(Mesa.fundos)
            .outerjoin(FundoMesaAssociacao.fundo)
            .outerjoin(Fundo.documentos)
            .outerjoin(FundoDocumento.fundo_categoria_documento)
            .outerjoin(FundoDocumento.arquivo)
            .options(
                contains_eager(Mesa.fundos),
                contains_eager(Mesa.fundos, FundoMesaAssociacao.fundo),
                contains_eager(
                    Mesa.fundos, FundoMesaAssociacao.fundo, Fundo.documentos
                ),
                contains_eager(
                    Mesa.fundos,
                    FundoMesaAssociacao.fundo,
                    Fundo.documentos,
                    FundoDocumento.fundo_categoria_documento,
                ),
                contains_eager(
                    Mesa.fundos,
                    FundoMesaAssociacao.fundo,
                    Fundo.documentos,
                    FundoDocumento.arquivo,
                ),
            )
        )
        return result.unique().scalars().all()
