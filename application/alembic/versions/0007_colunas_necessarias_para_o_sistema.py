"""Colunas necessárias para o sistema anterior + views para consumo de dados

Revision ID: 0007
Revises: 0006
Create Date: 2024-01-29 10:00:51.423482

"""
from typing import Sequence
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE auth.usuarios ADD COLUMN telefone varchar NULL")

    op.execute(
        """
        CREATE TABLE arquivos.analistas_credito_notion (
            analista_credito_id int4 PRIMARY KEY,
            notion_id text NOT NULL,
            CONSTRAINT analistas_credito_notion_fk FOREIGN KEY (analista_credito_id) REFERENCES icatu.analistas_credito(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE arquivos.emissores_notion (
            emissor_id int4 PRIMARY KEY,
            notion_id text NOT NULL,
            CONSTRAINT emissores_notion_fk FOREIGN KEY (emissor_id) REFERENCES icatu.emissores(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE arquivos.emissor_grupos_notion (
            emissor_grupo_id int4 PRIMARY KEY,
            notion_id text NOT NULL,
            CONSTRAINT emissor_grupo_fk FOREIGN KEY (emissor_grupo_id) REFERENCES icatu.emissor_grupos(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE arquivos.emissor_setores_notion (
            emissor_setor_id int4 PRIMARY KEY,
            notion_id text NOT NULL,
            CONSTRAINT emissor_setor_fk FOREIGN KEY (emissor_setor_id) REFERENCES icatu.emissor_setores(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE OR REPLACE VIEW migracao.view_analistas AS (
        select
            ac.id,
            split_part(u.nome, ' ', 1) as nome,
            u.nome as nome_completo,
            acn.notion_id as id_notion,
            u.email,
            u.telefone
        from
            icatu.analistas_credito ac
            left join
            auth.usuarios u
                on u.id = ac.user_id
            left join
            arquivos.analistas_credito_notion acn
                on acn.analista_credito_id = ac.id
        )
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW migracao.view_info_papeis AS (
        select
            a.codigo,
            e.nome as empresa,
            a.isin,
            e.cnpj,
            (case
                when a.serie = -1 then 'UNI'
                else lpad(a.serie::text, 3, '0')
            end) as serie,
            a.emissao,
            a.valor_emissao,
            a.data_emissao,
            a.data_vencimento,
            (case
                when ai.id = 1 then 'IGP-M'
                when ai.id = 2 then 'IPCA'
                when ai.id = 3 then 'DI'
                when ai.id = 4 then 'DI'
                when ai.id = 5 then 'PRÉ'
            end) as indice,
            (case
                when ai.id = 4 then a.taxa * 100
                else null
            end) as percentual,
            (case
                when ai.id = 3 then a.taxa * 100
                else null
            end) as juros,
            null as banco_mandatario,
            af.nome as agente_fiduciario,
            null as instituicao_depositaria,
            null as coordenador_lider,
            a.atualizacao,
            a.inicio_rentabilidade,
            (case
                when a.tipo_id = 1 then 'Letra Financeira'
                when a.tipo_id = 2 then 'Debênture'
                when a.tipo_id = 3 then 'CDB'
                when a.tipo_id = 4 then 'CRI'
                when a.tipo_id = 5 then 'FIDC'
                when a.tipo_id = 6 then 'BOND'
                when a.tipo_id = 7 then 'NC'
                when a.tipo_id = 8 then 'DPGE'
                when a.tipo_id = 9 then 'FII'
            end) as tipo_ativo,
            (case
                when a.cadastro_manual = true then 'Manual'
                else 'Automático'
            end) as cadastro,
            null as incentivada,
            ap.mesversario as aniversario,
            ap.ipca_negativo,
            ap.ipca_2_meses,
            an.notion_id as id_notion,
            a.quantidade_mercado as qtd_mercado
        from
            icatu.ativos a
            left join
            icatu.emissores e
                on a.emissor_id = e.id
            left join
            icatu.ativo_indices ai
                on a.indice_id = ai.id
            left join
            icatu.ativos_ipca ap
                on a.codigo = ap.ativo_codigo
            left join
            arquivos.ativos_notion an
                on a.codigo = an.ativo_codigo
            left join
            icatu.agentes_fiduciarios af
                on a.agente_fiduciario_id = af.id
        )
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW migracao.view_fluxo_papeis AS (
            select
                af.ativo_codigo || replace(af.data_evento::text, '-', '') || af.ativo_fluxo_tipo_id as id,
                af.ativo_codigo as codigo,
                af.data_evento,
                af.data_pagamento,
                af.ativo_fluxo_tipo_id as tipo_id,
                af.percentual * 100 as percentual,
                af.pu_evento,
                null as liquidacao,
                a.atualizacao,
                (case
                    when a.cadastro_manual then 'Manual'
                    else 'Automático'
                end),
                af.pu_calculado
            from
                icatu.ativo_fluxos af
                left join
                icatu.ativos a
                    on a.codigo = af.ativo_codigo
        )
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW migracao.view_grupo_emissores AS (
        select
            eg.id,
            eg.nome,
            null as cnpj,
            egn.notion_id as id_notion
        from
            icatu.emissor_grupos eg
            left join
            arquivos.emissor_grupos_notion egn
                on eg.id = egn.emissor_grupo_id
        )
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW migracao.view_setores AS (
        select
            es.id,
            es.nome,
            esn.notion_id as id_notion
        from
            icatu.emissor_setores es
            left join
            arquivos.emissor_setores_notion esn
                on es.id = esn.emissor_setor_id
        )
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW migracao.view_emissores AS (
        select
            e.cnpj,
            e.nome as empresa,
            e.codigo_cvm,
            e.grupo_id as grupo,
            e.setor_id as setor,
            e.analista_credito_id as analista,
            e.tier,
            en.notion_id as id_notion
        from
            icatu.emissores e
            left join
            arquivos.emissores_notion en
                on e.id = en.emissor_id
        )
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW migracao.view_ipca_proj AS (
        select
            ip."data",
            ip.taxa as projecao,
            ip.taxa/100 + 1 as indice,
            (case
                when ip.projetado then 'Projeção'
                else 'Índice fechado'
            end) as tipo,
            ip.atualizacao
        from
            icatu.ipca_proj ip
        )
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW migracao.view_igpm_proj AS (
        select
            ip."data",
            ip.taxa as projecao,
            ip.taxa/100 + 1 as indice,
            (case
                when ip.projetado then 'Projeção'
                else 'Índice fechado'
            end) as tipo,
            ip.atualizacao
        from
            icatu.igpm_proj ip
        )
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW migracao.view_historico_cdi AS (
        select
            hc."data",
            hc.taxa,
            POWER(hc.taxa/100 + 1, 1.0/252)::numeric(15,8) as indice,
            hc.indice_acumulado as indice_acum,
            hc.atualizacao
        from
            icatu.historico_cdi hc
        )
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW migracao.view_historico_ipca as (
        with recursive CTE_R as 
        (
            select
                T.data,
                198.22::float8 as indice_acumulado,
                T.indice_acumulado as indice_mes,
                (T.indice_acumulado - 1) * 100 as percentual,
                T.atualizacao
            from
                icatu.historico_ipca as T
            where
                T.data = '1994-02-01'
            union all
            select
                T.data,
                T.indice_acumulado * C.indice_acumulado as indice_acumulado,
                T.indice_acumulado as indice_mes,
                (T.indice_acumulado - 1) * 100 as percentual,
                T.atualizacao
            from
                CTE_R as C
                inner join
                icatu.historico_ipca as T
                    on T.data = (C.data + interval '1 month')::date
        )
        select *
        from CTE_R
        )
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW migracao.view_historico_igpm as (
        with recursive CTE_R as 
        (
            select
                T.data,
                106.553::float8 as indice_acumulado,
                T.indice_acumulado as indice_mes,
                (T.indice_acumulado - 1) * 100 as percentual,
                T.atualizacao
            from
                icatu.historico_igpm as T
            where
                T.data = '1994-11-01'
            union all
            select
                T.data,
                T.indice_acumulado * C.indice_acumulado as indice_acumulado,
                T.indice_acumulado as indice_mes,
                (T.indice_acumulado - 1) * 100 as percentual,
                T.atualizacao
            from
                CTE_R as C
                inner join
                icatu.historico_igpm as T
                    on T.data = (C.data + interval '1 month')::date
        )
        select *
        from CTE_R
        )
        """
    )
    op.execute("ALTER TABLE icatu.fundos ADD COLUMN apelido text NULL")
    op.execute(
        """
        CREATE OR REPLACE VIEW migracao.view_fundos AS (
        select
            f.isin,
            f.apelido as nome,
            f.codigo_brit::text,
            f.cnpj,
            f.nome as nome_xml,
            risco_id as id_risco,
            classificacao_id as id_classificacao,
            (case
				when fc.id = 1 then '42272526000170'
				when fc.id = 2 then '62318407000119'
				when fc.id = 3 then '60701190000104'
				when fc.id = 4 then '60746948000112'
			end) as custodiante,
            null as administrador,
            fi.nome as indice,
            f.atualizacao,
            null as gestor,
            null as inicio,
            null as taxa_adm,
            null as taxa_performance,
            null as periodicidade,
            null as aplicacao_inicial_minima,
            null as movimentacao_minima,
            null as saldo_minimo,
            null as aplicacao_cotizacao_liquidacao,
            null as resgates_cotizacao_liquidacao,
            f.codigo_carteira,
            ft.nome as tipo,
            f.pl_alocavel,
            f.conta_cetip as cetip
        from
            icatu.fundos f
            left join
            icatu.fundo_custodiantes fc
                on f.custodiante_id = fc.id
            left join
            icatu.fundo_indices fi
                on f.indice_id = fi.id
            left join
            icatu.fundo_tipos ft
                on f.tipo_id = ft.id
        )
        """
    )
    op.execute(
        """
        CREATE TABLE migracao.negocios_b3 (
            "data" timestamp NOT NULL,
            codigo varchar NOT NULL,
            quantidade float8 NOT NULL,
            preco float8 NOT NULL,
            taxa float8 NULL,
            origem varchar NULL,
            tipo varchar NOT NULL,
            id_operacao int4 NULL,
            atualizacao timestamp NOT NULL
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE migracao.negocios_b3")

    op.execute("DROP VIEW migracao.view_fundos")

    op.execute("ALTER TABLE icatu.fundos DROP COLUMN apelido")

    op.execute("DROP VIEW migracao.view_historico_igpm")
    op.execute("DROP VIEW migracao.view_historico_ipca")
    op.execute("DROP VIEW migracao.view_historico_cdi")
    op.execute("DROP VIEW migracao.view_igpm_proj")
    op.execute("DROP VIEW migracao.view_ipca_proj")
    op.execute("DROP VIEW migracao.view_emissores")
    op.execute("DROP VIEW migracao.view_setores")
    op.execute("DROP VIEW migracao.view_grupo_emissores")
    op.execute("DROP VIEW migracao.view_fluxo_papeis")
    op.execute("DROP VIEW migracao.view_info_papeis")
    op.execute("DROP VIEW migracao.view_analistas")

    op.execute("DROP TABLE arquivos.emissor_setores_notion")
    op.execute("DROP TABLE arquivos.emissor_grupos_notion")
    op.execute("DROP TABLE arquivos.emissores_notion")
    op.execute("DROP TABLE arquivos.analistas_credito_notion")

    op.execute("ALTER TABLE auth.usuarios DROP COLUMN telefone")


# agentes_fiduciarios       | ---
# analistas_credito         | view_analistas
# ativo_fluxo_tipos         | ---
# ativo_fluxos              | view_fluxo_papeis
# ativo_indices             | ---
# ativo_tipos               | ---
# ativos                    | view_info_papeis
# ativos_ipca               | ---
# atualizacao_rotina        | tabela anterior
# emissor_grupos            | view_grupo_emissores
# emissor_setores           | view_setores
# emissores                 | view_emissores
# fundo_classificacoes      | tabela nova
# fundo_custodiantes        | tabela nova
# fundo_indices             | ---
# fundo_riscos              | ---
# fundo_tipos               | ---
# fundos                    | view_fundos
# historico_cdi             | view_historico_cdi
# historico_igpm            | view_historico_igpm
# historico_ipca            | view_historico_ipca
# igpm_proj                 | view_igpm_proj
# ipca_proj                 | view_ipca_proj
# rotina                    | tabela anterior
# taxas_dap                 | tabela nova
# taxas_di                  | endpoint
# taxas_ntnb                | tabela nova
