import pandas_market_calendars as mcal
from pandas import DataFrame


def get_b3_feriados() -> list[str]:
    feriados = list(mcal.get_calendar("B3").holidays().holidays)  # type: ignore
    feriados_tratados: list[str] = [str(feriado) for feriado in feriados]

    return feriados_tratados


def get_b3_dias_funcionamento(
    data_inicio_yyyy_mm_dd: str, data_fim_yyyy_mm_dd: str
) -> DataFrame:
    """
    Retorna DataFrame do seguinte formato:
    Col1 (sem label): yyyy-mm-dd
    Col2 (market_open): yyyy-mm-dd hh:mm:ss
    Col3 (market_close): yyyy-mm-dd hh:mm:ss
    """

    return mcal.get_calendar("B3").schedule(
        start_date=data_inicio_yyyy_mm_dd, end_date=data_fim_yyyy_mm_dd
    )
