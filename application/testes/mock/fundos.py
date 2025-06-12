from datetime import datetime
import re

from sqlalchemy import insert
from modules.fundos.model import (
    Fundo,
    FundoCustodiante,
    FundoSiteInstitucional,
)

from modules.util.orm import model_to_dict

from faker import Faker

from sqlalchemy.ext.asyncio.session import AsyncSession

fake = Faker(locale="pt_BR")


async def fake_fundo_custodiante(*, db: AsyncSession | None = None):
    fc = FundoCustodiante()
    fc.nome = fake.name()
    fc.nome_curto = "".join(fc.nome.split(" "))
    if db:
        fc.id = (
            (
                await db.execute(
                    insert(FundoCustodiante)
                    .values(model_to_dict(fc))
                    .returning(FundoCustodiante.id)
                )
            )
            .scalars()
            .one()
        )
    return fc


async def fake_fundo(custodiante_id: int, *, db: AsyncSession | None = None):
    f = Fundo()
    f.cnpj = re.sub(r"[^0-9]", "", fake.cnpj())
    f.nome = fake.name()
    f.apelido = fake.name()
    f.fundo_custodiante_id = custodiante_id
    f.atualizacao = datetime.now()
    if db:
        f.id = (
            (
                await db.execute(
                    insert(Fundo).values(model_to_dict(f)).returning(Fundo.id)
                )
            )
            .scalars()
            .one()
        )
    return f


async def fake_fundo_site_institucional(
    fundo_id: int, estrategia_id: int, tipo_id: int, *, db: AsyncSession | None = None
):
    f_si = FundoSiteInstitucional()
    f_si.fundo_id = fundo_id
    f_si.site_institucional_classificacao_id = estrategia_id
    f_si.site_institucional_tipo_id = tipo_id
    if db:
        f_si.id = (
            (
                await db.execute(
                    insert(FundoSiteInstitucional)
                    .values(model_to_dict(f_si))
                    .returning(FundoSiteInstitucional.id)
                )
            )
            .scalars()
            .one()
        )
    return f_si
