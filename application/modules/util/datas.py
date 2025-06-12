from datetime import date, datetime, timedelta
from .feriados_recorrentes import feriados

# from storage.contar_du import contar_dias
contar_dias = {}


def contar_du(data_inicial: date, data_final: date):
    di = data_inicial.strftime("%Y-%m-%d")
    df = data_final.strftime("%Y-%m-%d")
    if di in contar_dias and df in contar_dias[di]:
        return contar_dias[di][df]

    resultado = 0
    for i in range(abs(data_final - data_inicial).days):
        data = data_inicial + timedelta(days=i + 1)
        if is_dia_util(data):
            resultado += 1

    if is_dia_util(data_final):
        return resultado
    else:
        return resultado + 1


def date_to_int(data: date) -> int:
    return data.day + data.month * 100 + data.year * 10000


def is_dia_util(data: date):
    if data.weekday() > 4 or date_to_int(data) in feriados:
        return False
    else:
        return True


def get_dia_util(data):
    if is_dia_util(data):
        return data
    else:
        return somar_dia_util(data, 1)


def somar_dia_util(data, dias):
    if dias == 0:
        return data
    contagem = 0
    sinal = dias / abs(dias)
    while contagem < abs(dias):
        data = data + timedelta(days=1 * (sinal))
        if is_dia_util(data):
            contagem += 1
    return data.date() if not isinstance(data, type(date.today())) else data


def truncar(valor, decimais):
    valor = str(valor)
    if "." in valor:
        valor = valor.split(".")
        return float((f"{valor[0]}.{valor[1][:decimais]}"))
    else:
        return float(valor)


def date_to_datetime(data: date):
    return datetime(*data.today().timetuple()[:6])


def str_ymd_to_date(s: str):
    return date(*([int(frag) for frag in s.split("-")][:3]))


def get_data_inicio_coleta() -> date:
    return date(2000, 1, 3)
