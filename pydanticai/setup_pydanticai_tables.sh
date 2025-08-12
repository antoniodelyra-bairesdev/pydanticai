#!/bin/bash

# Script para configurar as tabelas do módulo pydanticai
# Usa as variáveis de ambiente: DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME

# Configurar variável de ambiente para senha do PostgreSQL
export PGPASSWORD=${POSTGRES_PASSWORD}

echo "Iniciando configuração das tabelas pydanticai..."

# Executar os comandos SQL no arquivo sql/pydanticai_tables.sql
echo "Executando os comandos SQL no arquivo sql/pydanticai_tables.sql..."
psql -h ${DB_HOST} -p ${DB_PORT} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f sql/pydanticai_tables.sql


echo "Configuração das tabelas pydanticai concluída!" 
