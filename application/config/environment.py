from dataclasses import dataclass
from os import getenv
from typing import Literal
from urllib.parse import quote


def _required_env(field: str, description: str) -> str:
    env_value = getenv(field)
    if not env_value:
        raise Exception(
            f"ENV: Chave obrigatória {field} ({description}) não foi definida."
        )
    return env_value


@dataclass
class PGConfig:
    username: str
    password: str
    host: str
    port: str
    database: str


def pg_config(escape_password=False):
    password = _required_env("DB_PASS", "Senha de acesso ao banco de dados")
    if escape_password:
        password = quote(password).replace("%", "%%")
    return PGConfig(
        username=_required_env("DB_USER", "Nome de usuário do banco de dados"),
        password=password,
        host=_required_env("DB_HOST", "Endereço de acesso ao banco de dados"),
        port=_required_env("DB_PORT", "Porta de rede do banco de dados"),
        database=_required_env("DB_NAME", "Nome do banco de dados"),
    )


def database_url(*, escape_password=False) -> str:
    config = pg_config(escape_password)

    params = "" if not is_prod() else "?ssl=require"

    return f"postgresql+asyncpg://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}{params}"


def is_dev() -> bool:
    return getenv("ENV") == "development"


def is_test() -> bool:
    return getenv("ENV") == "test"


def is_prod() -> bool:
    return not is_dev() and not is_test()


@dataclass
class FixConfig:
    address: str
    port: str
    target_compid: str
    sender_compid: str
    config_path: str
    user: str
    password: str
    ssl: bool


SessaoFIXType = Literal["POST_TRADE", "ORDER_ENTRY"]


def fix_config(sessao: SessaoFIXType) -> FixConfig:
    return FixConfig(
        # Comum
        user=_required_env("FIX_USER", "Usuário de serviço"),
        password=_required_env("FIX_PASSWORD", "Senha do usuário de serviço"),
        # Específico por sessão
        address=_required_env(
            f"FIX_SESSAO_{sessao}_ADDRESS", "Endereço da mensageria FIX"
        ),
        port=_required_env(f"FIX_SESSAO_{sessao}_PORT", "Porta da mensageria FIX"),
        target_compid=_required_env(
            f"FIX_SESSAO_{sessao}_TARGET_COMPID", "CompID do servidor FIX (B3)"
        ),
        sender_compid=_required_env(
            f"FIX_SESSAO_{sessao}_SENDER_COMPID", "CompID do cliente FIX (API)"
        ),
        config_path=_required_env(
            f"FIX_{sessao}_CONFIG_FILE", "Arquivo de configuração FIX"
        ),
        ssl=getenv(f"FIX_SESSAO_{sessao}_SSL") == "Y",
    )
