"""Fluxo de operações

Revision ID: 20250127110302
Revises: 20241029090123
Create Date: 2025-01-27 11:03:02.038530
"""

from typing import Sequence
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20250127110302"
down_revision: str | None = "20241029090123"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA financeiro")
    op.execute(
        """
        CREATE TABLE financeiro.inquilinos (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            razao_social TEXT UNIQUE NOT NULL,
            cnpj CHAR(14) UNIQUE NOT NULL,
            cep CHAR(8) NOT NULL,
            logradouro text NOT NULL,
            bairro text NOT NULL,
            cidade text NOT NULL,
            estado CHAR(2) NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE financeiro.contratos_locacao (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            fundo_id INTEGER NOT NULL,
            inquilino_id INTEGER NOT NULL,
            
            dia_vencimento INTEGER NOT NULL,
            percentual_juros_mora_ao_mes FLOAT8 NOT NULL,

            CONSTRAINT contratos_locacao_fundo_id_fk FOREIGN KEY (fundo_id) REFERENCES icatu.fundos (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT contratos_locacao_inquilino_id_fk FOREIGN KEY (inquilino_id) REFERENCES financeiro.inquilinos (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE financeiro.multa_mora (
            contrato_locacao_id INTEGER NOT NULL,
            dias_a_partir_vencimento INTEGER NOT NULL,
            percentual_sobre_valor FLOAT8 NOT NULL,

            CONSTRAINT multa_mora_pk PRIMARY KEY (contrato_locacao_id, dias_a_partir_vencimento),
            CONSTRAINT multa_mora_contrato_locacao_id_fk FOREIGN KEY (contrato_locacao_id) REFERENCES financeiro.contratos_locacao (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE financeiro.tipos_execucao_daycoval (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE financeiro.execucao_daycoval (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            
            inicio TIMESTAMP NOT NULL,
            fim TIMESTAMP NULL,
            erro TEXT NULL,
            
            tipo_execucao_id INTEGER NOT NULL,
            CONSTRAINT execucao_daycoval_tipo_execucao_id_fk FOREIGN KEY (tipo_execucao_id) REFERENCES financeiro.tipos_execucao_daycoval (id) ON DELETE CASCADE ON UPDATE CASCADE,

            usuario_id INTEGER NOT NULL,
            CONSTRAINT execucao_daycoval_usuario_id_fk FOREIGN KEY (usuario_id) REFERENCES auth.usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE financeiro.passo_execucao_daycoval (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            nome TEXT NOT NULL,
            inicio TIMESTAMP NOT NULL,
            fim TIMESTAMP NULL,
            erro TEXT NULL,

            execucao_daycoval_id INTEGER NOT NULL,
            CONSTRAINT passo_execucao_daycoval_execucao_daycoval_id_fk FOREIGN KEY (execucao_daycoval_id) REFERENCES financeiro.execucao_daycoval (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE financeiro.dados_execucao_daycoval (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            identificador_titulo CHAR(25) UNIQUE NOT NULL,
            identificador_documento_cobranca CHAR(10) UNIQUE NOT NULL,
            
            vencimento DATE NOT NULL,
            valor FLOAT8 NOT NULL,
            percentual_juros_mora_ao_mes FLOAT8 NOT NULL,
            percentual_sobre_valor_multa_mora FLOAT8 NOT NULL,

            conteudo_arquivo_remessa TEXT NULL,
            nome_arquivo_remessa TEXT NULL,
            nome_arquivo_retorno TEXT NULL,
            arquivo_id_boleto_parcial_pdf TEXT NULL,
            conteudo_arquivo_retorno TEXT NULL,
            arquivo_id_boleto_completo_pdf TEXT NULL,

            contrato_id INTEGER NOT NULL,
            CONSTRAINT dados_execucao_daycoval_contrato_id_fk FOREIGN KEY (contrato_id) REFERENCES financeiro.contratos_locacao (id) ON DELETE CASCADE ON UPDATE CASCADE,
            execucao_daycoval_id INTEGER NOT NULL,
            CONSTRAINT dados_execucao_daycoval_execucao_daycoval_id_fk FOREIGN KEY (execucao_daycoval_id) REFERENCES financeiro.execucao_daycoval (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP SCHEMA financeiro CASCADE")
