from dataclasses import dataclass
from datetime import datetime

from aiohttp import ClientSession
from sqlalchemy import select, insert, delete, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import contains_eager

from .model import Dispositivo, Funcao, Usuario, usuarios_funcoes_table


@dataclass
class AuthRepository:
    db: AsyncSession

    async def cargos_iguais_ou_acima(self, nome: str):
        cargo_especifico = (
            select(Funcao)
            .where(Funcao.nome == nome)
            .cte(name="role_tree", recursive=True)
        )
        cargos_acima = select(Funcao).join(
            cargo_especifico, Funcao.id == cargo_especifico.c.funcao_acima_id
        )
        recursiva = cargo_especifico.union(cargos_acima)

        results = await self.db.execute(select(recursiva))
        return [
            Funcao(id=id, nome=nome, funcao_acima_id=funcao_acima_id)
            for id, nome, funcao_acima_id in results.tuples().all()
        ]

    async def find_user_from_token(self, token: str):
        results = await self.db.execute(
            select(Usuario)
            .join(Dispositivo, isouter=True)
            .join(usuarios_funcoes_table, isouter=True)
            .join(Funcao, isouter=True)
            .options(
                contains_eager(Usuario.dispositivos), contains_eager(Usuario.funcoes)
            )
            .where(
                Dispositivo.usuario_id
                == (
                    select(Dispositivo.usuario_id)
                    .where(Dispositivo.token == token)
                    .scalar_subquery()
                )
            )
        )
        return results.scalar()

    async def find_user_from_email(self, email: str):
        results = await self.db.execute(
            select(Usuario)
            .options(selectinload(Usuario.dispositivos), selectinload(Usuario.funcoes))
            .where(Usuario.email == email)
        )
        return results.scalar()

    async def remove_device(self, token: str):
        await self.db.execute(delete(Dispositivo).where(Dispositivo.token == token))
        await self.db.commit()

    async def apagar_sessoes(self, token: str):
        await self.db.execute(
            delete(Dispositivo).where(
                Dispositivo.usuario_id
                == (
                    select(Dispositivo.usuario_id)
                    .where(Dispositivo.token == token)
                    .scalar_subquery()
                )
            )
        )
        await self.db.commit()

    async def redefinir_senha(self, email: str, senha: str):
        await self.db.execute(
            update(Usuario).where(Usuario.email == email).values(senha=senha)
        )
        await self.db.commit()

    async def save_login_credentials(
        self,
        usuario_id: int,
        agente: str,
        endereco: str,
        token: str,
        localizacao: str | None,
    ):
        result = await self.db.execute(
            insert(Dispositivo)
            .values(
                usuario_id=usuario_id,
                token=token,
                endereco=endereco,
                agente=agente,
                data_login=datetime.today(),
                ultima_atividade=datetime.today(),
                localizacao=localizacao,
            )
            .returning(
                Dispositivo.id,
                Dispositivo.endereco,
                Dispositivo.agente,
                Dispositivo.localizacao,
                Dispositivo.ultima_atividade,
                Dispositivo.data_login,
            )
        )
        await self.db.commit()
        return result.tuples().one()

    async def listar_sessoes(self, token: str):
        results = await self.db.execute(
            select(Dispositivo).where(
                Dispositivo.usuario_id
                == (
                    select(Dispositivo.usuario_id)
                    .where(Dispositivo.token == token)
                    .scalar_subquery()
                )
            )
        )
        return results.scalars().all()

    async def listar_usuarios(self):
        results = await self.db.execute(select(Usuario))
        return results.scalars().all()


@dataclass
class LocationRepository:
    db: AsyncSession

    async def from_address(self, address: str):
        async with ClientSession() as session:
            async with session.get(
                f"http://www.geoplugin.net/json.gp?ip={address}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["geoplugin_status"] == 200:
                        return f"{data['geoplugin_city']}, {data['geoplugin_regionName']} - {data['geoplugin_countryCode']}"
                    elif data["geoplugin_status"] == 206:
                        return f"{data['geoplugin_countryName']} / {data['geoplugin_continentName']}"
        return None
