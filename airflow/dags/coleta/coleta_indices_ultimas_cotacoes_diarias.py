import pendulum
import logging
import asyncio

from airflow.decorators import dag, task
from _lib.feriados import get_b3_feriados
from _lib.ApiVangClient import ApiVangClient
from WorkdayHolidayTimetable import WorkdayHolidayTimetable


@dag(
    dag_id="coleta_indices_ultimas_cotacoes",
    start_date=pendulum.datetime(2025, 6, 16, tz="America/Sao_Paulo"),
    schedule=WorkdayHolidayTimetable(
        holidays=get_b3_feriados(),
        schedule_hour=8,
        schedule_minute=30,
        timezone_str="America/Sao_Paulo",
    ),
    catchup=False,
    tags=["api_vang", "coleta", "indices", "dados", "mercado"],
    doc_md="""
    ###
    Busca as cotações de todos os índices cadastrados no banco de dados.
    Roda somente em dias úteis.
    """,
)
def coleta_indices_ultimas_cotacoes():
    @task
    def insert_cotacoes_base_indices_sinteticos():
        ENDPOINT: str = "/indices/cotacoes/sinteticos/base"
        logging.info(f"Enviando POST para endpoint {ENDPOINT}")

        client = ApiVangClient()
        response_data = asyncio.run(
            client.post(
                endpoint=ENDPOINT,
            )
        )
        logging.info("Responsta:", response_data)

    @task
    def fetch_indices_ultimas_cotacoes_diarias():
        ENDPOINT = "/rotinas/indices/cotacoes/coleta/ultimos"

        client = ApiVangClient()

        logging.info(f"Enviando POST para endpoint {ENDPOINT}")
        response_data = asyncio.run(
            client.post(
                endpoint=ENDPOINT,
                json_body=None,
            )
        )
        logging.info("Resposta: ", response_data)

        return response_data["cotacoes"]

    @task
    def insert_indices_cotacoes(cotacoes):
        ENDPOINT: str = "/indices/cotacoes"
        logging.info(f"Enviando POST para endpoint {ENDPOINT}")
        logging.info("Cotações", cotacoes)

        client = ApiVangClient()
        response_data = asyncio.run(
            client.post(
                endpoint=ENDPOINT,
                json_body={"cotacoes": cotacoes},
            )
        )
        logging.info("Resposta: ", response_data)

    insert_cotacoes_base_indices_sinteticos()
    cotacoes = fetch_indices_ultimas_cotacoes_diarias()
    insert_indices_cotacoes(cotacoes)


coleta_indices_ultimas_cotacoes()
