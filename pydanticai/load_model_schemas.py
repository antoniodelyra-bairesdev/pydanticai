"""
Script para carregar os modelos do ModelSchemaEnum na tabela ModelSchema.

Este script itera sobre todos os modelos definidos no ModelSchemaEnum,
gera o JSON simplificado de cada modelo usando o método .simplify(),
e insere os dados na tabela model_schema_tb.
"""

import json
import asyncio
from typing import Dict, Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

from config.database import async_session
from modules.repository import BaseRepositoryImpl
from .enum import ModelSchemaEnum
from .model import ModelSchema


async def load_model_schemas():
    """
    Carrega todos os modelos do ModelSchemaEnum na tabela ModelSchema.
    
    Para cada modelo no enum:
    1. Obtém a classe do schema
    2. Gera o JSON simplificado usando .simplify()
    3. Insere na tabela model_schema_tb
    4. Em caso de conflito (model_nm já existe), ignora a inserção
    """
    
    # Obter engine e criar sessão
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    async with engine.begin() as conn:
        # Preparar dados para inserção
        model_data = []
        
        print("Iniciando carregamento dos modelos de schema...")
        
        # Iterar sobre todos os modelos no enum
        for enum_member in ModelSchemaEnum:
            model_name = enum_member.name
            schema_class = enum_member.value
            
            try:
                # Gerar instância da classe e obter JSON simplificado
                schema_instance = schema_class
                simplified_schema = schema_instance.simplify()
                
                # Preparar dados para inserção
                model_data.append({
                    "model_nm": model_name,
                    "model_schema": simplified_schema
                })
                
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
            
            result = await conn.execute(insert_query)
            
            # Verificar quantos registros foram inseridos
            inserted_count = result.rowcount
            print(f"✓ Inseridos {inserted_count} novos modelos")
            
        except Exception as e:
            print(f"✗ Erro ao inserir dados: {str(e)}")
            raise
    
    print("\nCarregamento de modelos concluído!")


async def main():
    """
    Função principal que executa o carregamento dos modelos.
    """
    print("=== Carregador de Modelos de Schema ===")
       
    # Carregar novos modelos
    await load_model_schemas()

if __name__ == "__main__":
    asyncio.run(main())
