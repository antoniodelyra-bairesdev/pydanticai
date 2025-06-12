"""Tabelas relacionadas às operações

Revision ID: 0009
Revises: 0008
Create Date: 2024-04-04 19:32:10.149055

"""

from typing import Sequence
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE sistema.arquivos (
            id text PRIMARY KEY,
            provedor text not null,
            conteudo text not null,
            nome text not null,
            extensao text not null,
            CONSTRAINT arquivos_provedor_check CHECK( provedor in ('base64', 'filesystem', 'azure-blob-storage') )
        )
        """
    )
    op.execute(
        """
        CREATE TABLE icatu.fundos_laminas (
            id serial4 PRIMARY KEY,
            fundo_id int4 NOT NULL,
            arquivo_id text UNIQUE NOT NULL,
            data_referencia date NOT NULL,
            criado_em timestamp NOT NULL,
            CONSTRAINT fundos_laminas_fundo_fk FOREIGN KEY (fundo_id) REFERENCES icatu.fundos(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fundos_laminas_arquivo_fk FOREIGN KEY (arquivo_id) REFERENCES sistema.arquivos(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS icatu.fundo_classes_cvm (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            apelido TEXT
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS icatu.fundo_classificacoes_anbima (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            apelido TEXT
        )
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.categoria_relatorio_planos_de_fundo (
            id serial4 PRIMARY KEY,
            conteudo_b64 text NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE icatu.categoria_relatorio (
            id serial4 PRIMARY KEY,
            nome text NOT NULL,
            ordem int4 UNIQUE NOT NULL,
            plano_de_fundo_id int4 NULL,
            CONSTRAINT categoria_relatorio_plano_de_fundo_fk FOREIGN KEY (plano_de_fundo_id) REFERENCES icatu.categoria_relatorio_planos_de_fundo(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE icatu.documento_relatorio (
            id serial4 PRIMARY KEY,
            nome text NOT NULL,
            arquivo_id text UNIQUE NOT NULL,
            categoria_id int4 NOT NULL,
            CONSTRAINT documento_regulatorio_arquivo_fk FOREIGN KEY (arquivo_id) REFERENCES sistema.arquivos(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT documento_regulatorio_categoria_fk FOREIGN KEY (categoria_id) REFERENCES icatu.categoria_relatorio(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute("ALTER TABLE icatu.fundos ALTER COLUMN codigo_brit DROP NOT NULL")
    op.execute("ALTER TABLE icatu.fundos ALTER COLUMN isin DROP NOT NULL")

    op.execute("ALTER TABLE icatu.fundos ALTER COLUMN indice_id DROP NOT NULL")
    op.execute("ALTER TABLE icatu.fundos ALTER COLUMN tipo_id DROP NOT NULL")
    op.execute("ALTER TABLE icatu.fundos ALTER COLUMN risco_id DROP NOT NULL")
    op.execute("ALTER TABLE icatu.fundos ALTER COLUMN classificacao_id DROP NOT NULL")

    op.execute("ALTER TABLE icatu.fundos ALTER COLUMN atualizacao SET DEFAULT now()")

    op.execute(
        """
        CREATE TABLE sistema.site_institucional_classificacoes (
            id SERIAL PRIMARY KEY,
            nome TEXT UNIQUE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE sistema.fundo_site_institucional_classificacoes (
            id SERIAL PRIMARY KEY,
            fundo_id SERIAL UNIQUE REFERENCES icatu.fundos(id),
            site_institucional_classificacao_id SERIAL REFERENCES sistema.site_institucional_classificacoes(id)
        )
        """
    )

    op.execute(
        """
        INSERT INTO sistema.site_institucional_classificacoes (nome)
            VALUES
                ('Renda Fixa'),
                ('Credito Privado'),
                ('Ações'),
                ('Multimercado'),
                ('Imobiliário'),
                ('Ajustado ao Risco'),
                ('Data Alvo')
        """
    )

    op.execute(
        "select setval('sistema.fundo_site_institucional_classificacoes_id_seq', 7)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE sistema.fundo_site_institucional_classificacoes")
    op.execute("DROP TABLE sistema.site_institucional_classificacoes")
    # op.execute("ALTER TABLE icatu.fundos ALTER COLUMN isin SET NOT NULL")
    # op.execute("ALTER TABLE icatu.fundos ALTER COLUMN codigo_brit SET NOT NULL")
    op.execute("DROP TABLE icatu.documento_relatorio")
    op.execute("DROP TABLE icatu.categoria_relatorio")
    op.execute("DROP TABLE icatu.categoria_relatorio_planos_de_fundo")
    op.execute("DROP TABLE icatu.fundo_classificacoes_anbima")
    op.execute("DROP TABLE icatu.fundo_classes_cvm")
    op.execute("DROP TABLE icatu.fundos_laminas")
    op.execute("DROP TABLE sistema.arquivos")
