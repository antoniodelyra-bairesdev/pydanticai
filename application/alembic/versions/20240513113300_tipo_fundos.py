"""Tabelas relacionadas às operações

Revision ID: 20240513113300
Revises: 0009
Create Date: 2024-05-13 11:33:00.123497

"""

from typing import Sequence
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "20240513113300"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE sistema.site_institucional_fundo_tipos (
            id serial4 PRIMARY KEY,
            nome text unique not null
        )
        """
    )

    op.execute(
        """
        INSERT INTO sistema.site_institucional_fundo_tipos (nome) VALUES
            ('Fundo de Investimento'),
            ('Fundo de Previdência (FIE)'),
            ('Fundo de Previdência (FIFE)')
        """
    )

    op.execute("select setval('sistema.site_institucional_fundo_tipos_id_seq', 3)")

    op.execute(
        """
        ALTER TABLE
            sistema.fundo_site_institucional_classificacoes
        ADD COLUMN
            site_institucional_tipo_id int4
        CONSTRAINT
            fundo_site_institucional_fundo_classificacoes_tipo_fk
        REFERENCES
            sistema.site_institucional_fundo_tipos(id)
        ON UPDATE
            CASCADE
        ON DELETE
            CASCADE
        DEFAULT 1
        """
    )

    op.execute(
        """
        INSERT INTO auth.funcoes (nome) VALUES
            ('Fundos - Alterar documentação'),
            ('Site Institucional - Alterar fundos'),
            ('Site Institucional - Alterar documentos regulatórios')
    """
    )

    op.execute(
        "select setval('auth.funcoes_id_seq', (select max(id) from auth.funcoes))"
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE from auth.funcoes
        WHERE nome IN (
            'Fundos - Alterar documentação',
            'Site Institucional - Alterar fundos',
            'Site Institucional - Alterar documentos regulatórios'
        )
    """
    )
    op.execute(
        "select setval('auth.funcoes_id_seq', (select max(id) from auth.funcoes))"
    )
    op.execute(
        "ALTER TABLE sistema.fundo_site_institucional_classificacoes DROP CONSTRAINT fundo_site_institucional_fundo_classificacoes_tipo_fk"
    )
    op.execute(
        "ALTER TABLE sistema.fundo_site_institucional_classificacoes DROP COLUMN site_institucional_tipo_id"
    )
    op.execute("DROP TABLE sistema.site_institucional_fundo_tipos")
