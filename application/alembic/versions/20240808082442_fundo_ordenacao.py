"""fundo_distribuidores

Revision ID: 20240808082442
Revises: 20240729162547
Create Date: 2024-07-29 16:25:47.850399

"""

from typing import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "20240808082442"
down_revision: str | None = "20240729162547"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE site_institucional.fundos ADD COLUMN ordenacao int4 NOT NULL DEFAULT 0"
    )
    op.execute("ALTER TABLE site_institucional.fundos ADD COLUMN data_inicio DATE")
    op.execute(
        "ALTER TABLE site_institucional.fundos ADD COLUMN taxa_administracao_maxima TEXT NULL"
    )
    op.execute(
        "ALTER TABLE icatu.fundos ADD COLUMN taxa_administracao_maxima TEXT NULL"
    )

    op.execute(
        "ALTER TABLE site_institucional.fundos ALTER COLUMN cotizacao_resgate DROP NOT NULL"
    )
    op.execute(
        "ALTER TABLE site_institucional.fundos ALTER COLUMN cotizacao_resgate_sao_dias_uteis DROP NOT NULL"
    )
    op.execute(
        "ALTER TABLE site_institucional.fundos ALTER COLUMN cotizacao_resgate_detalhes DROP NOT NULL"
    )
    op.execute(
        "ALTER TABLE site_institucional.fundos ALTER COLUMN financeiro_resgate DROP NOT NULL"
    )
    op.execute(
        "ALTER TABLE site_institucional.fundos ALTER COLUMN financeiro_resgate_sao_dias_uteis DROP NOT NULL"
    )
    op.execute(
        "ALTER TABLE site_institucional.fundos ALTER COLUMN financeiro_resgate_detalhes DROP NOT NULL"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE icatu.fundos DROP COLUMN taxa_administracao_maxima")
    op.execute(
        "ALTER TABLE site_institucional.fundos DROP COLUMN taxa_administracao_maxima"
    )
    op.execute("ALTER TABLE site_institucional.fundos DROP COLUMN data_inicio")
    op.execute("ALTER TABLE site_institucional.fundos DROP COLUMN ordenacao")
