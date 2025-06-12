"""fundo_distribuidores

Revision ID: 20240814125551
Revises: 20240808082442
Create Date: 2024-07-29 12:55:51.850529

"""

from typing import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "20240814125551"
down_revision: str | None = "20240808082442"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "INSERT INTO auth.funcoes(nome) VALUES ('Site Institucional - Carregar arquivo de rentabilidades')"
    )
    op.execute(
        """
        INSERT INTO auth.usuarios_funcoes(usuario_id, funcao_id)
            SELECT auth.usuarios.id, auth.funcoes.id FROM auth.usuarios, auth.funcoes WHERE auth.usuarios.email = 'admin@icatuvanguarda.com.br'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM auth.usuarios_funcoes WHERE
            auth.usuarios_funcoes.usuario_id = 1 AND
            auth.usuarios_funcoes.funcao_id IN (SELECT auth.funcoes.id FROM auth.funcoes)
        """
    )
    op.execute(
        "DELETE FROM auth.funcoes WHERE nome = 'Site Institucional - Carregar arquivo de rentabilidades'"
    )
