# FIDC VerdeCard - Modelos de Resposta da API
# ----------------------------------------------
# Este arquivo contém as classes Pydantic que definem a estrutura de dados
# esperada para o relatório do Fundo de Investimento em Direitos Creditórios (FIDC) VerdeCard.
#
# Características do fundo:
# - Início: 29/03/2018 (fundo com histórico longo)
# - Foco em cartão de crédito verde
# - 11 séries diferentes de cotas seniores
# - Gestão: Integral Investimentos Ltda
# - Administração: Oliveira Trust DTVM
#
# Estas classes são usadas como response_model no FastAPI para garantir
# a tipagem, validação e documentação automática dos dados da API.

import re
from pydantic import Field, field_validator, HttpUrl
from modules.util.validators import ValidatedModel


# --- Seção: Indicadores Financeiros ---
class IndicadorFinanceiro(ValidatedModel):
    """Indicadores financeiros principais do fundo."""

    indicador: str = Field(..., description="Nome do indicador financeiro.")
    valor: float = Field(..., description="Valor do indicador em Reais.")

    @field_validator("indicador")
    @classmethod
    def validate_indicador_not_empty(cls, v: str) -> str:
        """Valida que o nome do indicador não seja vazio."""
        if not v.strip():
            raise ValueError("Nome do indicador não pode ser vazio")
        return v.strip()


# --- Seção: Gestão ---
class Gestao(ValidatedModel):
    """Informações da empresa gestora do fundo."""

    nome: str = Field(..., description="Nome da empresa gestora")
    endereco: str = Field(..., description="Endereço da empresa gestora")
    telefone: str = Field(..., description="Telefone da empresa gestora")
    site: HttpUrl = Field(..., description="Website da empresa gestora")


# --- Seção: Administração e Custódia ---
class AdministracaoCustodia(ValidatedModel):
    """Informações da empresa administradora e custodiante."""

    nome: str = Field(..., description="Nome da empresa administradora")
    endereco: str = Field(..., description="Endereço da empresa")
    telefone: str = Field(..., description="Telefone da empresa")
    site: HttpUrl = Field(..., description="Website da empresa")


# --- Seção: Características Gerais ---
class CaracteristicasGerais(ValidatedModel):
    """Características principais e cadastrais do fundo."""

    inicio_do_fundo: str = Field(..., description="Data de início do fundo")
    cnpj: str = Field(..., description="CNPJ do fundo no formato XX.XXX.XXX/XXXX-XX")
    objetivo_do_fundo: str = Field(
        ..., description="Objetivo principal do fundo conforme regulamento"
    )
    publico_alvo: str = Field(..., description="Perfil do público-alvo do fundo")
    auditoria: str = Field(
        ...,
        description="Nome da empresa de auditoria",
    )
    agencia_de_rating: str = Field(..., description="Nome da agência de rating")
    rating_das_series_de_cotas: str = Field(..., description="Rating atribuído às séries de cotas")

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj_format(cls, v: str) -> str:
        """Valida formato do CNPJ."""
        if not re.match(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", v):
            raise ValueError("CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX")
        return v


# --- Seção: Índices de Controle ---
class IndiceControle(ValidatedModel):
    """Índices de controle e compliance do fundo."""

    nome: str = Field(..., description="Nome do índice de controle")
    limite: str = Field(..., description="Limite estabelecido para o índice")
    periodicidade: str = Field(..., description="Periodicidade de verificação")
    valor: float = Field(..., description="Valor atual do índice")

    @field_validator("valor")
    def validate_valor_nao_negativo(cls, v: float) -> float:
        """Valida que o valor do índice não seja negativo."""
        if v < 0:
            raise ValueError("O valor do índice não pode ser negativo.")
        return v


# --- Modelo Principal: Estrutura Completa do Relatório ---
class RelatorioFIDCVerdeCard(ValidatedModel):
    """
    Modelo raiz que agrega todos os componentes do relatório do FIDC VerdeCard.
    Esta é a classe principal a ser usada como response_model na API.
    """

    indicadores_financeiros: list[IndicadorFinanceiro] = Field(
        ..., description="Lista de indicadores financeiros principais"
    )
    gestao: Gestao = Field(..., description="Informações da empresa gestora")
    administracao_custodia: AdministracaoCustodia = Field(
        ..., description="Informações da empresa administradora e custodiante"
    )
    caracteristicas_gerais: CaracteristicasGerais = Field(
        ..., description="Características principais e cadastrais do fundo"
    )
    indices_de_controle: list[IndiceControle] = Field(
        ..., description="Lista de índices de controle e compliance"
    )

    @field_validator("indicadores_financeiros", "indices_de_controle")
    @classmethod
    def validate_listas_not_empty(cls, v: list) -> list:
        """Valida que as listas não sejam vazias."""
        if not v:
            raise ValueError("Lista não pode ser vazia")
        return v
