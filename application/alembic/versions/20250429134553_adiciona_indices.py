"""Adiciona estrutura de indices, moedas, fontes de dados e preços de indices

Revision ID: 78a05a51fabc
Revises: 20250127110302
Create Date: 2025-04-29 13:45:53.102357

"""

from typing import Sequence
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "78a05a51fabc"
down_revision: str | None = "20250127110302"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # op.execute(
    #     """
    #     INSERT INTO auth.usuarios (nome, email, senha) VALUES
    #         ('Airflow', '_airflow_', '$argon2id$v=19$m=65536,t=3,p=4$b7wXYBsd7CcXxmyVOLlYQQ$3ydt9HCd38DTdOtziaDL77cMllCZ19BnI97rWfmiOwM')
    #     """
    # )
    op.execute(
        """
        CREATE TABLE icatu.fornecedores(
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT UNIQUE NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE icatu.fontes_dados(
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            fornecedor_id INTEGER NOT NULL,
            nome TEXT NULL,

            CONSTRAINT unique_fornecedor_id_nome UNIQUE (fornecedor_id, nome),
            CONSTRAINT fontes_dados_fornecedor_id_fk FOREIGN KEY (fornecedor_id) REFERENCES icatu.fornecedores (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE icatu.moedas(
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT UNIQUE NOT NULL,
            codigo VARCHAR(3) NOT NULL,
            simbolo VARCHAR(3) NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE icatu.medidas(
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            
            nome TEXT UNIQUE NOT NULL,
            descricao TEXT NULL,
            abreviacao TEXT NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE icatu.moedas_cotacoes(
            id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

            moeda_id INTEGER NOT NULL,
            fonte_dado_id INTEGER NOT NULL,

            data_referente DATE NOT NULL,
            cotacao DECIMAL NOT NULL,

            CONSTRAINT moedas_cotacoes_moeda_id_fk FOREIGN KEY (moeda_id) REFERENCES icatu.moedas (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT moedas_cotacoes_fonte_dado_id_fk FOREIGN KEY (fonte_dado_id) REFERENCES icatu.fontes_dados (id) ON DELETE CASCADE ON UPDATE CASCADE,

            CONSTRAINT unique_moeda_id_data_referente UNIQUE (data_referente, cotacao) 
        )
        """
    )
    op.execute(
        """
        CREATE TABLE icatu.indices(
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

            moeda_principal_id INTEGER NULL,
            fonte_dado_principal_id INTEGER NOT NULL,
            medida_id INTEGER NOT NULL,

            nome TEXT UNIQUE NOT NULL,
            descricao TEXT NULL,
            is_sintetico BOOLEAN,
            data_inicio_coleta DATE DEFAULT '2000-01-03',
            atraso_coleta_dias INTEGER,

            CONSTRAINT indices_moeda_principal_id_fk FOREIGN KEY (moeda_principal_id) REFERENCES icatu.moedas(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT indices_fonte_dado_principal_id_fk FOREIGN KEY (fonte_dado_principal_id) REFERENCES icatu.fontes_dados ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT indices_medida_id_fk FOREIGN KEY (medida_id) REFERENCES icatu.medidas ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE icatu.indices_identificadores(
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            indice_id INTEGER NOT NULL,
            fonte_dado_id INTEGER NOT NULL,
            
            codigo TEXT NOT NULL,
            descricao TEXT NULL,

            CONSTRAINT indices_identificadores_indice_id_fk FOREIGN KEY (indice_id) REFERENCES icatu.indices (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT indices_identificadores_fonte_dado_id_fk FOREIGN KEY (fonte_dado_id) REFERENCES icatu.fontes_dados (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT unique_indice_id_fonte_dado_id UNIQUE(indice_id, fonte_dado_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE icatu.indices_cotacoes(
            id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            indice_id INTEGER NOT NULL,
            fonte_dado_id INTEGER NOT NULL,
            moeda_id INTEGER NOT NULL,

            data_referente DATE NOT NULL,
            cotacao DECIMAL NOT NULL,

            CONSTRAINT indices_cotacoes_indice_id_fk FOREIGN KEY (indice_id) REFERENCES icatu.indices (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT indices_cotacoes_fonte_dado_id_fk FOREIGN KEY (fonte_dado_id) REFERENCES icatu.fontes_dados (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT indices_cotacoes_moeda_id_fk FOREIGN KEY (moeda_id) REFERENCES icatu.moedas (id) ON DELETE CASCADE ON UPDATE CASCADE,

            CONSTRAINT unique_indice_id_medida_id_moeda_id_fonte_dado_id_data_referente UNIQUE (indice_id, moeda_id, data_referente)
        )
        """
    )
    op.execute("INSERT INTO icatu.fornecedores (nome) VALUES ('ComDinheiro')")
    op.execute("INSERT INTO icatu.fontes_dados (fornecedor_id, nome) VALUES (1, 'API')")
    op.execute(
        """
        INSERT INTO icatu.moedas (codigo, nome, simbolo) VALUES
            ('BRL', 'Real Brasileiro', 'R$'),
            ('USD', 'Dólar Americano', '$'),
            ('EUR', 'Euro', '€')
        """
    )
    op.execute(
        """
        INSERT INTO icatu.medidas(nome, descricao, abreviacao) VALUES
            ('Pontos', NULL, 'pts.')
        """
    )
    op.execute(
        """
        INSERT INTO icatu.indices (nome, moeda_principal_id, fonte_dado_principal_id, medida_id, is_sintetico, data_inicio_coleta, atraso_coleta_dias) VALUES 
            ('CDI', 1, 1, 1, TRUE, DEFAULT, 1),
            ('IBOVESPA', 1, 1, 1, FALSE, DEFAULT, 1),
            ('IBRX', 1, 1, 1, FALSE, DEFAULT, 1),
            ('IFIX', 1, 1, 1, FALSE, '2010-12-30', 1),
            ('IHFA', 1, 1, 1, TRUE, '2007-09-28', 3),
            ('IMAB', 1, 1, 1, TRUE, '2003-09-16', 1),
            ('IMAB5', 1, 1, 1, TRUE, '2003-09-16', 1),
            ('IMAB5+', 1, 1, 1, TRUE, '2003-09-16', 1),
            ('IMAS', 1, 1, 1, TRUE, '2001-12-03', 1),
            ('INPC Estimado', 1, 1, 1, TRUE, DEFAULT, 1),
            ('IPCA Projetado', 1, 1, 1, TRUE, DEFAULT, 1),
            ('IRFM', 1, 1, 1, TRUE, '2000-02-01', 1),
            ('IRFM1+', 1, 1, 1, TRUE, '2000-02-01', 1),
            ('MSCI WORLD', 2, 1, 1, FALSE, DEFAULT, 1),
            ('NASDAQ', 2, 1, 1, FALSE, DEFAULT, 1),
            ('SMLL', 1, 1, 1, FALSE, '2005-06-09', 1),
            ('SP500', 2, 1, 1, FALSE, DEFAULT, 1),
            ('MSCI ACWI', 2, 1, 1, FALSE, DEFAULT, 1),
            ('SELIC', 1, 1, 1, TRUE, DEFAULT, 1),
            ('IMA GERAL', 1, 1, 1, FALSE, '2001-12-04', 1),
            ('MSCI WORLD TOTAL RETURN', 2, 1, 1, FALSE, DEFAULT, 1)
        """
    )
    op.execute(
        """
        INSERT INTO icatu.indices_identificadores (indice_id, fonte_dado_id, codigo, descricao) VALUES
            (1, 1, 'CDI', NULL),
            (2, 1, 'IBOV', NULL),
            (3, 1, 'IBRX', NULL),
            (4, 1, 'IFIX', NULL),
            (5, 1, 'ANBIMA_IHFA', NULL),
            (6, 1, 'ANBIMA_IMAB', NULL),
            (7, 1, 'ANBIMA_IMAB5', NULL),
            (8, 1, 'ANBIMA_IMAB5+', NULL),
            (9, 1, 'ANBIMA_IMAS', NULL),
            (10, 1, 'IBGE_INPCD', NULL),
            (11, 1, 'IPCADP', NULL),
            (12, 1, 'ANBIMA_IRFM', NULL),
            (13, 1, 'ANBIMA_IRFM1+', NULL),
            (14, 1, 'US:MSCI_WORLD', NULL),
            (15, 1, 'US:NASDAQ', NULL),
            (16, 1, 'SMLL', NULL),
            (17, 1, 'US:SP500', NULL),
            (18, 1, 'US:MSCI_ACWI', NULL),
            (19, 1, 'SELIC', NULL),
            (20, 1, 'ANBIMA_IMAG', NULL),
            (21, 1, 'US:MSCI_WORLD_NET', NULL)
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE icatu.indices_cotacoes CASCADE")
    op.execute("DROP TABLE icatu.indices_identificadores CASCADE")
    op.execute("DROP TABLE icatu.moedas_cotacoes CASCADE")
    op.execute("DROP TABLE icatu.fontes_dados CASCADE")
    op.execute("DROP TABLE icatu.fornecedores CASCADE")
    op.execute("DROP TABLE icatu.indices CASCADE")
    op.execute("DROP TABLE icatu.medidas CASCADE")
    op.execute("DROP TABLE icatu.moedas CASCADE")
