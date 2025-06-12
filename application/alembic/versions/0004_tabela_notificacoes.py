"""Tabela de notificações

Revision ID: 0004
Revises: 0003
Create Date: 2024-01-19 16:57:35.852738

"""
from alembic import op
from typing import Sequence


revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        create table sistema.notificacoes (
            id serial4 primary key,
            user_id smallint not null,
            text text not null,
            link text,
            created_at timestamp default now() not null,
            constraint fk_user_id foreign key (user_id) references auth.usuarios(id)
        )
    """
    )


def downgrade() -> None:
    op.execute("drop table sistema.notificacoes")
