"""fundo_distribuidores

Revision ID: 20240729162547
Revises: 03e0cde5d901
Create Date: 2024-07-29 16:25:47.850399

"""

from typing import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "20240729162547"
down_revision: str | None = "03e0cde5d901"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE icatu.fundo_distribuidores (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT NOT NULL,
            link TEXT NULL,
            instituicao_financeira_id INT,
            CONSTRAINT fundo_distribuidores_instituicao_financeira_fk FOREIGN KEY (instituicao_financeira_id) REFERENCES icatu.instituicoes_financeiras ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE icatu.fundo_distribuidores_fundos (
            fundo_distribuidor_id INT NOT NULL,
            fundo_id INT NOT NULL,
            CONSTRAINT fundo_distribuidores_fundos_pkey PRIMARY KEY (fundo_distribuidor_id, fundo_id),
            CONSTRAINT fundo_distribuidores_fundos_distribuidor_fundo_fk FOREIGN KEY (fundo_distribuidor_id) REFERENCES icatu.fundo_distribuidores ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fundo_distribuidores_fundos_fundo_fk FOREIGN KEY (fundo_id) REFERENCES icatu.fundos ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE site_institucional.fundo_distribuidores_fundos (
            fundo_distribuidor_id INT NOT NULL,
            site_institucional_fundo_id INT NOT NULL,
            CONSTRAINT fundo_distribuidores_fundos_pkey PRIMARY KEY (fundo_distribuidor_id, site_institucional_fundo_id),
            CONSTRAINT site_institucional_fundo_distribuidores_fundos_distribuidor_fundo_fk FOREIGN KEY (fundo_distribuidor_id) REFERENCES icatu.fundo_distribuidores ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT site_institucional_fundo_distribuidores_fundos_fundo_fk FOREIGN KEY (site_institucional_fundo_id) REFERENCES site_institucional.fundos ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE site_institucional.fundo_distribuidores_fundos")
    op.execute("DROP TABLE icatu.fundo_distribuidores_fundos")
    op.execute("DROP TABLE icatu.fundo_distribuidores")
