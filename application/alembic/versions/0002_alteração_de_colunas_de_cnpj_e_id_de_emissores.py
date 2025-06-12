"""Alteração de colunas de cnpj e id de emissores

Revision ID: 0002
Revises: 0001
Create Date: 2023-12-27 16:40:41.605563

"""
from typing import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1
    op.execute("ALTER TABLE icatu.emissores RENAME COLUMN cnpj TO id")
    op.execute("ALTER TABLE icatu.emissores ADD cnpj bpchar(14) NULL")
    op.execute("update icatu.emissores set cnpj = id")
    op.execute("ALTER TABLE icatu.emissores ALTER COLUMN cnpj SET NOT NULL;")

    # 2
    op.execute("ALTER TABLE icatu.ativos DROP CONSTRAINT ativos_emissor_cnpj_fkey")
    op.execute("ALTER TABLE icatu.ativos RENAME COLUMN emissor_cnpj TO emissor_id")

    # 3
    op.execute(
        "ALTER TABLE icatu.ativos ALTER COLUMN emissor_id TYPE int8 USING emissor_id::int8"
    )
    op.execute("ALTER TABLE icatu.emissores ALTER COLUMN id TYPE int8 USING id::int8")

    # 4
    op.execute("create sequence icatu.emissor_id_seq owned by icatu.emissores.id")
    op.execute(
        "select setval('icatu.emissor_id_seq', count(*)+1, false) from icatu.emissores"
    )
    op.execute(
        "alter table icatu.emissores alter column id set default nextval('icatu.emissor_id_seq')"
    )

    # 5
    op.execute(
        "alter table icatu.ativos add CONSTRAINT ativos_emissor_id_fkey FOREIGN KEY (emissor_id) REFERENCES icatu.emissores(id) on update cascade"
    )

    # 6
    op.execute(
        """
        update icatu.emissores e
        set id = s.new_position
        from (
            select
                cnpj,
                (row_number() over (order by cnpj)) as new_position
            from
                icatu.emissores
        ) s
        where e.cnpj = s.cnpj
    """
    )


def downgrade() -> None:
    # 6
    op.execute("update icatu.emissores e set id = -id")
    op.execute("update icatu.emissores e set id = cnpj::int8")

    # 5
    op.execute("alter table icatu.ativos drop constraint ativos_emissor_id_fkey")

    # 4
    op.execute("alter table icatu.emissores alter column id drop default")
    op.execute("drop sequence icatu.emissor_id_seq")

    # 3
    op.execute(
        "ALTER TABLE icatu.emissores ALTER COLUMN id TYPE bpchar(14) USING id::bpchar(14)"
    )
    op.execute("update icatu.emissores set id = lpad(replace(id, ' ', ''), 14, '0')")
    op.execute(
        "ALTER TABLE icatu.ativos ALTER COLUMN emissor_id TYPE bpchar(14) USING emissor_id::bpchar(14)"
    )
    op.execute(
        "update icatu.ativos set emissor_id = lpad(replace(emissor_id, ' ', ''), 14, '0')"
    )

    # 2
    op.execute("ALTER TABLE icatu.ativos RENAME COLUMN emissor_id TO emissor_cnpj")
    op.execute(
        "ALTER TABLE icatu.ativos ADD CONSTRAINT ativos_emissor_cnpj_fkey FOREIGN KEY (emissor_cnpj) REFERENCES icatu.emissores(id) ON UPDATE CASCADE"
    )

    # 1
    op.execute("ALTER TABLE icatu.emissores ALTER COLUMN cnpj DROP NOT NULL")
    op.execute("update icatu.emissores set id = cnpj")
    op.execute("ALTER TABLE icatu.emissores DROP COLUMN cnpj")
    op.execute("ALTER TABLE icatu.emissores RENAME COLUMN id TO cnpj")
