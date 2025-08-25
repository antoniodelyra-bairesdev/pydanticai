import asyncio
import logging
from typing import TypedDict

from _lib.DependenciasExternasClient import DependenciasExternasClient

from airflow.decorators import dag, task
from airflow.utils.dates import days_ago


# Constantes da DAG
ENDPOINT = "/leitor-documentos/limpeza"
QUERY_PARAMS = {"max_age_hours": "24"}
MAX_AGE_HOURS = 24


# Schema de saída da task
class LimpezaResult(TypedDict):
    """Schema de retorno da operação de limpeza"""
    success: bool
    removed_count: int
    message: str


@dag(
    dag_id="limpeza_leitor_documentos",
    start_date=days_ago(1),
    schedule="@daily",
    catchup=False,
    tags=["limpeza", "leitor_documentos", "dependencias_externas"],
    doc_md="""
    ### DAG de Limpeza do Leitor de Documentos

    Esta DAG realiza a limpeza automática de arquivos antigos no serviço de leitor de documentos.

    **Funcionamento:**
    - Executa diariamente às 00:00 (horário de Brasília)
    - Remove arquivos criados a mais de 24 horas
    - Faz request para o endpoint `/leitor-documentos/limpeza` da API de dependências externas

    **Parâmetros:**
    - `max_age_hours=24`: Remove arquivos com mais de 24 horas

    **Logs:**
    - Registra quantos arquivos foram removidos na operação
    """,
)
def limpeza_leitor_documentos_dag():
    @task
    def executar_limpeza_leitor_documentos() -> LimpezaResult:
        """
        Executa a limpeza de arquivos antigos no leitor de documentos.
        Remove arquivos criados a mais de 24 horas.

        Returns:
            LimpezaResult: Dicionário tipado contendo:
                - success (bool): True se a operação foi bem-sucedida
                - removed_count (int): Número de arquivos removidos
                - message (str): Mensagem descritiva do resultado

        Raises:
            Exception: Se a operação de limpeza falhar
        """
        logging.info(f"Iniciando limpeza do leitor de documentos - endpoint: {ENDPOINT}")
        logging.info(f"Parâmetros: {QUERY_PARAMS}")

        try:
            client = DependenciasExternasClient()
            response_data = asyncio.run(client.post(endpoint=ENDPOINT, query_params=QUERY_PARAMS))

            # Log da resposta estruturada
            success = response_data.get("success", False)
            message = response_data.get("message", "Resposta sem mensagem")
            removed_count = response_data.get("removed_count", 0)

            logging.info(f"Limpeza concluída - Sucesso: {success}")
            logging.info(f"Resultado: {message}")
            logging.info(f"Arquivos removidos: {removed_count}")

            if not success:
                raise Exception(f"Falha na limpeza: {message}")

            return LimpezaResult(
                success=success,
                removed_count=removed_count,
                message=message
            )

        except Exception as e:
            logging.error(f"Erro durante a limpeza do leitor de documentos: {str(e)}")
            raise

    executar_limpeza_leitor_documentos()


limpeza_leitor_documentos_dag()
