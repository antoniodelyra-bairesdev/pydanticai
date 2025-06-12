"""Tabelas relacionadas às operações

Revision ID: 0008
Revises: 0007
Create Date: 2024-02-26 10:19:09.297482

"""

from typing import Sequence
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE icatu.codigos_erro_b3_rtc (
            id serial4 NOT NULL,
            descricao text NOT NULL,
            CONSTRAINT codigos_erro_b3_rtc_pk PRIMARY KEY (id)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.casamento_operacao_voice (
            id serial8 NOT NULL,
            CONSTRAINT casamento_operacao_voice_pk PRIMARY KEY (id)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.operacao_capturada (
            id serial8 NOT NULL,
            casamento_operacao_voice_id int8 UNIQUE NULL,

            codigo_ativo text NOT NULL,
            taxa float8 NOT NULL,
            preco_unitario float8 NOT NULL,
            quantidade float8 NOT NULL,
            id_trader text NOT NULL,
            data_operacao date NOT NULL,
            criado_em timestamp NOT NULL DEFAULT now(),
            nome_contraparte text NOT NULL,
            vanguarda_compra bool NOT NULL,
            id_instrumento_financeiro text NOT NULL,
            id_instrumento_financeiro_subjacente text NULL,

            CONSTRAINT operacao_capturada_pk PRIMARY KEY (id),
            CONSTRAINT operacao_capturada_casamento_fk FOREIGN KEY (casamento_operacao_voice_id) REFERENCES icatu.casamento_operacao_voice(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
    """
    )

    op.execute(
        """
        CREATE TABLE icatu.agencias_ratings (
            id serial4 NOT NULL,
            nome text NOT NULL,
            CONSTRAINT agencias_ratings_pk PRIMARY KEY (id)
        )
    """
    )

    op.execute(
        """
        INSERT INTO icatu.agencias_ratings
            (nome)
        VALUES
            ('ICATU'),
            ('FITCH'),
            ('MOODYS'),
            ('S&P')
    """
    )

    op.execute(
        "select setval('icatu.agencias_ratings_id_seq', (select max(id) from icatu.agencias_ratings))"
    )

    op.execute(
        """
        CREATE TABLE icatu.ratings (
            id serial4 NOT NULL,
            agencia_ratings_id int4 NOT NULL,
            rating text NOT NULL,
            ordenacao int2 NOT NULL,
            CONSTRAINT ratings_pk PRIMARY KEY (id),
            CONSTRAINT ratings_fk FOREIGN KEY (agencia_ratings_id) REFERENCES icatu.agencias_ratings(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
    """
    )

    op.execute(
        """
        INSERT INTO icatu.ratings
            (agencia_ratings_id, rating, ordenacao)
        VALUES
            (1, '1', 11),
            (1, '2', 12),
            (1, '3', 13),
            (1, '4', 14),
            (1, '5', 15),
            (1, '6', 16),
            (2, 'AAA', 1),
            (2, 'AA+', 2),
            (2, 'AA', 3),
            (2, 'AA-', 4),
            (2, 'A+', 5),
            (2, 'A', 6),
            (2, 'A-', 7),
            (2, 'BBB+', 8),
            (2, 'BBB', 9),
            (2, 'BBB-', 10),
            (2, 'BB+', 11),
            (2, 'BB', 12),
            (2, 'BB-', 13),
            (2, 'B+', 14),
            (2, 'B', 15),
            (2, 'B-', 16),
            (2, 'CCC+', 17),
            (2, 'CCC', 18),
            (2, 'CCC-', 19),
            (2, 'CC+', 20),
            (2, 'CC', 21),
            (2, 'CC-', 22),
            (2, 'C+', 23),
            (2, 'C', 24),
            (2, 'C-', 25),
            (2, 'D', 26),
            (2, 'Retirado', 27),
            (3, 'Aaa', 1),
            (3, 'AAA', 1),
            (3, 'Aa1', 2),
            (3, 'AA+', 2),
            (3, 'Aa2', 3),
            (3, 'AA', 3),
            (3, 'Aa3', 4),
            (3, 'AA-', 4),
            (3, 'A1', 5),
            (3, 'A+', 5),
            (3, 'A2', 6),
            (3, 'A', 6),
            (3, 'A3', 7),
            (3, 'A-', 7),
            (3, 'Baa1', 8),
            (3, 'BBB+', 8),
            (3, 'Baa2', 9),
            (3, 'BBB', 9),
            (3, 'Baa3', 10),
            (3, 'BBB-', 10),
            (3, 'Ba1', 11),
            (3, 'BB+', 11),
            (3, 'Ba2', 12),
            (3, 'BB', 12),
            (3, 'Ba3', 13),
            (3, 'BB-', 13),
            (3, 'B1', 14),
            (3, 'B+', 14),
            (3, 'B2', 15),
            (3, 'B', 15),
            (3, 'B3', 16),
            (3, 'B-', 16),
            (3, 'CCC-', 19),
            (3, 'Retirado', 27),
            (4, 'AAA', 1),
            (4, 'AA+', 2),
            (4, 'AA', 3),
            (4, 'AA-', 4),
            (4, 'A+', 5),
            (4, 'A', 6),
            (4, 'A-', 7),
            (4, 'BBB+', 8),
            (4, 'BBB', 9),
            (4, 'BBB-', 10),
            (4, 'BB+', 11),
            (4, 'BB', 12),
            (4, 'BB-', 13),
            (4, 'B+', 14),
            (4, 'B', 15),
            (4, 'B-', 16),
            (4, 'CCC-', 19),
            (4, 'D', 26),
            (4, 'Retirado', 27)
    """
    )

    op.execute(
        "select setval('icatu.ratings_id_seq', (select max(id) from icatu.ratings))"
    )

    op.execute(
        """
        CREATE TABLE icatu.registro_NoMe (
            id serial8 NOT NULL,
            casamento_operacao_voice_id int8 NOT NULL,

            registro_NoMe_novo_id int8 UNIQUE NULL,
            fundo_id int8 NOT NULL,

            quantidade float8 NOT NULL,
            numero_controle_NoMe text NOT NULL,

            criado_em timestamp NOT NULL DEFAULT now(),

            CONSTRAINT registro_NoMe_pk PRIMARY KEY (id),
            CONSTRAINT registro_NoMe_casamento_fk FOREIGN KEY (casamento_operacao_voice_id) REFERENCES icatu.casamento_operacao_voice(id) ON DELETE CASCADE ON UPDATE CASCADE,

            CONSTRAINT registro_NoMe_novo_fk FOREIGN KEY (registro_NoMe_novo_id) REFERENCES icatu.registro_NoMe(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT registro_NoMe_fundo_fk FOREIGN KEY (fundo_id) REFERENCES icatu.fundos(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.aprovacao_backoffice (
            id serial8 NOT NULL,
            casamento_operacao_voice_id int8 NOT NULL,
            
            registro_NoMe_id int8 NULL,
            usuario_id int4 NOT NULL,
            operacao_alocada_internamente_id int8 NOT NULL,

            aprovacao bool NOT NULL,

            motivo text NULL,
            criado_em timestamp NOT NULL DEFAULT NOW(),
            
            CONSTRAINT aprovacao_backoffice_pk PRIMARY KEY (id),
            CONSTRAINT aprovacao_backoffice_casamento_fk FOREIGN KEY (casamento_operacao_voice_id) REFERENCES icatu.casamento_operacao_voice(id) ON DELETE CASCADE ON UPDATE CASCADE,

            CONSTRAINT aprovacao_backoffice_registro_fk FOREIGN KEY (registro_NoMe_id) REFERENCES icatu.registro_NoMe(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT aprovacao_backoffice_usuario_fk FOREIGN KEY (usuario_id) REFERENCES auth.usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE,

            CONSTRAINT aprovacao_backoffice_unique_tuple UNIQUE NULLS NOT DISTINCT (casamento_operacao_voice_id, registro_NoMe_id, operacao_alocada_internamente_id)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.operacao_alocada_internamente (
            id serial8 NOT NULL,
            casamento_operacao_voice_id int8 NOT NULL,

            aprovacao_anterior_backoffice_id int8 NULL,         -- Primeira alocação (NULL) ou realocação
            registro_NoMe_id int8 NULL,                         -- Anterior ou posterior ao envio para B3
            
            usuario_id int4 NULL default NULL,
            indice_id int4 NOT NULL,
            rating text NULL,
            
            codigo_ativo text NOT NULL,
            vanguarda_compra bool NOT NULL,
            nome_contraparte text NULL,
            taxa float8 NOT NULL,
            preco_unitario float8 NOT NULL,
            quantidade float8 NOT NULL,
            data_operacao date NOT NULL,
            criado_em timestamp NOT NULL DEFAULT now(),
            externa bool NOT NULL DEFAULT true,
            
            CONSTRAINT operacao_alocada_internamente_pk PRIMARY KEY (id),
            CONSTRAINT operacao_alocada_internamente_casamento_fk FOREIGN KEY (casamento_operacao_voice_id) REFERENCES icatu.casamento_operacao_voice(id) ON DELETE CASCADE ON UPDATE CASCADE,

            CONSTRAINT operacao_alocada_internamente_aprovacao_fk FOREIGN KEY (aprovacao_anterior_backoffice_id) REFERENCES icatu.aprovacao_backoffice(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT operacao_alocada_internamente_registro_fk FOREIGN KEY (registro_NoMe_id) REFERENCES icatu.registro_NoMe(id) ON DELETE CASCADE ON UPDATE CASCADE,

            CONSTRAINT operacao_alocada_internamente_usuario_fk FOREIGN KEY (usuario_id) REFERENCES auth.usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT operacao_alocada_internamente_indice_fk FOREIGN KEY (indice_id) REFERENCES icatu.ativo_indices(id) ON DELETE CASCADE ON UPDATE CASCADE,
            
            CONSTRAINT operacao_alocada_internamente_check_interno CHECK ((usuario_id is not null and externa = false) or (usuario_id is null and externa = true)),
            
            CONSTRAINT operacao_alocada_internamente_unique_tuple UNIQUE NULLS NOT DISTINCT (casamento_operacao_voice_id, registro_NoMe_id, aprovacao_anterior_backoffice_id)
        )
    """
    )

    op.execute(
        """
        ALTER TABLE
            icatu.aprovacao_backoffice
        ADD CONSTRAINT
            aprovacao_backoffice_operacao_fk
        FOREIGN KEY
            (operacao_alocada_internamente_id)
        REFERENCES
            icatu.operacao_alocada_internamente(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.alocacoes_operacao_alocada_internamente (
            id serial8 NOT NULL,
            
            operacao_alocada_internamente_id int8 NOT NULL,
            fundo_id int4 NOT NULL,

            quantidade float8 NOT NULL,
            criado_em timestamp NOT NULL DEFAULT now(),
            
            CONSTRAINT alocacoes_operacao_alocada_internamente_pk PRIMARY KEY (id),

            CONSTRAINT alocacoes_operacao_alocada_internamente_operacao_fk FOREIGN KEY (operacao_alocada_internamente_id) REFERENCES icatu.operacao_alocada_internamente(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT alocacoes_operacao_alocada_internamente_fundo_fk FOREIGN KEY (fundo_id) REFERENCES icatu.fundos(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.atualizacao_custodiante (
            id serial8 NOT NULL,
            casamento_operacao_voice_id int8 NOT NULL,

            registro_NoMe_id int8 NOT NULL,
            status int NOT NULL,
            criado_em timestamp NOT NULL DEFAULT now(),

            CONSTRAINT atualizacao_custodiante_pk PRIMARY KEY (id),
            CONSTRAINT atualizacao_custodiante_casamento_fk FOREIGN KEY (casamento_operacao_voice_id) REFERENCES icatu.casamento_operacao_voice(id) ON DELETE CASCADE ON UPDATE CASCADE,

            CONSTRAINT atualizacao_custodiante_registro_fk FOREIGN KEY (registro_NoMe_id) REFERENCES icatu.registro_NoMe(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.corretoras (
            id serial4 NOT NULL,
            nome text UNIQUE NOT NULL,
            CONSTRAINT corretoras_pk PRIMARY KEY (id)
        )
        """
    )

    op.execute(
        """
        INSERT INTO
            icatu.corretoras
        VALUES
            (1, 'ABC Brasil'),
            (2, 'Alfa CCVM'),
            (3, 'Ativa'),
            (4, 'Banco ABC'),
            (5, 'Banco Alfa'),
            (6, 'Banco do Brasil'),
            (7, 'Banco Pan'),
            (8, 'Banco Paulista'),
            (9, 'Banrisul'),
            (10, 'BB BI'),
            (11, 'BGC'),
            (12, 'BNP Paribas'),
            (13, 'Bocom BBM'),
            (14, 'BR Partners'),
            (15, 'Bradesco'),
            (16, 'Bradesco BBI'),
            (17, 'BTG Pactual'),
            (18, 'BV'),
            (19, 'Caixa'),
            (20, 'Citibank'),
            (21, 'CM Capital'),
            (22, 'Credit Agricole'),
            (23, 'Credit Suisse'),
            (24, 'CSF'),
            (25, 'Daycoval'),
            (26, 'FIDC Alion II'),
            (27, 'Fram Capital'),
            (28, 'Genial'),
            (29, 'GUIDE'),
            (30, 'Industrial'),
            (31, 'Inter'),
            (32, 'Itaú'),
            (33, 'Itaú BBA'),
            (34, 'JP Morgan'),
            (35, 'MAF'),
            (36, 'Mercedes-Benz'),
            (37, 'Mirae'),
            (38, 'Modal'),
            (39, 'Necton'),
            (40, 'OPEA'),
            (41, 'Órama'),
            (42, 'Parana Banco'),
            (43, 'Planner'),
            (44, 'Porto Seguro Financeira'),
            (45, 'Quadra'),
            (46, 'Rabobank'),
            (47, 'RB Capital'),
            (48, 'Renascença'),
            (49, 'Safra'),
            (50, 'Santander'),
            (51, 'Sicredi'),
            (52, 'Singulare'),
            (53, 'Terra'),
            (54, 'Toyota'),
            (55, 'Tribanco'),
            (56, 'UBS BB'),
            (57, 'Votorantim'),
            (58, 'Warren'),
            (59, 'XP')
    """
    )

    op.execute(
        "select setval('icatu.corretoras_id_seq', (select max(id) from icatu.corretoras))"
    )

    op.execute(
        """
        CREATE TABLE icatu.corretoras_id_b3 (
            id serial4 NOT NULL,
            corretora_id serial4 NOT NULL,
            id_b3 text UNIQUE NOT NULL,
            CONSTRAINT corretoras_id_b3_pk PRIMARY KEY (id),
            CONSTRAINT corretoras_corretora_fk FOREIGN KEY (corretora_id) REFERENCES icatu.corretoras(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
    """
    )

    op.execute(
        """
        CREATE TABLE icatu.mensagens_enviadas_post_trade (
            id text NOT NULL,
            casamento_operacao_voice_id int8 NOT NULL,
            registro_nome_id int8 NULL,
            conteudo text NOT NULL,
            erro jsonb NULL,
            criado_em timestamp NOT NULL DEFAULT now(),
            atualizado_em timestamp NOT NULL DEFAULT now(),
            CONSTRAINT mensagens_enviadas_post_trade_pk PRIMARY KEY (id),
            CONSTRAINT mensagens_enviadas_post_trade_casamento_fk FOREIGN KEY (casamento_operacao_voice_id) REFERENCES icatu.casamento_operacao_voice(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT mensagens_enviadas_post_trade_nome_fk FOREIGN KEY (registro_nome_id) REFERENCES icatu.registro_nome(id) ON DELETE SET NULL ON UPDATE CASCADE
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE icatu.mensagens_enviadas_post_trade")
    op.execute("DROP TABLE icatu.corretoras_id_b3")
    op.execute("DROP TABLE icatu.corretoras")
    op.execute("DROP TABLE icatu.atualizacao_custodiante")
    op.execute("DROP TABLE icatu.alocacoes_operacao_alocada_internamente")
    op.execute("DROP TABLE icatu.operacao_alocada_internamente CASCADE")
    op.execute("DROP TABLE icatu.aprovacao_backoffice")
    op.execute("DROP TABLE icatu.registro_NoMe")
    op.execute("DROP TABLE icatu.ratings")
    op.execute("DROP TABLE icatu.agencias_ratings")
    op.execute("DROP TABLE icatu.operacao_capturada")
    op.execute("DROP TABLE icatu.casamento_operacao_voice")
    op.execute("DROP TABLE icatu.codigos_erro_b3_rtc")
