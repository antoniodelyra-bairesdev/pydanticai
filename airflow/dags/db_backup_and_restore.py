from __future__ import annotations
import pendulum
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.models.param import Param


BACKUP_FILE_PATH = "/tmp/db_backup_{{ ds_nodash }}.dump"
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": pendulum.duration(minutes=5),
}

with DAG(
    dag_id="db_backup_and_restore",
    default_args=default_args,
    schedule=None,
    start_date=days_ago(1),
    catchup=False,
    tags=["db", "database", "backup", "restore", "parametrized"],
    params={
        "source_conn_id": Param(
            "api_source_db",
            type="string",
            title="Source Connection ID",
            description="Connection ID para o banco de dados source, que será a fonte (tem que ser do tipo Postgres)",
        ),
        "target_conn_id": Param(
            "api_target_db",
            type="string",
            title="Target Connection ID",
            description="Connection ID para o banco de dados target, que será restaurado (tem que ser do tipo Postgres)",
        ),
    },
    doc_md="""
    ### DAG de Backup de BD (source) e restauração em Outro BD (target)

    Esta DAG realiza as seguintes etapas:
    1.  **Backup Source DB:** Faz o backup do banco de dados da conexão de origem especificada no parâmetro `source_conn_id`.
    2.  **Restore Target DB (with --clean):** Restaura o backup no banco de dados da conexão de destino especificada no parâmetro `target_conn_id`.
        O banco de dados de destino já deve existir. A opção `--clean` do `pg_restore` tentará dropar os objetos antes de recriá-los.
    3.  **Cleanup Backup File:** Remove o arquivo de backup local.

    **Como Usar:**
    - Acione a DAG manualmente ("Trigger DAG w/ config").
    - Modifique o JSON de configuração para definir `source_conn_id` e `target_conn_id` com os IDs das conexões Airflow desejadas.

    **Importante:**
    - As conexões Airflow especificadas nos parâmetros **devem existir** e ser do tipo Postgres.
    - O banco de dados de destino **DEVE EXISTIR**.
    - O usuário da conexão de destino precisa de permissões para `DROP` e `CREATE` objetos dentro do banco de dados de destino.
    """,
) as dag:
    backup_db_command = f"""
        set -e;
        BACKUP_FILE="{BACKUP_FILE_PATH}"

        echo "Iniciando backup do banco de dados {{{{ conn[params.source_conn_id].schema }}}} (Conn ID: {{{{ params.source_conn_id }}}})...";
        # Chaves extras {{}} para que a f-string não interprete as chaves Jinja internas
        PGPASSWORD='{{{{ conn[params.source_conn_id].password }}}}' pg_dump \\
            -h {{{{ conn[params.source_conn_id].host }}}} \\
            -p {{{{ conn[params.source_conn_id].port }}}} \\
            -U {{{{ conn[params.source_conn_id].login }}}} \\
            -d {{{{ conn[params.source_conn_id].schema }}}} \\
            -Fc \\
            -f "$BACKUP_FILE"
        echo "Backup concluído: $BACKUP_FILE";
    """
    restore_db_command = f"""
        set -e;
        BACKUP_FILE="{BACKUP_FILE_PATH}"

        echo "Iniciando restauração para o banco de dados {{ conn[params.target_conn_id].schema }} (Conn ID: {{ params.target_conn_id }}) com --clean...";
        PGPASSWORD='{{{{ conn[params.target_conn_id].password }}}}' pg_restore \\
            -h {{{{ conn[params.target_conn_id].host }}}} \\
            -p {{{{ conn[params.target_conn_id].port }}}} \\
            -U {{{{ conn[params.target_conn_id].login }}}} \\
            -d {{{{ conn[params.target_conn_id].schema }}}} \\
            --clean \\
            --if-exists \\
            -1 \\
            "$BACKUP_FILE"
        echo "Restauração concluída.";
    """
    cleanup_backup_file_command = f"""
        BACKUP_FILE="{BACKUP_FILE_PATH}"

        echo "Limpando arquivo de backup: $BACKUP_FILE";
        rm -f "$BACKUP_FILE"
        echo "Limpeza concluída.";
    """

    task_backup_db = BashOperator(
        task_id="backup_source_database",
        bash_command=backup_db_command,
    )
    task_restore_db_with_clean = BashOperator(
        task_id="restore_to_target_db_with_clean",
        bash_command=restore_db_command,
    )
    task_cleanup_backup_file = BashOperator(
        task_id="cleanup_backup_file",
        bash_command=cleanup_backup_file_command,
    )

    task_backup_db >> task_restore_db_with_clean >> task_cleanup_backup_file
