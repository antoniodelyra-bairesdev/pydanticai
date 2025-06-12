"""Detalhes dos fundos do site institucional

Revision ID: 20240614132259
Revises: 20240513113300
Create Date: 2024-06-14 13:22:59.952011

"""

from typing import Sequence
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "20240614132259"
down_revision: str | None = "20240513113300"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE icatu.fundos ADD CONSTRAINT fundos_nome_key UNIQUE (nome)")

    op.execute(
        """
        CREATE TABLE icatu.fundo_categorias_documento (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT NOT NULL
        )
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.fundos_documentos (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            fundo_id INTEGER NOT NULL,
            arquivo_id TEXT NOT NULL,
            fundo_categoria_documento_id INTEGER NOT NULL,
            titulo TEXT NULL,
            criado_em TIMESTAMP NOT NULL DEFAULT now(),
            data_referencia DATE NOT NULL DEFAULT now(),
            CONSTRAINT fundos_documentos_fundo_fk FOREIGN KEY (fundo_id) REFERENCES icatu.fundos(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fundos_documentos_arquivo_fk FOREIGN KEY (arquivo_id) REFERENCES sistema.arquivos(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fundos_documentos_fundo_categoria_documento_fk FOREIGN KEY (fundo_categoria_documento_id) REFERENCES icatu.fundo_categorias_documento(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.instituicoes_financeiras (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT NOT NULL
        )
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.fundo_disponibilidades (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT NOT NULL
        )
        """
    )

    op.execute(
        """
        ALTER TABLE icatu.fundo_custodiantes
            ADD COLUMN instituicao_financeira_id INT,
            ADD CONSTRAINT fundo_custodiantes_instituicao_financeira_fk FOREIGN KEY (instituicao_financeira_id)
            REFERENCES icatu.instituicoes_financeiras ON DELETE CASCADE ON UPDATE CASCADE,
            DROP COLUMN IF EXISTS nome_curto
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.fundo_administradores (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT NOT NULL,
            instituicao_financeira_id INT,
            CONSTRAINT fundo_administradores_instituicao_financeira_fk FOREIGN KEY (instituicao_financeira_id) REFERENCES icatu.instituicoes_financeiras ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.fundo_controladores (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT NOT NULL,
            instituicao_financeira_id INT,
            CONSTRAINT fundo_controladores_instituicao_financeira_fk FOREIGN KEY (instituicao_financeira_id) REFERENCES icatu.instituicoes_financeiras ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        INSERT INTO icatu.instituicoes_financeiras (nome) VALUES
            ('BNY Mellon Banco SA'),
            ('Santander'),
            ('Itaú Unibanco SA'),
            ('Bradesco'),
            ('Daycoval')
        """
    )
    op.execute(
        """
        INSERT INTO icatu.fundo_administradores (nome, instituicao_financeira_id) VALUES
            ('Mellon', 1),
            ('Santander', 2),
            ('Intrag DTVM', 3),
            ('Bradesco', 4),
            ('Daycoval', 5)
        """
    )
    op.execute(
        """
        INSERT INTO icatu.fundo_controladores (nome, instituicao_financeira_id) VALUES
            ('Mellon', 1),
            ('Santander', 2),
            ('Itaú', 3),
            ('Bradesco', 4),
            ('Daycoval', 5)
        """
    )

    op.execute(
        "UPDATE icatu.fundo_custodiantes SET nome = 'Mellon', instituicao_financeira_id = 1 WHERE id = 1"
    )
    op.execute(
        "UPDATE icatu.fundo_custodiantes SET nome = 'Santander', instituicao_financeira_id = 2 WHERE id = 2"
    )
    op.execute(
        "UPDATE icatu.fundo_custodiantes SET nome = 'Itaú', instituicao_financeira_id = 3 WHERE id = 3"
    )
    op.execute(
        "UPDATE icatu.fundo_custodiantes SET nome = 'Bradesco', instituicao_financeira_id = 4 WHERE id = 4"
    )
    op.execute(
        "UPDATE icatu.fundo_custodiantes SET nome = 'Daycoval', instituicao_financeira_id = 5 WHERE id = 5"
    )

    op.execute(
        """
        CREATE TABLE icatu.publicos_alvo (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT NOT NULL
        )
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.fundo_caracteristicas_extras (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT NOT NULL
        )
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.fundos_fundo_caracteristicas_extras (
            fundo_id INTEGER NOT NULL,
            fundo_caracteristica_extra_id INTEGER NOT NULL,

            CONSTRAINT fundos_fundo_caracteristicas_extras_fundo_fk FOREIGN KEY (fundo_id) REFERENCES icatu.fundos(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fundos_fundo_caracteristicas_extras_fundo_caracteristica_extra_fk FOREIGN KEY (fundo_caracteristica_extra_id) REFERENCES icatu.fundo_caracteristicas_extras(id) ON DELETE CASCADE ON UPDATE CASCADE,

            PRIMARY KEY (fundo_id, fundo_caracteristica_extra_id)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.indices_benchmark (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE icatu.fundos_indices_benchmark (
            fundo_id INTEGER NOT NULL,
            indice_benchmark_id INTEGER NOT NULL,
            ordenacao INTEGER NOT NULL,
        
            CONSTRAINT fundos_indices_benchmark_indice_benchmark_fk FOREIGN KEY (indice_benchmark_id) REFERENCES icatu.indices_benchmark(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fundos_indices_benchmark_fundo_fk FOREIGN KEY (fundo_id) REFERENCES icatu.fundos(id) ON DELETE CASCADE ON UPDATE CASCADE,
        
            PRIMARY KEY (fundo_id, indice_benchmark_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE icatu.mesas (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT NOT NULL,
            ordenacao INTEGER NOT NULL DEFAULT 0,
            sobre TEXT NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE icatu.fundos_mesas (
            fundo_id INTEGER NOT NULL,
            mesa_id INTEGER NOT NULL,
            responsavel BOOLEAN NOT NULL,
        
            CONSTRAINT fundos_mesas_fundo_fk FOREIGN KEY (fundo_id) REFERENCES icatu.fundos(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fundos_mesas_mesa_fk FOREIGN KEY (mesa_id) REFERENCES icatu.mesas(id) ON DELETE CASCADE ON UPDATE CASCADE,
        
            PRIMARY KEY (fundo_id, mesa_id)
        )
        """
    )

    op.execute("ALTER TABLE icatu.fundos DROP COLUMN IF EXISTS apelido CASCADE")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN IF EXISTS pl_alocavel CASCADE")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN IF EXISTS indice_id CASCADE")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN IF EXISTS tipo_id CASCADE")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN IF EXISTS risco_id CASCADE")
    op.execute(
        "ALTER TABLE icatu.fundos DROP COLUMN IF EXISTS classificacao_id CASCADE"
    )

    op.execute("DROP TABLE IF EXISTS icatu.fundo_indices CASCADE")
    op.execute("DROP TABLE IF EXISTS icatu.fundo_tipos CASCADE")
    op.execute("DROP TABLE IF EXISTS icatu.fundo_riscos CASCADE")
    op.execute("DROP TABLE IF EXISTS icatu.fundo_classificacoes CASCADE")

    op.execute("ALTER TABLE icatu.fundos RENAME COLUMN atualizacao TO atualizado_em")
    op.execute(
        "ALTER TABLE icatu.fundos RENAME COLUMN custodiante_id TO fundo_custodiante_id"
    )
    op.execute(
        "ALTER TABLE icatu.fundos ALTER COLUMN fundo_custodiante_id DROP NOT NULL"
    )

    op.execute("ALTER TABLE icatu.fundos ADD COLUMN conta_selic TEXT NULL")
    op.execute("ALTER TABLE icatu.fundos ADD COLUMN mnemonico TEXT NULL")
    op.execute(
        "ALTER TABLE icatu.fundos ADD COLUMN aberto_para_captacao BOOLEAN DEFAULT FALSE NOT NULL"
    )
    op.execute(
        "ALTER TABLE icatu.fundos ADD COLUMN fundo_disponibilidade_id INTEGER NULL"
    )
    op.execute("ALTER TABLE icatu.fundos ADD COLUMN ticker_b3 TEXT NULL")
    op.execute(
        "ALTER TABLE icatu.fundos ADD CONSTRAINT fundos_ticker_b3_key UNIQUE (ticker_b3)"
    )
    op.execute(
        "ALTER TABLE icatu.fundos ADD COLUMN fundo_administrador_id INTEGER NULL"
    )
    op.execute(
        "ALTER TABLE icatu.fundos ADD COLUMN codigo_carteira_administrador TEXT NULL"
    )
    op.execute("ALTER TABLE icatu.fundos ADD COLUMN fundo_controlador_id INTEGER NULL")
    op.execute(
        "ALTER TABLE icatu.fundos ADD COLUMN agencia_bancaria_custodia TEXT NULL"
    )

    op.execute("ALTER TABLE icatu.fundos ADD COLUMN conta_aplicacao TEXT NULL")
    op.execute("ALTER TABLE icatu.fundos ADD COLUMN conta_resgate TEXT NULL")
    op.execute("ALTER TABLE icatu.fundos ADD COLUMN conta_movimentacao TEXT NULL")
    op.execute("ALTER TABLE icatu.fundos ADD COLUMN conta_tributada TEXT NULL")

    op.execute("ALTER TABLE icatu.fundos ADD COLUMN minimo_aplicacao FLOAT8 NULL")
    op.execute("ALTER TABLE icatu.fundos ADD COLUMN minimo_movimentacao FLOAT8 NULL")
    op.execute("ALTER TABLE icatu.fundos ADD COLUMN minimo_saldo FLOAT8 NULL")

    op.execute("ALTER TABLE icatu.fundos ADD COLUMN cotizacao_aplicacao INTEGER NULL")
    op.execute(
        "ALTER TABLE icatu.fundos ADD COLUMN cotizacao_aplicacao_sao_dias_uteis BOOLEAN NULL"
    )
    op.execute(
        "ALTER TABLE icatu.fundos ADD COLUMN cotizacao_aplicacao_detalhes TEXT NULL"
    )

    op.execute("ALTER TABLE icatu.fundos ADD COLUMN cotizacao_resgate INTEGER NULL")
    op.execute(
        "ALTER TABLE icatu.fundos ADD COLUMN cotizacao_resgate_sao_dias_uteis BOOLEAN NULL"
    )
    op.execute(
        "ALTER TABLE icatu.fundos ADD COLUMN cotizacao_resgate_detalhes TEXT NULL"
    )

    op.execute("ALTER TABLE icatu.fundos ADD COLUMN financeiro_aplicacao INTEGER NULL")
    op.execute(
        "ALTER TABLE icatu.fundos ADD COLUMN financeiro_aplicacao_sao_dias_uteis BOOLEAN NULL"
    )
    op.execute(
        "ALTER TABLE icatu.fundos ADD COLUMN financeiro_aplicacao_detalhes TEXT NULL"
    )

    op.execute("ALTER TABLE icatu.fundos ADD COLUMN financeiro_resgate INTEGER NULL")
    op.execute(
        "ALTER TABLE icatu.fundos ADD COLUMN financeiro_resgate_sao_dias_uteis BOOLEAN NULL"
    )
    op.execute(
        "ALTER TABLE icatu.fundos ADD COLUMN financeiro_resgate_detalhes TEXT NULL"
    )

    op.execute("ALTER TABLE icatu.fundos ADD COLUMN publico_alvo_id INTEGER NULL")
    op.execute("ALTER TABLE icatu.fundos ADD COLUMN benchmark TEXT NULL")
    op.execute("ALTER TABLE icatu.fundos ADD COLUMN taxa_performance TEXT NULL")
    op.execute("ALTER TABLE icatu.fundos ADD COLUMN taxa_administracao TEXT NULL")
    op.execute("ALTER TABLE icatu.fundos ADD COLUMN resumo_estrategias TEXT NULL")

    op.execute(
        """
        ALTER TABLE icatu.fundos
        DROP CONSTRAINT IF EXISTS fundos_custodiante_id_fkey,
        ADD CONSTRAINT fundos_publico_alvo_fk FOREIGN KEY (publico_alvo_id) REFERENCES icatu.publicos_alvo(id) ON DELETE CASCADE ON UPDATE CASCADE,
        ADD CONSTRAINT fundos_fundo_disponibilidade_fk FOREIGN KEY (fundo_disponibilidade_id) REFERENCES icatu.fundo_disponibilidades(id) ON DELETE CASCADE ON UPDATE CASCADE,
        ADD CONSTRAINT fundos_fundo_administrador_fk FOREIGN KEY (fundo_administrador_id) REFERENCES icatu.fundo_administradores(id) ON DELETE CASCADE ON UPDATE CASCADE,
        ADD CONSTRAINT fundos_fundo_controlador_fk FOREIGN KEY (fundo_controlador_id) REFERENCES icatu.fundo_controladores(id) ON DELETE CASCADE ON UPDATE CASCADE,
        ADD CONSTRAINT fundos_fundo_custodiante_fk FOREIGN KEY (fundo_custodiante_id) REFERENCES icatu.fundo_custodiantes(id) ON DELETE CASCADE ON UPDATE CASCADE
        """
    )

    op.execute("CREATE SCHEMA historico_icatu")

    op.execute(
        """
        CREATE TABLE historico_icatu.fundos (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            fundo_id INTEGER NOT NULL,
            CONSTRAINT historico_icatu_fundos_fundo_fk FOREIGN KEY (fundo_id) REFERENCES icatu.fundos(id) ON DELETE CASCADE ON UPDATE CASCADE,
            
            isin bpchar(12) NULL,
            mnemonico text null,
            conta_selic TEXT NULL,
            nome text NOT NULL,
            codigo_brit int4 NULL,
            cnpj bpchar(14) NOT NULL,
            atualizado_em timestamp DEFAULT now() NOT NULL,
            conta_cetip text NULL,
            codigo_carteira text NULL,
            fundo_custodiante_id int2 NOT NULL,
            aberto_para_captacao bool DEFAULT false NOT NULL,
            fundo_disponibilidade_id int4 NULL,
            ticker_b3 text NULL,
            fundo_administrador_id int4 NULL,
            codigo_carteira_administrador text NULL,
            fundo_controlador_id int4 NULL,
            agencia_bancaria_custodia text NULL,
            conta_aplicacao text NULL,
            conta_resgate text NULL,
            conta_movimentacao text NULL,
            conta_tributada text NULL,
            minimo_aplicacao float8 NULL,
            minimo_movimentacao float8 NULL,
            minimo_saldo float8 NULL,
            cotizacao_aplicacao int4 NULL,
            cotizacao_aplicacao_sao_dias_uteis bool NULL,
            cotizacao_aplicacao_detalhes text NULL,
            cotizacao_resgate int4 NULL,
            cotizacao_resgate_sao_dias_uteis bool NULL,
            cotizacao_resgate_detalhes text NULL,
            financeiro_aplicacao int4 NULL,
            financeiro_aplicacao_sao_dias_uteis bool NULL,
            financeiro_aplicacao_detalhes text NULL,
            financeiro_resgate int4 NULL,
            financeiro_resgate_sao_dias_uteis bool NULL,
            financeiro_resgate_detalhes text NULL,
            publico_alvo_id int4 NULL,
            benchmark text NULL,
            taxa_performance text NULL,
            taxa_administracao text NULL,
            resumo_estrategias text NULL,
            
            CONSTRAINT fundos_cnpj_key UNIQUE (cnpj),
            CONSTRAINT fundos_codigo_brit_key UNIQUE (codigo_brit)
        )
        """
    )

    op.execute(
        """
        ALTER TABLE historico_icatu.fundos
        ADD CONSTRAINT historico_icatu_fundos_publico_alvo_fk FOREIGN KEY (publico_alvo_id) REFERENCES icatu.publicos_alvo(id) ON DELETE CASCADE ON UPDATE CASCADE,
        ADD CONSTRAINT historico_icatu_fundos_fundo_disponibilidade_fk FOREIGN KEY (fundo_disponibilidade_id) REFERENCES icatu.fundo_disponibilidades(id) ON DELETE CASCADE ON UPDATE CASCADE,
        ADD CONSTRAINT historico_icatu_fundos_fundo_administrador_fk FOREIGN KEY (fundo_administrador_id) REFERENCES icatu.fundo_administradores(id) ON DELETE CASCADE ON UPDATE CASCADE,
        ADD CONSTRAINT historico_icatu_fundos_fundo_controlador_fk FOREIGN KEY (fundo_controlador_id) REFERENCES icatu.fundo_controladores(id) ON DELETE CASCADE ON UPDATE CASCADE,
        ADD CONSTRAINT historico_icatu_fundos_fundo_custodiante_fk FOREIGN KEY (fundo_custodiante_id) REFERENCES icatu.fundo_custodiantes(id) ON DELETE CASCADE ON UPDATE CASCADE;
        """
    )

    op.execute(
        """
        CREATE TABLE historico_icatu.fundos_fundo_caracteristicas_extras (
            historico_fundo_id INTEGER NOT NULL,
            fundo_caracteristica_extra_id INTEGER NOT NULL,
            
            CONSTRAINT historico_icatu_fundos_fundo_caracteristicas_extras_historico_icatu_fundo_fk FOREIGN KEY (historico_fundo_id) REFERENCES historico_icatu.fundos(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT historico_icatu_fundos_fundo_caracteristicas_extras_fundo_caracteristica_extra_fk FOREIGN KEY (fundo_caracteristica_extra_id) REFERENCES icatu.fundo_caracteristicas_extras(id) ON DELETE CASCADE ON UPDATE CASCADE,
        
            PRIMARY KEY (historico_fundo_id, fundo_caracteristica_extra_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE historico_icatu.fundos_indices_benchmark (
            historico_fundo_id INTEGER NOT NULL,
            indice_benchmark_id INTEGER NOT NULL,
            ordenacao INTEGER NOT NULL,
        
            CONSTRAINT historico_icatu_fundos_indices_benchmark_historico_icatu_fundo_fk FOREIGN KEY (historico_fundo_id) REFERENCES historico_icatu.fundos(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT historico_icatu_fundos_indices_benchmark_indice_benchmark_fk FOREIGN KEY (indice_benchmark_id) REFERENCES icatu.indices_benchmark(id) ON DELETE CASCADE ON UPDATE CASCADE,
        
            PRIMARY KEY (historico_fundo_id, indice_benchmark_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE historico_icatu.fundos_mesas (
            historico_fundo_id INTEGER NOT NULL,
            mesa_id INTEGER NOT NULL,
        
            CONSTRAINT historico_icatu_fundos_mesas_historico_icatu_fundo_fk FOREIGN KEY (historico_fundo_id) REFERENCES historico_icatu.fundos(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT historico_icatu_fundos_mesas_mesa_fk FOREIGN KEY (mesa_id) REFERENCES icatu.mesas(id) ON DELETE CASCADE ON UPDATE CASCADE,
        
            PRIMARY KEY (historico_fundo_id, mesa_id)
        )
        """
    )
    op.execute(
        """
        INSERT INTO icatu.fundo_caracteristicas_extras (
            nome
        ) VALUES
            ('Incentivado em infraestrutura'),
            ('Total Return'),
            ('Long Biased'),
            ('Short Biased')
        """
    )
    op.execute(
        """
        INSERT INTO icatu.fundo_disponibilidades (
            nome
        ) VALUES
            ('Listado'),
            ('Aberto'),
            ('Fechado'),
            ('Exclusivo')
        """
    )
    op.execute(
        """
        INSERT INTO icatu.publicos_alvo (
            nome
        ) VALUES
            ('Investidor geral'),
            ('Investidor qualificado'),
            ('Investidor profissional')
        """
    )
    op.execute(
        """
        INSERT INTO icatu.mesas (
            nome
        ) VALUES
            ('Renda Fixa'),
            ('Crédito Privado'),
            ('Ações'),
            ('Imobiliário'),
            ('Investment Solutions')
        """
    )
    op.execute(
        """
        INSERT INTO icatu.fundo_categorias_documento (
            nome
        ) VALUES
            ('Lâminas'),
            ('Prospectos preliminares'),
            ('Avisos ao mercado')
        """
    )

    op.execute("DROP TABLE IF EXISTS sistema.site_institucional_fundo_tipos CASCADE")
    op.execute("DROP TABLE IF EXISTS sistema.site_institucional_classificacoes CASCADE")
    op.execute(
        "DROP TABLE IF EXISTS sistema.fundo_site_institucional_classificacoes CASCADE"
    )

    op.execute("CREATE SCHEMA site_institucional")

    op.execute(
        """
        CREATE TABLE site_institucional.fundo_classificacoes (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT NOT NULL
        )
        """
    )

    op.execute(
        """
        INSERT INTO site_institucional.fundo_classificacoes (
            nome
        ) VALUES
            ('Renda Fixa'),
            ('Ações'),
            ('Multimercado'),
            ('Imobiliário'),
            ('Ajustado ao Risco'),
            ('Data Alvo'),
            ('Crédito Privado')
        """
    )

    op.execute(
        """
        CREATE TABLE site_institucional.fundo_tipos (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT NOT NULL
        )
        """
    )

    op.execute(
        """
        INSERT INTO site_institucional.fundo_tipos (
            nome
        ) VALUES
            ('Fundo de Investimento'),
            ('Fundo de Previdência (FIE Tipo I)'),
            ('Fundo de Previdência (FIE Tipo II)'),
            ('Fundo de Previdência (FIFE)')
        """
    )

    op.execute(
        """
        CREATE TABLE site_institucional.fundos (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            fundo_id INTEGER NOT NULL,
            CONSTRAINT site_institucional_fundos_fundo_fk FOREIGN KEY (fundo_id) REFERENCES icatu.fundos(id) ON DELETE CASCADE ON UPDATE CASCADE,
            nome text NOT NULL,
            cnpj bpchar(14) NOT NULL,
            atualizado_em timestamp DEFAULT now() NOT NULL,
            aberto_para_captacao bool DEFAULT false NOT NULL,
            fundo_disponibilidade_id int4 NULL,
            ticker_b3 text NULL,
            cotizacao_resgate int4 NOT NULL,
            cotizacao_resgate_sao_dias_uteis bool NOT NULL,
            cotizacao_resgate_detalhes text NOT NULL,
            financeiro_resgate int4 NOT NULL,
            financeiro_resgate_sao_dias_uteis bool NOT NULL,
            financeiro_resgate_detalhes text NOT NULL,
            publico_alvo_id int4 NOT NULL,
            benchmark text NULL,
            taxa_performance text NULL,
            taxa_administracao text NULL,
            resumo_estrategias text NULL,
            site_institucional_classificacao_id integer NOT NULL,
            CONSTRAINT site_institucional_fundos_classificacao_fk FOREIGN KEY (site_institucional_classificacao_id) REFERENCES site_institucional.fundo_classificacoes(id) ON DELETE CASCADE ON UPDATE CASCADE,
            site_institucional_tipo_id integer NOT NULL,
            CONSTRAINT site_institucional_fundos_tipo_fk FOREIGN KEY (site_institucional_tipo_id) REFERENCES site_institucional.fundo_tipos(id) ON DELETE CASCADE ON UPDATE CASCADE,
            mesa_id INTEGER NOT NULL,
            CONSTRAINT site_institucional_fundos_mesas_mesa_fk FOREIGN KEY (mesa_id) REFERENCES icatu.mesas(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fundos_nome_key UNIQUE (nome),
            CONSTRAINT fundos_cnpj_key UNIQUE (cnpj),
            CONSTRAINT fundos_ticker_b3_key UNIQUE (ticker_b3)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE site_institucional.fundos_documentos (
            site_institucional_fundo_id INTEGER NOT NULL,
            fundos_documento_id INTEGER NOT NULL,
            
            PRIMARY KEY (site_institucional_fundo_id, fundos_documento_id),
            CONSTRAINT fundos_documentos_site_institucional_fundo_fk FOREIGN KEY (site_institucional_fundo_id) REFERENCES site_institucional.fundos(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fundos_documentos_fundos_documento_fk FOREIGN KEY (fundos_documento_id) REFERENCES icatu.fundos_documentos(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE site_institucional.fundos_fundo_caracteristicas_extras (
            site_institucional_fundo_id INTEGER NOT NULL,
            fundo_caracteristica_extra_id INTEGER NOT NULL,
            
            CONSTRAINT site_institucional_fundos_fundo_caracteristicas_extras_site_institucional_fundo_fk FOREIGN KEY (site_institucional_fundo_id) REFERENCES site_institucional.fundos(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT site_institucional_fundos_fundo_caracteristicas_extras_fundo_caracteristica_extra_fk FOREIGN KEY (fundo_caracteristica_extra_id) REFERENCES icatu.fundo_caracteristicas_extras(id) ON DELETE CASCADE ON UPDATE CASCADE,
        
            PRIMARY KEY (site_institucional_fundo_id, fundo_caracteristica_extra_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE site_institucional.fundos_indices_benchmark (
            site_institucional_fundo_id INTEGER NOT NULL,
            indice_benchmark_id INTEGER NOT NULL,
            ordenacao INTEGER NOT NULL,
        
            CONSTRAINT site_institucional_fundos_indices_benchmark_site_institucional_fundo_fk FOREIGN KEY (site_institucional_fundo_id) REFERENCES site_institucional.fundos(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT site_institucional_fundos_indices_benchmark_indice_benchmark_fk FOREIGN KEY (indice_benchmark_id) REFERENCES icatu.indices_benchmark(id) ON DELETE CASCADE ON UPDATE CASCADE,
        
            PRIMARY KEY (site_institucional_fundo_id, indice_benchmark_id)
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE site_institucional.fundos_indices_benchmark")
    op.execute("DROP TABLE site_institucional.fundos_fundo_caracteristicas_extras")
    op.execute("DROP TABLE site_institucional.fundos_documentos")
    op.execute("DROP TABLE site_institucional.fundos")
    op.execute("DROP TABLE site_institucional.fundo_tipos")
    op.execute("DROP TABLE site_institucional.fundo_classificacoes")
    op.execute("DROP SCHEMA site_institucional")

    op.execute("DROP TABLE historico_icatu.fundos_mesas")
    op.execute("DROP TABLE historico_icatu.fundos_indices_benchmark")
    op.execute("DROP TABLE historico_icatu.fundos_fundo_caracteristicas_extras")

    op.execute(
        """
        ALTER TABLE historico_icatu.fundos
        DROP CONSTRAINT historico_icatu_fundos_fundo_custodiante_fk,
        DROP CONSTRAINT historico_icatu_fundos_fundo_controlador_fk,
        DROP CONSTRAINT historico_icatu_fundos_fundo_administrador_fk,
        DROP CONSTRAINT historico_icatu_fundos_fundo_disponibilidade_fk,
        DROP CONSTRAINT historico_icatu_fundos_publico_alvo_fk
        """
    )

    op.execute("DROP TABLE historico_icatu.fundos")

    op.execute("DROP SCHEMA historico_icatu")

    op.execute(
        """
        ALTER TABLE icatu.fundos
        DROP CONSTRAINT fundos_publico_alvo_fk,
        DROP CONSTRAINT fundos_fundo_disponibilidade_fk,
        DROP CONSTRAINT fundos_fundo_administrador_fk,
        DROP CONSTRAINT fundos_fundo_controlador_fk,
        DROP CONSTRAINT fundos_fundo_custodiante_fk
        """
    )

    op.execute("ALTER TABLE icatu.fundos DROP COLUMN resumo_estrategias")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN taxa_administracao")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN taxa_performance")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN benchmark")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN publico_alvo_id")

    op.execute("ALTER TABLE icatu.fundos DROP COLUMN financeiro_resgate_detalhes")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN financeiro_resgate_sao_dias_uteis")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN financeiro_resgate")

    op.execute("ALTER TABLE icatu.fundos DROP COLUMN financeiro_aplicacao_detalhes")
    op.execute(
        "ALTER TABLE icatu.fundos DROP COLUMN financeiro_aplicacao_sao_dias_uteis"
    )
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN financeiro_aplicacao")

    op.execute("ALTER TABLE icatu.fundos DROP COLUMN cotizacao_resgate_detalhes")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN cotizacao_resgate_sao_dias_uteis")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN cotizacao_resgate")

    op.execute("ALTER TABLE icatu.fundos DROP COLUMN cotizacao_aplicacao_detalhes")
    op.execute(
        "ALTER TABLE icatu.fundos DROP COLUMN cotizacao_aplicacao_sao_dias_uteis"
    )
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN cotizacao_aplicacao")

    op.execute("ALTER TABLE icatu.fundos DROP COLUMN minimo_saldo")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN minimo_movimentacao")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN minimo_aplicacao")

    op.execute("ALTER TABLE icatu.fundos DROP COLUMN conta_tributada")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN conta_movimentacao")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN conta_resgate")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN conta_aplicacao")

    op.execute("ALTER TABLE icatu.fundos DROP COLUMN agencia_bancaria_custodia")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN fundo_controlador_id")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN codigo_carteira_administrador")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN fundo_administrador_id")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN ticker_b3")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN fundo_disponibilidade_id")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN aberto_para_captacao")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN mnemonico")
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN conta_selic")

    op.execute(
        "ALTER TABLE icatu.fundos RENAME COLUMN fundo_custodiante_id TO custodiante_id"
    )
    op.execute("ALTER TABLE icatu.fundos RENAME COLUMN atualizado_em TO atualizacao")

    op.execute("DROP TABLE icatu.fundos_mesas")
    op.execute("DROP TABLE icatu.mesas")
    op.execute("DROP TABLE icatu.fundos_indices_benchmark")
    op.execute("DROP TABLE icatu.indices_benchmark")
    op.execute("DROP TABLE icatu.fundos_fundo_caracteristicas_extras")
    op.execute("DROP TABLE icatu.fundo_caracteristicas_extras")
    op.execute("DROP TABLE icatu.publicos_alvo")
    op.execute("DROP TABLE icatu.fundo_controladores")
    op.execute("DROP TABLE icatu.fundo_administradores")
    op.execute(
        """
        ALTER TABLE icatu.fundo_custodiantes
            DROP COLUMN IF EXISTS instituicao_financeira_id
        """
    )
    op.execute("DROP TABLE icatu.fundo_disponibilidades")
    op.execute("DROP TABLE icatu.instituicoes_financeiras CASCADE")

    op.execute("DROP TABLE icatu.fundos_documentos")
    op.execute("DROP TABLE icatu.fundo_categorias_documento")

    op.execute("ALTER TABLE icatu.fundos DROP CONSTRAINT fundos_nome_key")
