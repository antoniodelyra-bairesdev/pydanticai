from datetime import date
from typing import Any, Callable, List, Literal
from sqlalchemy import (
    select,
    delete,
    insert,
    BinaryExpression,
    ColumnElement,
    UnaryExpression,
    type_coerce,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import CollationClause


async def upsert(db: AsyncSession, model, *, where, values, commit: bool):
    if not isinstance(where, List):
        where = [where]
    await db.execute(delete(model).where(*where))
    await db.execute(insert(model).values(values))
    if commit:
        await db.commit()
    return db


def optional_interval(
    model, field: InstrumentedAttribute, interval: tuple[date, date] | None
):
    query = select(model)
    if interval:
        inicio, fim = interval
        query = query.where(field.between(inicio, fim))
    return query


OrderingType = Literal["asc", "desc"]
ColType = InstrumentedAttribute | CollationClause


def mapeamento_ordenacao(
    dados: list[tuple[str, OrderingType]],
    mapeamento: dict[str, ColType],
) -> list[UnaryExpression]:
    ordem_ordenacao: list[UnaryExpression] = []
    for coluna, ordenacao in dados:
        if coluna not in mapeamento:
            continue
        ordem_ordenacao.append(getattr(mapeamento[coluna], ordenacao)())
    return ordem_ordenacao


def mapeamento_filtros(
    dados: dict[str, tuple[str, list[str]]],
    mapeamento: dict[str, ColType],
    conversao: dict[str, Callable[[Any], Any]] = {},
) -> list[ColumnElement[bool] | BinaryExpression[bool]]:
    filtros: list[ColumnElement[bool] | BinaryExpression[bool]] = []
    for coluna in dados:
        if coluna not in mapeamento:
            continue
        tipo_filtro, argumentos = dados[coluna]

        coluna_orm = mapeamento[coluna]

        if tipo_filtro == "blank":
            filtros.append(coluna_orm.is_(None))
            continue
        elif tipo_filtro == "notBlank":
            filtros.append(coluna_orm.is_not(None))
            continue
        elif tipo_filtro == "set":
            filtros.append(coluna_orm.in_(argumentos))
            continue
        elif tipo_filtro == "notInSet":
            filtros.append(coluna_orm.not_in(argumentos))
            continue

        valor = (
            argumentos[0]
            if coluna not in conversao
            else conversao[coluna](argumentos[0])
        )

        if tipo_filtro == "equals":
            filtros.append(coluna_orm == valor)
        elif tipo_filtro == "notEqual":
            filtros.append(coluna_orm != valor)
        elif tipo_filtro == "greaterThan":
            filtros.append(coluna_orm > valor)
        elif tipo_filtro == "greaterThanOrEqual":
            filtros.append(coluna_orm >= valor)
        elif tipo_filtro == "lessThan":
            filtros.append(coluna_orm < valor)
        elif tipo_filtro == "lessThanOrEqual":
            filtros.append(coluna_orm <= valor)
        elif tipo_filtro == "contains":
            valor = valor.replace("\\", "\\\\").replace("%", "\\%")
            filtros.append(coluna_orm.like(f"%{valor}%"))
        elif tipo_filtro == "notContains":
            valor = valor.replace("\\", "\\\\").replace("%", "\\%")
            filtros.append(coluna_orm.not_like(f"%{valor}%"))
        elif tipo_filtro == "startsWith":
            valor = valor.replace("\\", "\\\\").replace("%", "\\%")
            filtros.append(coluna_orm.like(f"{valor}%"))
        elif tipo_filtro == "endsWith":
            valor = valor.replace("\\", "\\\\").replace("%", "\\%")
            filtros.append(coluna_orm.like(f"%{valor}"))
        elif tipo_filtro == "inRange":
            valor2 = (
                argumentos[1]
                if coluna not in conversao
                else conversao[coluna](argumentos[1])
            )
            filtros.append(coluna_orm.between(valor, valor2))
    return filtros
