from dataclasses import dataclass
from typing import Any, Generic, TypeVar
from pydantic import BaseModel as Schema


@dataclass
class Page:
    number: int
    url: str


T = TypeVar("T")


class Pagination(Generic[T], Schema):
    page: int
    pages: list[Page]
    items_per_page: int
    total_items: int
    data: T
