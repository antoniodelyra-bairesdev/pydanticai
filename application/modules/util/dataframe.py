from decimal import Decimal
from math import isnan
from numpy import nan


def get_str_dataframe_item(item) -> str | None:
    if isinstance(item, (int, float, Decimal)):
        if isnan(item):
            return None
    if item == "None" or item == "" or item == "nan" or item == nan:
        return None

    return str(item).strip()
