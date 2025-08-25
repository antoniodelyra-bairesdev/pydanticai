"""
Testes de validação básica das DAGs.
Estes são os testes mais importantes - garantem que as DAGs carregam sem erro.
"""

import pendulum
import pytest


@pytest.mark.unit
def test_all_dags_load_without_errors(dag_bag):
    """Verifica se todas as DAGs carregam sem erros de import"""
    assert len(dag_bag.import_errors) == 0, f"Erros de import encontrados: {dag_bag.import_errors}"


@pytest.mark.unit
def test_all_dags_have_required_attributes(dag_bag):
    """Verifica se todas as DAGs têm atributos obrigatórios"""
    for dag_id, dag in dag_bag.dags.items():
        # Verifica se tem start_date
        assert dag.start_date is not None, f"DAG {dag_id} não tem start_date"

        # Converte para comparar timezone-aware datetimes
        now = pendulum.now()
        if dag.start_date.tzinfo is None:
            # Se start_date é naive, assume UTC
            start_date_aware = pendulum.instance(dag.start_date, tz="UTC")
        else:
            start_date_aware = pendulum.instance(dag.start_date)

        # Verifica se start_date não é no futuro distante (erro comum)
        assert start_date_aware <= now, f"DAG {dag_id} tem start_date no futuro"

        # Verifica se tem pelo menos uma task
        assert len(dag.tasks) > 0, f"DAG {dag_id} não tem tasks"


@pytest.mark.unit
@pytest.mark.dag
def test_limpeza_leitor_documentos_dag_structure(dag_bag):
    """Testa especificamente a DAG de limpeza"""
    # Usa diretamente o dicionário de DAGs ao invés de get_dag()
    dag = dag_bag.dags.get("limpeza_leitor_documentos")

    # Verifica se a DAG existe
    assert dag is not None, "DAG limpeza_leitor_documentos não encontrada"

    # Verifica configurações básicas
    assert dag.schedule_interval == "@daily"
    assert dag.catchup is False
    assert "limpeza" in dag.tags
    assert "leitor_documentos" in dag.tags

    # Verifica se tem exatamente 1 task
    assert len(dag.tasks) == 1

    # Verifica se a task tem o nome correto
    task_ids = [task.task_id for task in dag.tasks]
    assert "executar_limpeza_leitor_documentos" in task_ids


@pytest.mark.unit
@pytest.mark.dag
def test_coleta_dags_structure(dag_bag):
    """Testa as DAGs de coleta existentes"""
    # Testa DAG de histórico completo
    dag_historico = dag_bag.dags.get("coleta_cotacoes_indices_historico_completo_dag")
    assert dag_historico is not None
    assert dag_historico.catchup is False
    assert "coleta" in dag_historico.tags

    # Testa DAG de últimas cotações
    dag_ultimas = dag_bag.dags.get("coleta_indices_ultimas_cotacoes")
    assert dag_ultimas is not None
    assert dag_ultimas.catchup is False
    assert "coleta" in dag_ultimas.tags


@pytest.mark.unit
@pytest.mark.dag
def test_backup_dag_structure(dag_bag):
    """Testa a DAG de backup"""
    dag_backup = dag_bag.dags.get("db_backup_and_restore")
    assert dag_backup is not None
    assert dag_backup.schedule_interval is None  # Manual trigger
    assert "backup" in dag_backup.tags


@pytest.mark.unit
def test_all_dags_have_documentation(dag_bag):
    """Verifica se todas as DAGs têm documentação"""
    for dag_id, dag in dag_bag.dags.items():
        # Verifica se tem doc_md ou __doc__
        has_documentation = (dag.doc_md is not None and len(dag.doc_md.strip()) > 0) or (
            dag.__doc__ is not None and len(dag.__doc__.strip()) > 0
        )
        assert has_documentation, f"DAG {dag_id} não tem documentação"
