from typing import Any
from unittest import IsolatedAsyncioTestCase

from httpx import AsyncClient, Response as HTTPXResponse
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession


import config.database
from main import app
from modules.auth.model import Dispositivo, Usuario, Funcao, usuarios_funcoes_table
from modules.util.orm import model_to_dict
from testes.mock.auth import fake_device, fake_user


class BaseTesteIntegracao(IsolatedAsyncioTestCase):
    client: AsyncClient
    db: AsyncSession

    user: Usuario
    device: Dispositivo

    async def asyncSetUp(self):
        if not config.database._test_connection:
            config.database._test_connection = await config.database.engine.connect()

        self.db = config.database.get_session(config.database.engine)

        self.user = fake_user()
        self.device = fake_device(self.user)

        async with self.db.begin_nested():
            d_user = model_to_dict(self.user)
            d_device = model_to_dict(self.device)

            await self.db.execute(insert(Usuario).values(d_user))
            await self.db.execute(insert(Dispositivo).values(d_device))

        self.client = AsyncClient(app=app, base_url="http://localhost:8000")

    async def asyncTearDown(self):
        await self.db.close()
        if config.database._test_connection:
            await config.database._test_connection.close()
            config.database._test_connection = None

    async def funcoes_usuario(self):
        results = await self.db.execute(select(Funcao))
        return {result.nome: result for result in results.scalars().all()}

    async def adicionar_funcao_usuario(self, funcao: Funcao):
        await self.db.execute(
            insert(usuarios_funcoes_table).values(
                {"usuario_id": self.user.id, "funcao_id": funcao.id}
            )
        )

    async def get(
        self, path: str, *, autenticado: bool = True, **kwargs
    ) -> HTTPXResponse:
        return await self.client.get(
            path,
            headers={"x-user-token": self.device.token} if autenticado else None,
            **kwargs
        )

    async def post(
        self, path: str, body: Any | None = None, *, autenticado: bool = True, **kwargs
    ) -> HTTPXResponse:
        return await self.client.post(
            path,
            json=body,
            headers={"x-user-token": self.device.token} if autenticado else None,
            **kwargs
        )

    async def put(
        self, path: str, body: Any | None = None, *, autenticado: bool = True, **kwargs
    ) -> HTTPXResponse:
        return await self.client.put(
            path,
            json=body,
            headers={"x-user-token": self.device.token} if autenticado else None,
            **kwargs
        )

    async def delete(
        self, path: str, *, autenticado: bool = True, **kwargs
    ) -> HTTPXResponse:
        return await self.client.delete(
            path,
            headers={"x-user-token": self.device.token} if autenticado else None,
            **kwargs
        )
