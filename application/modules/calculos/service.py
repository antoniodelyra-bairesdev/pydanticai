from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from dateutil.relativedelta import relativedelta
from modules.util.feriados_financeiros_numpy import feriados

from numpy import busday_offset


class CalculosService:
    @classmethod
    def porcentagens_absolutas_para_relativas(
        cls, absolutas: list[float]
    ) -> list[date]:
        """
        Assume que a lista estará pré-ordenada. Exemplo:

        Entrada - [0.2, 0.2, 0.2, 0.2, 0.2]

        Saída - [0.2, 0.25, 0.33, 0.5, 1]
        """
        relativas = []
        total = 1.0
        for porcentagem in absolutas:
            porcentagem_relativa = porcentagem / total if total != 0 else 0
            relativas.append(porcentagem_relativa)
            total -= porcentagem
        return relativas

    @classmethod
    def porcentagens_relativas_para_absolutas(
        cls, relativas: list[float]
    ) -> list[date]:
        """
        Assume que a lista estará pré-ordenada. Exemplo:

        Entrada - [0.2, 0.25, 0.33, 0.5, 1]

        Saída - [0.2, 0.2, 0.2, 0.2, 0.2]
        """
        absolutas = []
        total = 1.0
        for porcentagem in relativas:
            porcentagem_absoluta = porcentagem * total
            absolutas.append(porcentagem_absoluta)
            total -= porcentagem_absoluta
        return absolutas

    @classmethod
    def dias_uteis_seguintes(cls, datas: list[date]) -> list[date]:
        return (
            busday_offset(datas, 0, roll="forward", holidays=feriados)  # type: ignore
            .astype(date)
            .tolist()
        )

    @classmethod
    def periodicidade_datas(
        cls, inicio_rentabilidade: date, vencimento: date, periodicidade_meses: int
    ) -> list[date]:
        if periodicidade_meses == 0:
            return cls.dias_uteis_seguintes([vencimento])
        lista_propostas = []
        proposta = vencimento
        qtd_meses = 0
        while proposta > inicio_rentabilidade:
            proposta = vencimento - relativedelta(months=abs(qtd_meses))
            lista_propostas.append(proposta)
            qtd_meses += periodicidade_meses
        return cls.dias_uteis_seguintes(lista_propostas)

    @classmethod
    def get_data_d_util_mais_x_dias(
        cls,
        x_dias: int,
        data_input: date,
        feriados,
        roll: Literal["forward", "backward"] = "forward",
    ) -> date:
        dia_posterior = data_input + relativedelta(days=x_dias)

        assert roll == "backward" or roll == "forward"

        dia_util_posterior = busday_offset(
            dates=dia_posterior,
            offsets=0,
            roll=roll,
            holidays=feriados,
        )

        return dia_util_posterior.astype(date)

    @classmethod
    def get_data_d_util_menos_x_dias(
        cls,
        x_dias: int,
        data_input: date,
        feriados,
        roll: Literal["forward", "backward"] = "backward",
    ) -> date:
        dia_anterior = data_input - relativedelta(days=x_dias)

        assert roll == "backward" or roll == "forward"

        dia_util_anterior = busday_offset(
            dates=dia_anterior,
            offsets=0,
            roll=roll,
            holidays=feriados,
        )

        return dia_util_anterior.astype(date)

    @classmethod
    def get_ultimo_dia_util_mes_anterior(cls, data_input: date) -> date:
        data_input_ano_mes_str = data_input.strftime("%Y-%m")
        data_primeiro_dia_mes_data_input = datetime.strptime(
            data_input_ano_mes_str + "-01", "%Y-%m-%d"
        ).date()

        return cls.get_data_d_util_menos_x_dias(
            x_dias=1, data_input=data_primeiro_dia_mes_data_input, feriados=feriados
        )

    @classmethod
    def get_ultimo_dia_util_ano_anterior(cls, data_input: date) -> date:
        data_input_ano_str = data_input.strftime("%Y")
        data_primeiro_dia_ano_data_input = datetime.strptime(
            data_input_ano_str + "-01-01", "%Y-%m-%d"
        ).date()

        return cls.get_data_d_util_menos_x_dias(
            x_dias=1, data_input=data_primeiro_dia_ano_data_input, feriados=feriados
        )

    @classmethod
    def get_media_ponderada(cls, valores: list[tuple]) -> Decimal:
        soma_ponderada: Decimal = Decimal(0)
        soma_pesos: Decimal = Decimal(0)

        for valor in valores:
            v: Decimal = Decimal(valor[0])
            p: Decimal = Decimal(valor[1])

            soma_ponderada += v * p
            soma_pesos += p

        return soma_ponderada / soma_pesos
