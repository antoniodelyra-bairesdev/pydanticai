from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.ext.asyncio.engine import AsyncConnection, AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from config.environment import is_test, database_url
from sqlalchemy.pool.impl import NullPool

engine = create_async_engine(
    database_url(), future=True, echo=True, poolclass=NullPool if is_test() else None
)


class Model(AsyncAttrs, DeclarativeBase):
    pass


class SchemaAuth:
    __table_args__ = {"schema": "auth", "extend_existing": True}


class SchemaIcatu:
    __table_args__ = {"schema": "icatu", "extend_existing": True}


class SchemaSistema:
    __table_args__ = {"schema": "sistema", "extend_existing": True}


class SchemaSiteInstitucional:
    __table_args__ = {"schema": "site_institucional", "extend_existing": True}


class SchemaOperacoes:
    __table_args__ = {"schema": "operacoes", "extend_existing": True}


class SchemaFinanceiro:
    __table_args__ = {"schema": "financeiro", "extend_existing": True}


def make_async_session(engine: AsyncEngine):
    return async_sessionmaker(engine, expire_on_commit=False)


async_session = make_async_session(engine)


_test_connection: AsyncConnection | None = None


def _get_session(_: AsyncEngine) -> AsyncSession:
    return async_session()


def _get_session_test(engine: AsyncEngine) -> AsyncSession:
    global _test_connection
    if not _test_connection:
        raise TypeError("Conexão deve ser configurada externamente")
    return make_async_session(engine)(
        bind=_test_connection, join_transaction_mode="create_savepoint"
    )


get_session = _get_session_test if is_test() else _get_session
