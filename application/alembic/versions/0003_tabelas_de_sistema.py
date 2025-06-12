"""Tabelas de sistema

Revision ID: 0003
Revises: 0002
Create Date: 2024-01-03 17:41:14.566898

"""
from typing import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("create schema sistema")
    op.execute(
        """
        CREATE TABLE sistema.emissor_setor_icone (
            setor_id serial4 NOT NULL,
            icone text NOT NULL,
            CONSTRAINT emissor_setor_icone_pk PRIMARY KEY (setor_id)
        );
        """
    )
    op.execute(
        """
        insert into
            sistema.emissor_setor_icone (setor_id, icone)
        values
            (23, 'FastFood'),       -- Alimentos e Bebidas
            (30, 'Card'),           -- Bancos
            (20, 'Car'),            -- Conc. Rodoviária
            (31, 'School'),         -- Educação
            (27, 'Flash'),          -- Elétrico - Distribuição
            (14, 'Flash'),          -- Elétrico - Geração
            (18, 'Flash'),          -- Elétrico - Holding
            (22, 'Flash'),          -- Elétrico - Transmissão
            (19, 'Leaf'),           -- Gestão ambiental
            (29, 'People'),         -- Holding
            (13, 'Cog'),            -- Indústria e Bens de Capital
            (28, 'Analytics'),      -- Logística
            (7, 'Diamond'),         -- Mineração e siderurgia
            (5, 'Bus'),         	-- Mobilidade Urbana
            (9, 'Document'),  	    -- Papel e Celulose
            (25, 'Flask'),    	    -- Petroquímico
            (4, 'Boat'),     	    -- Portos
            (24, 'Business'), 	    -- Real Estate
            (6, 'Cash'),    	    -- Rental
            (12, 'Water'),    	    -- Saneamento
            (17, 'Heart'),    	    -- Saúde
            (10, 'Documents'),   	-- Securitizadora
            (3, 'DocumentLock'),	-- Seguros
            (8, 'Hammer'),   	    -- Serviço
            (21, 'Wallet'),   	    -- Serviços Financeiros
            (16, 'BagHandle'),	    -- Shopping Center
            (15, 'Call'),     	    -- Telecom
            (26, 'Pricetags'),	    -- Varejo
            (11, 'Flame')           -- Óleo e Gás
        """
    )
    op.execute(
        "select setval('sistema.emissor_setor_icone_setor_id_seq', max(esi.setor_id)+1, false) from sistema.emissor_setor_icone esi"
    )


def downgrade() -> None:
    op.execute("drop table sistema.emissor_setor_icone")
    op.execute("drop schema sistema")
