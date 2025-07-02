# FIDC Somacred - Modelos de Resposta da API
# ---------------------------------------------------
# Este arquivo contém as classes Pydantic que definem a estrutura de dados
# esperada para o relatório do Fundo de Investimento em Direitos Creditórios (FIDC) Somacred.
#
# Características do fundo:
# - Foco em crédito consignado público (servidores federais).
# - Cedentes: Sabemi e Sabemi Previdência Privada.
# - Gestão e Administração: Oliveira Trust.
#
# Estas classes são usadas como `response_model` no FastAPI para garantir
# a tipagem, validação e documentação automática dos dados da API.

import re
from typing import List
from pydantic import Field, field_validator

# Supondo que ValidatedModel está em um local acessível, como 'modules.util.validators'
from modules.util.validators import ValidatedModel


# --- Seção: Dados Cadastrais ---
class DadosCadastraisSomacred(ValidatedModel):
    """Informações básicas e de identificação do fundo Somacred."""

    cnpj: str = Field(..., description="CNPJ do fundo no formato XX.XXX.XXX/XXXX-XX.")
    objetivo_fundo: str = Field(
        ..., description="Objetivo principal do fundo, conforme regulamento."
    )
    classificacao_anbima: str = Field(
        ..., description="Classificação do fundo segundo os critérios da ANBIMA."
    )
    forma_constituicao: str = Field(
        ..., description="Forma de constituição do fundo (ex: Condomínio Fechado)."
    )
    inicio_fundo: str = Field(..., description="Data de início das operações do fundo.")
    prazo_fundo: str = Field(..., description="Prazo de duração do fundo (ex: Indeterminado).")
    taxa_administracao: str = Field(
        ..., description="Descrição da política de taxa de administração do fundo."
    )
    administrador: str = Field(..., description="Nome da instituição administradora do fundo.")
    gestor: str = Field(..., description="Nome da instituição gestora do fundo.")
    custodiante: str = Field(..., description="Nome da instituição custodiante dos ativos.")
    auditor: str = Field(..., description="Empresa responsável pela auditoria externa do fundo.")
    consultora_especializada: str = Field(
        ..., description="Nome da consultoria especializada contratada pelo fundo."
    )
    cedentes: str = Field(..., description="Empresas originadoras dos direitos creditórios.")
    coobrigacao_cedentes: str = Field(
        ..., description="Indica se há coobrigação por parte dos cedentes."
    )
    entes_publicos_conveniados: str = Field(
        ..., description="Lista de entes públicos conveniados para o crédito consignado."
    )

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, v: str) -> str:
        """Valida se o CNPJ está no formato correto."""
        if not re.match(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", v):
            raise ValueError("Formato de CNPJ inválido. Use XX.XXX.XXX/XXXX-XX.")
        return v


# --- Seção: Indicadores de Acompanhamento ---
class IndiceAcompanhamento(ValidatedModel):
    """Estrutura para os indicadores de acompanhamento e risco do fundo."""

    nome: str = Field(
        ...,
        description="Nome do indicador de acompanhamento.",
    )
    limite: str = Field(
        ...,
        description="Critério ou limite estabelecido para o indicador.",
    )
    valor: float = Field(..., description="Valor atual apurado para o indicador.")

    @field_validator("valor")
    @classmethod
    def validate_valor_not_negative(cls, v: float) -> float:
        """Valida que o valor do indicador não seja negativo."""
        if v < 0:
            raise ValueError("O valor do indicador não pode ser negativo.")
        return v

    @field_validator("nome", "limite")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        """Valida que os campos de texto não sejam vazios."""
        if not v.strip():
            raise ValueError("O campo não pode ser vazio.")
        return v.strip()


# --- Modelo Principal: Estrutura Completa do Relatório ---
class RelatorioCompletoSomacred(ValidatedModel):
    """
    Modelo raiz que agrega todos os componentes do relatório do FIDC Somacred.
    Esta é a classe principal a ser usada como `response_model` na API.
    """

    dados_cadastrais: DadosCadastraisSomacred
    indices_acompanhamento: List[IndiceAcompanhamento]

    @field_validator("indices_acompanhamento")
    @classmethod
    def validate_indices_not_empty(
        cls, v: List[IndiceAcompanhamento]
    ) -> List[IndiceAcompanhamento]:
        """Valida que a lista de indicadores de acompanhamento não esteja vazia."""
        if not v:
            raise ValueError("A lista de indicadores de acompanhamento não pode estar vazia.")
        return v
