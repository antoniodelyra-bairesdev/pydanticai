"""Fluxo de operações

Revision ID: 20241029090123
Revises: 20240814125551
Create Date: 2024-10-29 09:01:23.540348
"""

from typing import Sequence

from alembic import op
from os import getenv

# revision identifiers, used by Alembic.
revision: str = "20241029090123"
down_revision: str | None = "20240814125551"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA operacoes")
    op.execute(
        """
        CREATE TABLE operacoes.b3_corretoras (
            id_b3 INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            razao_social TEXT NOT NULL,
            
            corretora_id INTEGER NOT NULL,
            CONSTRAINT b3_corretoras_corretora_id_fk FOREIGN KEY (corretora_id) REFERENCES icatu.corretoras (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE operacoes.b3_mesas (
            id_b3 INTEGER NOT NULL PRIMARY KEY,
            nome TEXT NOT NULL,
            
            b3_corretora_id INTEGER NOT NULL,
            CONSTRAINT b3_mesas_b3_corretora_id_fk FOREIGN KEY (b3_corretora_id) REFERENCES operacoes.b3_corretoras (id_b3) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE operacoes.b3_usuarios (
            id_b3 INTEGER NOT NULL,
            nome TEXT NOT NULL,
            
            b3_mesa_id INTEGER NOT NULL PRIMARY KEY,
            CONSTRAINT b3_usuarios_b3_mesa_id_fk FOREIGN KEY (b3_mesa_id) REFERENCES operacoes.b3_mesas (id_b3) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE icatu.categorias_ativo (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL
        )
        """
    )
    op.execute(
        """
        INSERT INTO
            icatu.categorias_ativo (id, nome)
        VALUES
            (1, 'Títulos Privados')
        """
    )
    op.execute(
        """
        CREATE TABLE icatu.tipos_ativo (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            
            categoria_ativo_id INTEGER NOT NULL,
            CONSTRAINT tipos_ativo_categoria_ativo_id_fk FOREIGN KEY (categoria_ativo_id) REFERENCES icatu.categorias_ativo (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        INSERT INTO
            icatu.tipos_ativo (id, nome, categoria_ativo_id)
        VALUES
            (1, 'BOND', 1),
            (2, 'CDB', 1),
            (3, 'CRA', 1),
            (4, 'CRI', 1),
            (5, 'Debênture', 1),
            (6, 'DPGE', 1),
            (7, 'FIDC', 1),
            (8, 'FII', 1),
            (9, 'LF', 1),
            (10, 'LFS', 1),
            (11, 'LFSC', 1),
            (12, 'LFSN', 1),
            (13, 'NC', 1),
            (14, 'RDB', 1)
        """
    )

    op.execute(
        """
        CREATE TABLE operacoes.natureza_operacao (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL
        )
        """
    )

    op.execute(
        """
        INSERT INTO
            operacoes.natureza_operacao (id, nome)
        VALUES
            (1, 'Externa'),
            (2, 'Interna')
        """
    )

    op.execute(
        """
        CREATE TABLE operacoes.mercado_negociado (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL
        )
        """
    )

    op.execute(
        """
        INSERT INTO
            operacoes.mercado_negociado (id, nome)
        VALUES
            (1, 'Primário'),
            (2, 'Secundário')
        """
    )

    op.execute(
        """
        CREATE TABLE operacoes.boletas (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            data_negociacao DATE NOT NULL,
            data_liquidacao DATE NOT NULL,

            tipo_ativo_id INTEGER NOT NULL,
            natureza_operacao_id INTEGER NOT NULL,
            mercado_negociado_id INTEGER NOT NULL,
            corretora_id INTEGER NOT NULL,
            CONSTRAINT boletas_tipo_ativo_id_fk FOREIGN KEY (tipo_ativo_id) REFERENCES icatu.tipos_ativo (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT boletas_natureza_operacao_id_fk FOREIGN KEY (natureza_operacao_id) REFERENCES operacoes.natureza_operacao (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT boletas_mercado_negociado_id_fk FOREIGN KEY (mercado_negociado_id) REFERENCES operacoes.mercado_negociado (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT boletas_corretora_id_fk FOREIGN KEY (corretora_id) REFERENCES icatu.corretoras (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE operacoes.alocacoes (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            codigo_ativo TEXT NOT NULL,
            vanguarda_compra BOOL NOT NULL,
            preco_unitario DECIMAL(20,8) NOT NULL,
            quantidade DECIMAL(20,8) NOT NULL,
            data_negociacao DATE NOT NULL,
            data_liquidacao DATE NOT NULL,
            alocado_em TIMESTAMP NOT NULL,
            aprovado_em TIMESTAMP,
            corretora_id INTEGER NOT NULL,
            CONSTRAINT alocacoes_corretora_id_fk FOREIGN KEY (corretora_id) REFERENCES icatu.corretoras (id) ON DELETE CASCADE ON UPDATE CASCADE,
            fundo_id INTEGER NOT NULL,
            CONSTRAINT alocacoes_fundo_id_fk FOREIGN KEY (fundo_id) REFERENCES icatu.fundos (id) ON DELETE CASCADE ON UPDATE CASCADE,
            tipo_ativo_id INTEGER NOT NULL,
            CONSTRAINT alocacoes_tipo_ativo_id_fk FOREIGN KEY (tipo_ativo_id) REFERENCES icatu.tipos_ativo (id) ON DELETE CASCADE ON UPDATE CASCADE,
            boleta_id INTEGER NOT NULL,
            CONSTRAINT alocacoes_boleta_id_fk FOREIGN KEY (boleta_id) REFERENCES operacoes.boletas (id) ON DELETE CASCADE ON UPDATE CASCADE,
            alocacao_usuario_id INTEGER NOT NULL,
            CONSTRAINT alocacoes_alocacao_usuario_id_fk FOREIGN KEY (alocacao_usuario_id) REFERENCES auth.usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE,
            aprovacao_usuario_id INTEGER,
            CONSTRAINT alocacoes_aprovacao_usuario_id_fk FOREIGN KEY (aprovacao_usuario_id) REFERENCES auth.usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE,
            alocacao_anterior_id INTEGER,
            CONSTRAINT alocacoes_alocacao_anterior_id_fk FOREIGN KEY (alocacao_anterior_id) REFERENCES operacoes.alocacoes (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE operacoes.alocacoes_administrador (
            alocacao_id INTEGER PRIMARY KEY,
            CONSTRAINT alocacoes_administrador_alocacao_id_fk FOREIGN KEY (alocacao_id) REFERENCES operacoes.alocacoes (id) ON DELETE CASCADE ON UPDATE CASCADE,

            codigo_administrador TEXT,
            alocado_em TIMESTAMP NOT NULL,
            
            alocacao_usuario_id INTEGER NOT NULL,
            CONSTRAINT alocacoes_administrador_alocacao_usuario_id_fk FOREIGN KEY (alocacao_usuario_id) REFERENCES auth.usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE operacoes.cancelamentos_alocacao (
            alocacao_id INTEGER PRIMARY KEY,
            CONSTRAINT cancelamentos_alocacao_alocacao_id_fk FOREIGN KEY (alocacao_id) REFERENCES operacoes.alocacoes (id) ON DELETE CASCADE ON UPDATE CASCADE,

            motivo TEXT,
            cancelado_em TIMESTAMP NOT NULL,
            
            usuario_id INTEGER NOT NULL,
            CONSTRAINT cancelamentos_alocacao_usuario_id_fk FOREIGN KEY (usuario_id) REFERENCES auth.usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE operacoes.cancelamentos_alocacao_administrador (
            alocacao_administrador_id INTEGER PRIMARY KEY,
            CONSTRAINT cancelamentos_alocacao_administrador_alocacao_administrador_id_fk FOREIGN KEY (alocacao_administrador_id) REFERENCES operacoes.alocacoes_administrador (alocacao_id) ON DELETE CASCADE ON UPDATE CASCADE,

            motivo TEXT,
            cancelado_em TIMESTAMP NOT NULL,
            
            usuario_id INTEGER NOT NULL,
            CONSTRAINT cancelamentos_alocacao_administrador_usuario_id_fk FOREIGN KEY (usuario_id) REFERENCES auth.usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE operacoes.liquidacoes_alocacao_administrador (
            alocacao_administrador_id INTEGER PRIMARY KEY,
            CONSTRAINT liquidacoes_alocacao_administrador_alocacao_administrador_id_fk FOREIGN KEY (alocacao_administrador_id) REFERENCES operacoes.alocacoes_administrador (alocacao_id) ON DELETE CASCADE ON UPDATE CASCADE,

            liquidado_em TIMESTAMP NOT NULL,
            
            usuario_id INTEGER NOT NULL,
            CONSTRAINT liquidacoes_alocacao_administrador_usuario_id_fk FOREIGN KEY (usuario_id) REFERENCES auth.usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE operacoes.b3_voices (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

            id_ordem TEXT NOT NULL,
            id_ordem_secundario TEXT NOT NULL,
            id_trader TEXT NOT NULL,

            id_execucao TEXT NOT NULL,

            codigo_ativo TEXT NOT NULL,

            id_instrumento TEXT,
            id_instrumento_subjacente TEXT,

            vanguarda_compra BOOL NOT NULL,
            preco_unitario DECIMAL(20,8) NOT NULL,
            quantidade DECIMAL(20,8) NOT NULL,
            data_negociacao DATE NOT NULL,
            data_liquidacao DATE NOT NULL,
            
            contraparte_b3_corretora_nome TEXT,
            contraparte_b3_mesa_id INTEGER,

            horario_recebimento_order_entry TIMESTAMP,
            horario_recebimento_post_trade TIMESTAMP,

            aprovado_em TIMESTAMP,
            cancelado_em TIMESTAMP
        )
        """
    )

    op.execute(
        """
        CREATE TABLE operacoes.envios_decisao_b3_voice (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            voice_id INTEGER NOT NULL,
            CONSTRAINT envios_decisao_b3_voice_voice_id_fk FOREIGN KEY (voice_id) REFERENCES operacoes.b3_voices (id) ON DELETE CASCADE ON UPDATE CASCADE,

            sequencia_fix INTEGER NOT NULL,

            decisao TEXT NOT NULL,
            enviado_em TIMESTAMP NOT NULL,
            processamento_em TIMESTAMP,
            erro_em TIMESTAMP,
            detalhes_erro TEXT,
            
            usuario_id INTEGER NOT NULL,
            CONSTRAINT envios_decisao_b3_voice_usuario_id_fk FOREIGN KEY (usuario_id) REFERENCES auth.usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE operacoes.casamento_alocacoes_b3_voice (
            voice_id INTEGER PRIMARY KEY,
            CONSTRAINT casamento_alocacoes_b3_voice_voice_id_fk FOREIGN KEY (voice_id) REFERENCES operacoes.b3_voices (id) ON DELETE CASCADE ON UPDATE CASCADE,

            casado_em TIMESTAMP NOT NULL,

            usuario_id INTEGER NOT NULL,
            CONSTRAINT casamento_alocacoes_b3_voice_usuario_id_fk FOREIGN KEY (usuario_id) REFERENCES auth.usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE operacoes.alocacoes_casamentos (
            alocacao_id INTEGER PRIMARY KEY,
            CONSTRAINT alocacoes_casamentos_alocacao_id_fk FOREIGN KEY (alocacao_id) REFERENCES operacoes.alocacoes (id) ON DELETE CASCADE ON UPDATE CASCADE,

            casamento_id INTEGER NOT NULL,
            CONSTRAINT alocacoes_casamentos_casamento_id_fk FOREIGN KEY (casamento_id) REFERENCES operacoes.casamento_alocacoes_b3_voice (voice_id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE operacoes.envios_alocacao_b3_voice (
            id TEXT PRIMARY KEY,
            voice_id INTEGER NOT NULL,
            CONSTRAINT envios_alocacao_b3_voice_voice_id_fk FOREIGN KEY (voice_id) REFERENCES operacoes.b3_voices (id) ON DELETE CASCADE ON UPDATE CASCADE,

            enviado_em TIMESTAMP NOT NULL,
            erro_em TIMESTAMP,
            detalhes_erro TEXT,
            sucesso_em TIMESTAMP,

            usuario_id INTEGER NOT NULL,
            CONSTRAINT envios_alocacao_b3_voice_usuario_id_fk FOREIGN KEY (usuario_id) REFERENCES auth.usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE,

            conteudo TEXT NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE operacoes.b3_registros_nome (
            alocacao_id INTEGER PRIMARY KEY,
            CONSTRAINT registros_nome_alocacao_id_fk FOREIGN KEY (alocacao_id) REFERENCES operacoes.alocacoes (id) ON DELETE CASCADE ON UPDATE CASCADE,

            numero_controle TEXT NOT NULL,
            data DATE NOT NULL,
            
            recebido_em TIMESTAMP NOT NULL,
            
            posicao_custodia BOOL,
            posicao_custodia_em TIMESTAMP,

            posicao_custodia_contraparte BOOL,
            posicao_custodia_contraparte_em TIMESTAMP
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE icatu.tipos_ativo CASCADE")
    op.execute("DROP TABLE icatu.categorias_ativo CASCADE")
    op.execute("DROP SCHEMA operacoes CASCADE")
