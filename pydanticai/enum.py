"""
Enum com mapeamento de strings para as classes de schema FIDC.

Este módulo fornece um Enum que mapeia strings para as principais classes
de relatório de cada schema FIDC, permitindo acesso dinâmico aos modelos.
"""

from enum import Enum
from pydantic import BaseModel

# Importar as classes principais de cada schema
from .schema.fidc.bemol import RelatorioFIDCBemol
from .schema.fidc.brz_consignados_v import RelatorioFIDCBRZConsignadosV
from .schema.fidc.icred import RelatorioFIDCICredImage
from .schema.fidc.sol_agora_iii import RelatorioFIDCSolAgoraIII
from .schema.fidc.somacred import RelatorioCompletoSomacred
from .schema.fidc.valora_alion_ii import RelatorioFIDCValoraAlion
from .schema.fidc.valora_noto import RelatorioFIDCValoraNoto
from .schema.fidc.verde_card import RelatorioFIDCVerdeCard


class Default(BaseModel):
    """Classe padrão para respostas simples."""

    resposta: str


class ModelSchemaEnum(Enum):
    """
    Enum que mapeia strings para as classes de schema FIDC.

    Permite acesso dinâmico aos modelos através de strings.
    """

    # Classe padrão
    default = Default

    # Mapeamento principal usando nomes dos arquivos em minúsculo
    bemol = RelatorioFIDCBemol
    brz_consignados_v = RelatorioFIDCBRZConsignadosV
    icred = RelatorioFIDCICredImage
    sol_agora_iii = RelatorioFIDCSolAgoraIII
    somacred = RelatorioCompletoSomacred
    valora_alion_ii = RelatorioFIDCValoraAlion
    valora_noto = RelatorioFIDCValoraNoto
    verde_card = RelatorioFIDCVerdeCard

    @classmethod
    def get_schema_class(cls, schema_name: str):
        """
        Retorna a classe de schema baseada no nome fornecido.

        Args:
            schema_name: Nome do schema (string)

        Returns:
            Classe do schema correspondente

        Raises:
            ValueError: Se o schema_name não for encontrado
        """
        try:
            return cls[schema_name.lower()].value
        except KeyError:
            available_schemas = ", ".join([member.name for member in cls])
            raise ValueError(
                f"Schema '{schema_name}' não encontrado. Schemas disponíveis: {available_schemas}"
            )

    @classmethod
    def get_available_schemas(cls):
        """
        Retorna uma lista com todos os nomes de schema disponíveis.

        Returns:
            Lista de strings com os nomes dos schemas
        """
        return [member.name for member in cls]

    @classmethod
    def get_by_name(cls, name: str):
        """
        Retorna o enum member baseado no nome.

        Args:
            name: Nome do schema (case insensitive)

        Returns:
            Enum member correspondente
        """
        return cls[name.lower()]


# Dicionário de conveniência para acesso direto
MODEL_SCHEMA_MAPPING = {member.name: member.value for member in ModelSchemaEnum}


def get_schema_class(schema_name: str):
    """
    Função de conveniência para obter a classe de schema.

    Args:
        schema_name: Nome do schema (string)

    Returns:
        Classe do schema correspondente
    """
    return ModelSchemaEnum.get_schema_class(schema_name)


def get_available_schemas():
    """
    Função de conveniência para listar schemas disponíveis.

    Returns:
        Lista de strings com os nomes dos schemas
    """
    return ModelSchemaEnum.get_available_schemas()
