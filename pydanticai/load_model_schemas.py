"""
Script para carregar os modelos do ModelSchemaEnum na tabela ModelSchema.

Este script itera sobre todos os modelos definidos no ModelSchemaEnum,
gera o JSON simplificado de cada modelo usando o método .simplify(),
e insere os dados na tabela model_schema_tb.
"""

import asyncio

from config.database import async_session, engine
from modules.repository import BaseRepository, BaseRepositoryImpl
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from .entity import ModelSchema
from .enum_modules import ModelSchemaEnum


async def load_model_schemas(repository: BaseRepository[ModelSchema]):
    """
    Carrega todos os modelos do ModelSchemaEnum na tabela ModelSchema.

    Args:
        repository: BaseRepository para ModelSchema

    Para cada modelo no enum:
    1. Obtém a classe do schema
    2. Gera o JSON simplificado usando .simplify()
    3. Insere na tabela model_schema_tb
    4. Em caso de conflito (model_nm já existe), ignora a inserção
    """

    print("Iniciando carregamento dos modelos de schema...")

    # Preparar dados para inserção
    model_data = []

    # Iterar sobre todos os modelos no enum
    for enum_member in ModelSchemaEnum:
        model_name = enum_member.name
        schema_class = enum_member.value

        try:
            # Gerar JSON simplificado usando o método .simplify()
            simplified_schema = schema_class.simplify()

            # Preparar dados para inserção
            model_data.append({"model_nm": model_name, "model_schema": simplified_schema})

            print(f"✓ Processado: {model_name}")

        except Exception as e:
            print(f"✗ Erro ao processar {model_name}: {str(e)}")
            continue

    if not model_data:
        print("Nenhum modelo foi processado com sucesso.")
        return

    # Inserir dados na tabela
    print(f"\nInserindo {len(model_data)} modelos na tabela...")

    try:
        # Query de inserção com tratamento de conflito
        insert_query = (
            insert(ModelSchema)
            .on_conflict_do_nothing(index_elements=["model_nm"])
            .values(model_data)
        )

        result = await repository.get_db_session().execute(insert_query)

        # Verificar quantos registros foram inseridos
        inserted_count = result.rowcount
        print(f"✓ Inseridos {inserted_count} novos modelos")

        # Commit das alterações
        await repository.get_db_session().commit()

        return inserted_count

    except Exception as e:
        print(f"✗ Erro ao inserir dados: {str(e)}")
        raise

    print("\nCarregamento de modelos concluído!")


async def main():
    """
    Função principal que executa o carregamento dos modelos.
    """
    print("=== Carregador de Modelos de Schema ===")

    inserted_count = 0

    # Executar com repository configurado
    async with async_session() as session:
        repository = BaseRepositoryImpl[ModelSchema](db_session=session, model_class=ModelSchema)

        inserted_count = await load_model_schemas(repository)

    # Executar VACUUM ANALYZE completamente fora da transação
    if inserted_count is not None and inserted_count > 0:
        print("Executando VACUUM ANALYZE na tabela...")
        autocommit_engine = engine.execution_options(isolation_level="AUTOCOMMIT")
        async with async_session(bind=autocommit_engine) as session:
            await session.execute(text("VACUUM ANALYZE icatu.model_schema_tb"))
        print("✓ VACUUM ANALYZE executado com sucesso")


if __name__ == "__main__":
    asyncio.run(main())
