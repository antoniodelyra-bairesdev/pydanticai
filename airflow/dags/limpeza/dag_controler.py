from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.dummy_operator import DummyOperator

from datetime import datetime

from airflow.decorators import dag, task

from airflow import DAG

# Definindo a primeira DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 8, 6),
}

dag1 = DAG(
    'dag_1_trigger',
    default_args=default_args,
    schedule_interval=None,  # Essa DAG não tem agendamento, será acionada manualmente
)

start = DummyOperator(
    task_id='start',
    dag=dag1,
)

# Usando TriggerDagRunOperator para disparar a DAG 2
trigger_dag2 = TriggerDagRunOperator(
    task_id='trigger_dag',
    trigger_dag_id='limpeza_leitor_documentos',  # ID da DAG que será disparada
    dag=dag1,
)

start >> trigger_dag2
