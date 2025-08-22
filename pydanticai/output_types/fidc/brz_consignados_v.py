# FIDC BRZ Consignados V - Modelos de Resposta da API
# ---------------------------------------------------
# Este arquivo contém as classes Pydantic que definem a estrutura de dados
# esperada para o relatório do Fundo de Investimento em Direitos Creditórios (FIDC) BRZ Consignados V.
#
# Características do fundo:
# - Foco em crédito consignado (SIAPE, CAPAG, INSS, etc.)
# - Estrutura com cotas Sênior, Mezanino e Subordinada
# - Gestão: BRZ Investimentos Ltda
# - Administração: Banvox DTVM Ltda
#
# Estas classes são usadas como `response_model` no FastAPI para garantir
# a tipagem, validação e documentação automática dos dados da API.

from modules.util.validators import ValidatedModel
from pydantic import Field, field_validator


# --- Seção: Características Gerais ---
class CaracteristicasGerais(ValidatedModel):
    """Principais características e benchmarks das cotas do fundo."""

    benchmark_senior: str = Field(..., description="Benchmark da cota sênior.")
    razao_garantia_senior: float = Field(..., description="Razão de garantia da cota sênior.")
    rating_senior: str = Field(..., description="Classificação de risco da cota sênior.")
    benchmark_mezanino: str = Field(..., description="Benchmark da cota mezanino.")
    razao_garantia_mezanino: float = Field(..., description="Razão de garantia da cota mezanino.")
    rating_mezanino: str = Field(..., description="Classificação de risco da cota mezanino.")
    gestao: str = Field(..., description="Nome da gestora do fundo.")
    administracao: str = Field(..., description="Nome da administradora do fundo.")
    custodia: str = Field(..., description="Nome da instituição custodiante.")
    inicio_fundo: str = Field(..., description="Data de início do fundo.")

    @field_validator("razao_garantia_senior", "razao_garantia_mezanino")
    @classmethod
    def validate_razao_garantia(cls, v: float) -> float:
        """Valida que a razão de garantia não seja negativa."""
        if v < 0:
            raise ValueError("A razão de garantia não pode ser negativa.")
        return v


# --- Seção: Informações da Carteira ---
class InformacoesCarteira(ValidatedModel):
    """Dados consolidados sobre a carteira de direitos creditórios do fundo."""

    direitos_creditorios: float = Field(..., description="Valor total dos direitos creditórios.")
    num_contratos: int = Field(..., description="Número de contratos na carteira.")
    ticket_medio: float = Field(..., description="Ticket médio dos contratos.")
    prazo_vencimento_originacao_meses: int = Field(
        ..., description="Prazo de vencimento médio dos contratos originais (meses)."
    )
    duration_originacao_meses: int = Field(..., description="Duration da originação (meses).")
    prazo_remanescente_meses: int = Field(
        ..., description="Prazo remanescente médio dos contratos (meses)."
    )
    duration_atual_meses: int = Field(..., description="Duration atual da carteira (meses).")
    taxa_media_pct: float = Field(..., description="Taxa média dos contratos em percentual.")
    idade_media: float = Field(..., description="Idade média dos contratos.")

    @field_validator("ticket_medio", "taxa_media_pct", "idade_media")
    @classmethod
    def validate_positive(cls, v: float) -> float:
        """Valida que os valores sejam positivos."""
        if v < 0:
            raise ValueError("O valor não pode ser negativo.")
        return v


# --- Seção: Indicadores de Performance e Risco ---
class Indicadores(ValidatedModel):
    """Comparativo entre os indicadores exigidos pelo regulamento e os valores atuais do fundo."""

    indicador: str = Field(..., alias="Indicador", description="Nome do indicador.")
    exigido: float = Field(..., description="Valor exigido pelo regulamento do fundo.")
    atual: float = Field(..., description="Valor atual do indicador no fundo.")
    situacao: str = Field(
        ..., description="Status do indicador em relação à regra (ex: 'Enquadrado')."
    )

    @field_validator("exigido", "atual")
    @classmethod
    def validate_non_negative(cls, v: float) -> float:
        """Valida que os valores dos indicadores não sejam negativos."""
        if v < 0:
            raise ValueError("O valor do indicador não pode ser negativo.")
        return v


# --- Seção: Análise de Inadimplência ---
class ParcelasInadimplentes(ValidatedModel):
    """Distribuição dos valores inadimplentes por faixa de atraso."""

    periodo: str = Field(..., description="Faixa de dias de atraso.")
    valor: float = Field(
        ..., description="Valor total das parcelas inadimplentes na respectiva faixa."
    )

    @field_validator("valor")
    @classmethod
    def validate_inadimplencia_value(cls, v: float) -> float:
        """Valida que o valor das parcelas inadimplentes seja positivo."""
        if v < 0:
            raise ValueError("O valor das parcelas inadimplentes não pode ser negativo.")
        return v


# --- Modelo Principal: Estrutura Completa do Relatório ---
class RelatorioFIDCBRZConsignadosV(ValidatedModel):
    """
    Modelo raiz que agrega todos os componentes do relatório do FIDC BRZ Consignados V.
    Esta é a classe principal a ser usada como `response_model` na API.
    """

    caracteristicas_gerais: CaracteristicasGerais
    objetivo_fundo: str = Field(
        ..., description="Descrição do objetivo principal do fundo, conforme regulamento."
    )
    politica_investimento: str = Field(
        ..., description="Descrição da política de investimento e alocação de recursos do fundo."
    )
    publico_alvo: str = Field(
        ...,
        description="Perfil de investidor ao qual o fundo se destina (ex: 'Investidores Qualificados').",
    )
    informacoes_carteira: InformacoesCarteira
    indicadores: list[Indicadores]
    parcelas_liquidadas: float = Field(
        ..., description="Valor total das parcelas que foram pagas e liquidadas no período."
    )
    parcelas_inadimplentes: list[ParcelasInadimplentes]

    @field_validator("parcelas_liquidadas")
    @classmethod
    def validate_positive_value(cls, v: float) -> float:
        """Valida que o valor das parcelas liquidadas seja positivo."""
        if v < 0:
            raise ValueError("O valor das parcelas liquidadas não pode ser negativo.")
        return v
