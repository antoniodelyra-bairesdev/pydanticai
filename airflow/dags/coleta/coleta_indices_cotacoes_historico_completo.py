import pendulum
import logging
import asyncio

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
from _lib.feriados import get_b3_feriados
from _lib.ApiVangClient import ApiVangClient
from WorkdayHolidayTimetable import WorkdayHolidayTimetable


@dag(
    dag_id="coleta_cotacoes_indices_historico_completo_dag",
    start_date=pendulum.datetime(2025, 6, 13, tz="America/Sao_Paulo"),
    schedule=WorkdayHolidayTimetable(
        holidays=get_b3_feriados(),
        schedule_hour=8,
        schedule_minute=0,
        timezone_str="America/Sao_Paulo",
    ),
    catchup=False,
    tags=[
        "api_vang",
        "coleta",
        "indices",
        "dados",
        "mercado",
        "completo",
        "retroativo",
    ],
    doc_md="""
    ###
    Busca todas as cotações de índices que não têm cotações.
    Roda somente em dias úteis.
    """,
)
def coleta_cotacoes_indices_historico_completo_dag():
    @task
    def fetch_indices_sem_cotacoes():
        ENDPOINT = "/indices/sem-cotacoes"
        logging.info(f"Buscando índices sem cotações no endpoint {ENDPOINT}")

        client = ApiVangClient()
        response_data = asyncio.run(client.get(endpoint=ENDPOINT))

        indices_sem_cotacoes = response_data
        if indices_sem_cotacoes:
            logging.info(f"Índices sem cotações encontrados: {indices_sem_cotacoes}")
            return [
                {
                    "indice": indice["nome"],
                    "moeda": indice["moeda"]["codigo"],
                    "fonte": indice["fonte_dados"]["fornecedor"]["nome"]
                    + indice["fonte_dados"]["nome"],
                }
                for indice in indices_sem_cotacoes
            ]

        return []

    @task.branch
    def should_proceed_with_coleta(indices):
        if indices and len(indices) > 0:
            return "insert_cotacoes_base_indices_sinteticos"
        else:
            return "skip_coleta_tasks"

    @task
    def insert_cotacoes_base_indices_sinteticos():
        ENDPOINT: str = "/indices/cotacoes/sinteticos/base"
        logging.info(f"Enviando POST para endpoint {ENDPOINT}")

        client = ApiVangClient()
        asyncio.run(
            client.post(
                endpoint=ENDPOINT,
            )
        )

    @task
    def fetch_indices_cotacoes(indices_para_coleta):
        ENDPOINT = "/rotinas/indices/cotacoes/coleta"

        client = ApiVangClient()

        logging.info(f"Enviando POST para endpoint {ENDPOINT}")
        logging.info("Body: ", indices_para_coleta)
        response_data = asyncio.run(
            client.post(
                endpoint=ENDPOINT,
                json_body=indices_para_coleta,
            )
        )
        logging.info("Resposta:", response_data)

        return response_data["cotacoes"]

    @task
    def insert_indices_cotacoes(cotacoes):
        if not cotacoes:
            logging.info("Nenhuma cotação para inserir. Finalizando.")
            return

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
        logging.info("Resposta:", response_data)

    skip_coleta_tasks = EmptyOperator(task_id="skip_coleta_tasks")

    indices_sem_cotacoes = fetch_indices_sem_cotacoes()
    branch_op = should_proceed_with_coleta(indices=indices_sem_cotacoes)

    prep_task = insert_cotacoes_base_indices_sinteticos()
    fetch_task = fetch_indices_cotacoes(indices_para_coleta=indices_sem_cotacoes)
    insert_task = insert_indices_cotacoes(cotacoes=fetch_task)

    branch_op >> prep_task
    branch_op >> skip_coleta_tasks

    prep_task >> fetch_task >> insert_task


coleta_cotacoes_indices_historico_completo_dag()
