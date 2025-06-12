from datetime import timedelta
from modules.indicadores.types import CurvaDI
from modules.indicadores.schema import CurvaDIResponse, PontoCurvaDISchema
from .datas import is_dia_util


def max_int_with_bits(bits: int):
    return 2 ** (bits - 1) - 1


SMALL_INT_MAX = max_int_with_bits(16)
INT_MAX = max_int_with_bits(32)


def acumular(
    fator: float, du_fator: int, percentual: float, juros: float, du: int, valor: float
):
    fator = (1 + ((fator ** (1 / du_fator) - 1) * (percentual / 100))) ** du
    fator = fator * ((1 + juros / 100) ** (du / 252))
    valor_calc = valor * fator

    return {
        "fator": round(fator, 8),
        "taxa": round((fator - 1), 8),
        "valor": valor,
        "valor_calc": truncar(valor_calc, 6),
        "du": du,
    }


def truncar(valor: float, decimais: int):
    valor_str = str(valor)
    if "." in valor_str:
        valor_str = valor_str.split(".")
        return float((f"{valor_str[0]}.{valor_str[1][:decimais]}"))
    else:
        return float(valor)


def curva_di_interpolada(curva: CurvaDI):
    inicio, fim = min(curva.dominio), max(curva.dominio)

    dias = [dia for dia in range(inicio, fim + 1)]
    taxas = curva.funcao(dias)

    pontos: list[PontoCurvaDISchema] = []

    dias_uteis = 0
    for i in range(len(dias)):
        dia = dias[i]
        taxa = taxas[i]
        data_ref = curva.data + timedelta(days=dia)
        if is_dia_util(data_ref):
            dias_uteis += 1
            pontos.append(
                PontoCurvaDISchema(
                    dias_corridos=dia,
                    dias_uteis=dias_uteis,
                    data_referencia=data_ref,
                    interpolado=dia not in curva.dominio,
                    taxa=round(float(taxa), 2),
                )
            )

    return CurvaDIResponse(
        dia=curva.data,
        atualizacao=curva.atualizacao,
        curva=pontos,
    )
