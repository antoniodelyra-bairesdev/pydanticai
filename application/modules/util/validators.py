import json

from datetime import date
from http import HTTPStatus
from http.client import HTTPException
from typing import Annotated
from pydantic.functional_validators import AfterValidator

from fastapi import Query, Depends
from .queries import OrderingType


def date_interval(inicio: Annotated[date, Query()], fim: Annotated[date, Query()]):
    if inicio > fim:
        raise HTTPException(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "Data de início não pode ser maior que a data de fim",
        )
    return (inicio, fim)


def optional_date_interval(
    inicio: Annotated[date | None, Query()] = None,
    fim: Annotated[date | None, Query()] = None,
):
    if (not inicio and fim) or (inicio and not fim):
        raise HTTPException(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "Você precisa informar o intervalo de busca ou nenhum intervalo",
        )
    elif inicio and fim:
        return date_interval(inicio, fim)

    return None


OptionalDateInterval = Annotated[
    tuple[date, date] | None, Depends(optional_date_interval)
]

DateInterval = Annotated[tuple[date, date], Depends(date_interval)]


def get_ordering(serialized: str) -> list[tuple[str, OrderingType]]:
    if not serialized:
        return []
    dados_ordenacao: list[tuple[str, OrderingType]] = []
    try:
        ordering = json.loads(serialized)
    except:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "Formato inválido de ordenação")
    for sort in ordering:
        if "colId" not in sort:
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                "O nome da propriedade é obrigatório em todas as ordenações",
            )
        if "sort" not in sort:
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                "A propriedade de ordenação é obrigatória",
            )
        order = sort["sort"]
        if order not in {"asc", "desc"}:
            raise HTTPException(
                HTTPStatus.BAD_REQUEST, "Tipo de ordenação inválida: " + order
            )
        dados_ordenacao.append((sort["colId"], order))

    return dados_ordenacao


def get_filtering(serialized: str) -> dict[str, tuple[str, list[str]]]:
    if not serialized:
        return {}

    possible_statements = {"blank", "notBlank"}
    possible_with_string = {
        "equals",
        "greaterThan",
        "greaterThanOrEqual",
        "lessThan",
        "lessThanOrEqual",
        "notEqual",
        "contains",
        "notContains",
        "startsWith",
        "endsWith",
    }
    possible_with_list = {"inRange", "notInSet", "set"}

    dados_filtragem: dict[str, tuple[str, list[str]]] = {}
    try:
        filtering = json.loads(serialized)
    except:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "Formato inválido de filtros")
    for column in filtering:
        operation = filtering[column]
        if type(operation) == str:
            if operation in possible_statements:
                dados_filtragem[column] = (operation, [])
                continue
            else:
                raise HTTPException(
                    HTTPStatus.BAD_REQUEST, "Operação inválida: " + operation
                )
        skip_column = False
        for possible_string in possible_with_string:
            if possible_string not in operation:
                continue
            value = operation[possible_string]
            if type(value) != str:
                raise HTTPException(
                    HTTPStatus.BAD_REQUEST,
                    "O valor informado precisa ser uma string",
                )
            dados_filtragem[column] = (possible_string, [value])
            skip_column = True
            break
        if skip_column:
            continue
        for possible_list in possible_with_list:
            if possible_list not in operation:
                continue
            values = operation[possible_list]
            if type(values) != list:
                raise HTTPException(
                    HTTPStatus.BAD_REQUEST,
                    "O valor informado precisa ser um array",
                )
            if possible_list == "inRange" and len(values) != 2:
                raise HTTPException(
                    HTTPStatus.BAD_REQUEST,
                    f"Um intervalo precisa de exatos dois valores, {len(values)} foram fornecidos",
                )
            for value in values:
                if type(value) != str:
                    raise HTTPException(
                        HTTPStatus.BAD_REQUEST,
                        "Todos os valores da lista precisam ser strings",
                    )
            dados_filtragem[column] = (possible_list, values)
            skip_column = True
            break
        if skip_column:
            continue
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            "Operação inválida: " + ", ".join(list(operation.keys())),
        )
    return dados_filtragem
