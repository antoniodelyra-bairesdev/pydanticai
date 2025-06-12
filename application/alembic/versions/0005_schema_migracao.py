"""Criação do schema 'migração' e suas respectivas tabelas

Revision ID: 0005
Revises: 0004
Create Date: 2024-01-26 13:33:06.441454
"""
from typing import Sequence

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("create schema migracao")
    op.execute(
        """
        create table migracao.administradores (
            cnpj bpchar(15) NOT NULL,
            nome text NOT NULL,
            CONSTRAINT administradores_pkey PRIMARY KEY (cnpj)
        )
        """
    )
    op.execute(
        """
        create table migracao.ativos_anbima (
            id bpchar(20) NOT NULL,
            "data" date NOT NULL,
            codigo bpchar(10) NOT NULL,
            preco float8 NULL,
            taxa float8 NULL,
            duration float8 NULL,
            atualizacao timestamp NULL DEFAULT now(),
            spread float8 NULL,
            pu_par float8 NULL,
            CONSTRAINT ativos_anbima_pkey PRIMARY KEY (id)
        )
        """
    )
    op.execute(
        "CREATE INDEX ativos_anbima_data_idx ON migracao.ativos_anbima USING btree (data);"
    )
    op.execute(
        """
        create table migracao.bancos (
            cnpj bpchar(14) NOT NULL,
            setor varchar NOT NULL,
            curso_anormal bool NOT NULL,
            rating_gestao int4 NULL,
            CONSTRAINT bancos_pkey PRIMARY KEY (cnpj)
        )
        """
    )
    op.execute(
        """
        create table migracao.calls_lf (
            "data" date NOT NULL,
            banco varchar NOT NULL,
            tipo_lf varchar NOT NULL,
            tipo_taxa varchar NOT NULL,
            indice varchar NOT NULL,
            corretora varchar NOT NULL,
            vencimento date NOT NULL,
            taxa float8 NOT NULL,
            fluxo varchar NOT NULL,
            atualizacao timestamp NULL,
            CONSTRAINT calls_lf_unique UNIQUE (data, banco, tipo_lf, tipo_taxa, indice, corretora, vencimento, fluxo)
        )
        """
    )
    op.execute(
        """
        create table migracao.carteira_bancos (
            emissor bpchar(14) NOT NULL,
            "data" date NOT NULL,
            tipo varchar NOT NULL,
            linha text NOT NULL,
            atualizacao timestamp NOT NULL DEFAULT now(),
            valor float8 NOT NULL,
            categoria varchar NOT NULL,
            CONSTRAINT carteira_bancos_pk PRIMARY KEY (emissor, data, tipo, linha, categoria)
        )
        """
    )
    op.execute(
        """
        create table migracao.compras_vendas (
            "data" date NOT NULL,
            fundo varchar NOT NULL,
            side bpchar(1) NOT NULL,
            codigo varchar NOT NULL,
            pu float8 NOT NULL,
            quantidade float8 NOT NULL,
            taxa float8 NOT NULL,
            duration float8 NOT NULL,
            spread float8 NOT NULL,
            corretagem float8 NOT NULL,
            tipo varchar NOT NULL,
            mercado varchar NOT NULL,
            contraparte int4 NOT NULL
        )
        """
    )
    op.execute(
        """
        create table migracao.corretoras (
            id serial4 NOT NULL,
            nome varchar NOT NULL,
            CONSTRAINT corretoras_pk PRIMARY KEY (id)
        )
        """
    )
    op.execute(
        """
        create table migracao.cotas_fiis (
            "data" date NOT NULL,
            fundo bpchar(10) NOT NULL,
            cota float8 NOT NULL,
            cota_ajustada float8 NOT NULL,
            proventos float8 NOT NULL,
            atualizacao timestamp NOT NULL DEFAULT now(),
            peso_ifix float8 NULL,
            CONSTRAINT cotas_fiis_pkey PRIMARY KEY (data, fundo)
        )
        """
    )
    op.execute(
        """
        create table migracao.cvm_fidcs (
            id varchar NOT NULL,
            patrimonio_liquido float8 NULL,
            direitos_creditorios float8 NULL,
            prazo_carteira json NULL,
            prazo_carteira_inadimplentes json NULL,
            pl_senior float8 NULL,
            atualizacao timestamp NULL DEFAULT now(),
            data_ref date NULL,
            fidc varchar NULL,
            CONSTRAINT cvm_fidcs_pkey PRIMARY KEY (id)
        )
        """
    )
    op.execute(
        """
        create table migracao.documentos_notion (
            id_notion varchar NOT NULL,
            properties json NOT NULL,
            blocks json NOT NULL,
            atualizacao timestamp NOT NULL,
            arquivos json NULL,
            CONSTRAINT documentos_notion_pk PRIMARY KEY (id_notion)
        )
        """
    )
    op.execute(
        """
        create table migracao.estoque_ativos (
            id bpchar(50) NOT NULL,
            "data" date NOT NULL,
            fundo bpchar(15) NOT NULL,
            ativo bpchar(15) NOT NULL,
            quantidade_disponivel float8 NOT NULL,
            quantidade_garantia float8 NOT NULL,
            fonte text NOT NULL,
            atualizacao timestamp NOT NULL,
            obs text NULL,
            preco float8 NULL,
            preco_ajustado float8 NULL,
            fic bool NULL,
            CONSTRAINT estoque_ativos_pkey PRIMARY KEY (id)
        );
        """
    )
    op.execute(
        "CREATE INDEX estoque_ativos_fundo_idx ON migracao.estoque_ativos USING btree (fundo, data, ativo);"
    )
    op.execute(
        """
        create table migracao.estoque_compromissadas (
            "data" date NOT NULL,
            fundo varchar NOT NULL,
            ativo varchar NOT NULL,
            quantidade float8 NOT NULL,
            preco float8 NOT NULL,
            atualizacao timestamp NOT NULL,
            CONSTRAINT estoque_compromissadas_pk PRIMARY KEY (data, fundo, ativo)
        )
        """
    )
    op.execute(
        """
        create table migracao.estoque_fic (
            fundo varchar NOT NULL,
            "data" date NOT NULL,
            fundo_cota varchar NOT NULL,
            quantidade float8 NOT NULL,
            atualizacao timestamp NOT NULL,
            CONSTRAINT estoque_fic_pk PRIMARY KEY (fundo, data, fundo_cota)
        )
        """
    )
    op.execute(
        """
        create table migracao.fidcs (
            codigo bpchar(15) NOT NULL,
            codigo_brit bpchar(15) NULL,
            CONSTRAINT fidcs_pkey PRIMARY KEY (codigo)
        )
        """
    )
    op.execute(
        """
        create table migracao.fluxos_teste_conversao (
            id bpchar(25) NULL,
            codigo bpchar(15) NULL,
            data_evento date NULL,
            data_pagamento date NOT NULL,
            tipo_id int4 NOT NULL,
            percentual float8 NULL,
            pu_evento float8 NULL,
            liquidacao text NULL,
            atualizacao timestamp NULL,
            cadastro bpchar(10) NULL,
            pu_calculado float8 NULL
        )
        """
    )
    op.execute(
        """
        create table migracao.setores_fii (
            id serial4 NOT NULL,
            nome text NOT NULL,
            CONSTRAINT setor_unico UNIQUE (nome),
            CONSTRAINT setores_fii_pkey PRIMARY KEY (id)
        )
        """
    )
    op.execute(
        """
        create table migracao.fundos_imobiliarios (
            codigo bpchar(10) NOT NULL,
            setor int4 NOT NULL,
            CONSTRAINT fundos_imobiliarios_pkey PRIMARY KEY (codigo),
            CONSTRAINT setor_fk FOREIGN KEY (setor) REFERENCES migracao.setores_fii(id)
        )
        """
    )
    op.execute(
        """
        create table migracao.gerencial_previo (
            codigo varchar NOT NULL,
            "data" date NOT NULL,
            preco float8 NOT NULL,
            taxa float8 NOT NULL,
            fonte varchar NOT NULL,
            atualizacao timestamp NULL DEFAULT now(),
            spread float8 NULL,
            CONSTRAINT gerencial_previo_pkey PRIMARY KEY (codigo, data, preco, taxa, fonte)
        )
        """
    )
    op.execute(
        """
        create table migracao.indicadores (
            emissor bpchar(14) NOT NULL,
            tipo varchar NOT NULL,
            periodo varchar NOT NULL,
            indicador varchar NOT NULL,
            "data" date NOT NULL,
            valor_numero float8 NULL,
            valor_texto text NULL,
            atualizacao timestamp NOT NULL,
            CONSTRAINT indicadores_pkey PRIMARY KEY (emissor, tipo, periodo, indicador, data)
        )
        """
    )
    op.execute(
        """
        create table migracao.indices_anbima (
            id bpchar(20) NOT NULL,
            indice bpchar(10) NOT NULL,
            "data" date NOT NULL,
            num_indice float8 NOT NULL,
            ret_diario float8 NULL,
            ret_mensal float8 NULL,
            ret_anual float8 NULL,
            atualizacao timestamp NOT NULL,
            CONSTRAINT indices_anbima_pkey PRIMARY KEY (id)
        )
        """
    )
    op.execute(
        """
        create table migracao.lamina_fundos (
            fundo varchar NOT NULL,
            "data" date NOT NULL,
            informacao varchar NOT NULL,
            categoria varchar NOT NULL,
            valor_texto text NULL,
            valor_numero float8 NULL,
            atualizacao timestamp NOT NULL DEFAULT now(),
            CONSTRAINT lamina_teste_pkey PRIMARY KEY (fundo, data, informacao, categoria)
        )
        """
    )
    op.execute(
        """
        create table migracao.lfs_anbima (
            banco varchar NOT NULL,
            "data" date NOT NULL,
            tipo_lf varchar NOT NULL,
            tipo_taxa varchar NOT NULL,
            duration float8 NOT NULL,
            taxa float8 NOT NULL,
            indice varchar NOT NULL,
            CONSTRAINT lfs_anbima_pk PRIMARY KEY (banco, data, tipo_lf, tipo_taxa, duration, indice)
        )
        """
    )
    op.execute(
        """
        create table migracao.ordem_funding_bancos (
            linha text NOT NULL,
	        ordem int4 NOT NULL
        )
        """
    )
    op.execute(
        """
        create table migracao.ordenacao_ratings (
            id serial4 NOT NULL,
            agencia varchar NULL,
            rating varchar NULL,
            ordenacao int4 NULL,
            CONSTRAINT ordenacao_ratings_pkey PRIMARY KEY (id)
        )
        """
    )
    op.execute(
        """
        create table migracao.patrimonio_liquido (
            id varchar NOT NULL,
            empresa_grupo varchar NOT NULL,
            data_ref date NOT NULL,
            patrimonio_liquido float8 NOT NULL,
            tipo varchar NULL,
            atualizacao timestamp NULL DEFAULT now(),
            cadastro varchar NULL,
            CONSTRAINT patrimonio_liquido_pkey PRIMARY KEY (id)
        )
        """
    )
    op.execute(
        """
        create table migracao.pnl_fundos (
            id varchar NOT NULL,
            fundo varchar NOT NULL,
            "data" date NOT NULL,
            categoria varchar NOT NULL,
            periodo varchar NOT NULL,
            valor float8 NOT NULL,
            atualizacao timestamp NOT NULL DEFAULT now(),
            CONSTRAINT pnl_fundos_pkey PRIMARY KEY (id)
        )
        """
    )
    op.execute(
        """
        create table migracao.posicao_fundos (
            id bpchar(30) NOT NULL,
            "data" date NOT NULL,
            fundo bpchar(15) NOT NULL,
            quantidade float8 NOT NULL,
            cota float8 NOT NULL,
            fonte text NOT NULL,
            atualizacao timestamp NOT NULL,
            obs text NULL,
            CONSTRAINT posicao_fundos_pkey PRIMARY KEY (id)
        )
        """
    )
    op.execute(
        """
        create table migracao.preco_ativos (
            id bpchar(50) NOT NULL,
            ativo bpchar(15) NOT NULL,
            "data" date NOT NULL,
            fonte text NOT NULL,
            preco float8 NOT NULL,
            atualizacao timestamp NOT NULL,
            obs text NULL,
            CONSTRAINT preco_ativos_pkey PRIMARY KEY (id)
        )
        """
    )
    op.execute(
        """
        create table migracao.rating_bancos (
            rating serial4 NOT NULL,
            perc_pl float8 NOT NULL,
            prazo bpchar NULL,
            CONSTRAINT rating_bancos_pk PRIMARY KEY (rating)
        )
        """
    )
    op.execute(
        """
        create table migracao.ratings (
            id varchar NOT NULL,
            codigo varchar NULL,
            "data" date NULL,
            rating_id int4 NULL,
            tipo varchar NULL,
            atualizacao timestamp NULL DEFAULT now(),
            cadastro varchar NULL,
            CONSTRAINT ratings_pkey PRIMARY KEY (id)
        )
        """
    )
    op.execute(
        """
        create table migracao.taxas_ativos (
            codigo varchar NOT NULL,
            "data" date NOT NULL,
            preco float8 NOT NULL,
            taxa float8 NOT NULL,
            duration float8 NOT NULL,
            spread float8 NULL,
            fonte varchar NOT NULL,
            atualizacao timestamp NULL DEFAULT now(),
            pu_par float8 NULL,
            CONSTRAINT taxas_ativos_pkey PRIMARY KEY (codigo, data, preco, taxa, duration, fonte)
        );
        """
    )
    op.execute(
        "CREATE INDEX taxas_ativos_data_idx ON migracao.taxas_ativos USING btree (data);"
    )


def downgrade() -> None:
    op.execute("drop table migracao.taxas_ativos")
    op.execute("drop table migracao.ratings")
    op.execute("drop table migracao.rating_bancos")
    op.execute("drop table migracao.preco_ativos")
    op.execute("drop table migracao.posicao_fundos")
    op.execute("drop table migracao.pnl_fundos")
    op.execute("drop table migracao.patrimonio_liquido")
    op.execute("drop table migracao.ordenacao_ratings")
    op.execute("drop table migracao.ordem_funding_bancos")
    op.execute("drop table migracao.lfs_anbima")
    op.execute("drop table migracao.lamina_fundos")
    op.execute("drop table migracao.indices_anbima")
    op.execute("drop table migracao.indicadores")
    op.execute("drop table migracao.gerencial_previo")
    op.execute("drop table migracao.fundos_imobiliarios")
    op.execute("drop table migracao.setores_fii")
    op.execute("drop table migracao.fluxos_teste_conversao")
    op.execute("drop table migracao.fidcs")
    op.execute("drop table migracao.estoque_fic")
    op.execute("drop table migracao.estoque_compromissadas")
    op.execute("drop table migracao.estoque_ativos")
    op.execute("drop table migracao.documentos_notion")
    op.execute("drop table migracao.cvm_fidcs")
    op.execute("drop table migracao.cotas_fiis")
    op.execute("drop table migracao.corretoras")
    op.execute("drop table migracao.compras_vendas")
    op.execute("drop table migracao.carteira_bancos")
    op.execute("drop table migracao.calls_lf")
    op.execute("drop table migracao.bancos")
    op.execute("drop table migracao.ativos_anbima")
    op.execute("drop table migracao.administradores")
    op.execute("drop schema migracao")
