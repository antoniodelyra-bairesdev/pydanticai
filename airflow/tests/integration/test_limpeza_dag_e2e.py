"""
Testes de integração E2E para a DAG de limpeza
"""

import pendulum
import pytest

# Constantes para testes
EXPECTED_REMOVED_COUNT = 5


@pytest.mark.integration
class TestLimpezaDAGIntegration:
    def test_dag_structure_and_configuration(self, dag_bag):
        """Testa estrutura e configuração da DAG"""
        dag = dag_bag.dags.get("limpeza_leitor_documentos")

        # Verifica se a DAG existe
        assert dag is not None, "DAG limpeza_leitor_documentos não encontrada"

        # Verifica configurações básicas
        assert dag.schedule_interval == "@daily"
        assert dag.catchup is False
        assert "limpeza" in dag.tags
        assert "leitor_documentos" in dag.tags

        # Verifica se tem a task esperada
        task_ids = [task.task_id for task in dag.tasks]
        assert "executar_limpeza_leitor_documentos" in task_ids

        # Verifica se tem apenas uma task
        assert len(dag.tasks) == 1

    def test_task_interface_and_signature(self, dag_bag):
        """Testa interface e assinatura da task"""
        dag = dag_bag.dags.get("limpeza_leitor_documentos")
        task = dag.get_task("executar_limpeza_leitor_documentos")

        # Verifica se a task existe
        assert task is not None

        # Verifica se é uma PythonOperator
        assert hasattr(task, "python_callable")

        # Verifica se a função callable existe
        assert callable(task.python_callable)

    def test_dag_schedule_and_timing(self, dag_bag):
        """Testa configurações de schedule da DAG"""
        dag = dag_bag.dags.get("limpeza_leitor_documentos")

        # Verifica schedule interval
        assert dag.schedule_interval == "@daily"

        # Verifica que não faz catchup
        assert dag.catchup is False

        # Verifica start_date (deve ser uma data válida)
        assert dag.start_date is not None

        # Usa timezone-aware para comparação
        now = pendulum.now("UTC")
        if dag.start_date.tzinfo is None:
            # Se start_date é naive, assume UTC
            start_date_aware = pendulum.instance(dag.start_date, tz="UTC")
        else:
            start_date_aware = pendulum.instance(dag.start_date)

        assert start_date_aware <= now

    def test_dag_dependencies_and_imports(self, dag_bag):
        """Testa se todas as dependências estão disponíveis"""
        dag = dag_bag.dags.get("limpeza_leitor_documentos")
        task = dag.get_task("executar_limpeza_leitor_documentos")

        # Verifica se consegue acessar a função sem erro
        try:
            callable_func = task.python_callable
            assert callable_func is not None
        except Exception as e:
            pytest.fail(f"Erro ao acessar python_callable: {e}")

    def test_dag_documentation_and_metadata(self, dag_bag):
        """Testa documentação e metadados da DAG"""
        dag = dag_bag.dags.get("limpeza_leitor_documentos")

        # Verifica se tem documentação
        assert dag.doc_md is not None
        assert len(dag.doc_md.strip()) > 0

        # Verifica se a documentação contém informações relevantes
        doc_content = dag.doc_md.lower()
        assert "limpeza" in doc_content
        assert "leitor" in doc_content
        assert "documentos" in doc_content
