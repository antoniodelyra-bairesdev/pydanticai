# FIDC ICRED FGTS - Modelos de Resposta da API
# -----------------------------------------------
# Este arquivo contém as classes Pydantic que definem a estrutura de dados
# esperada para o relatório do Fundo de Investimento em Direitos Creditórios (FIDC) ICRED FGTS.
#
# Características do fundo:
# - Foco em crédito garantido por FGTS (Saque-Aniversário)
# - Estrutura com múltiplas cotas Sênior e Mezanino
# - Gestão: Oliveira Trust DTVM
# - Originador: iCred Soluções Financeiras S.A.
#
# Estas classes são usadas como response_model no FastAPI para garantir
# a tipagem, validação e documentação automática dos dados da API.

from typing import Optional
from pydantic import Field, field_validator

from modules.util.validators import ValidatedModel


# --- Seção: Fluxo de Caixa dos Direitos Creditórios ---
class FluxoDeCaixaItem(ValidatedModel):
    """Movimentação mensal de aquisições e liquidações de direitos creditórios."""

    ano: int = Field(..., description="Ano de referência do fluxo")
    mes: str = Field(..., description="Mês de referência do fluxo")
    aquisicoes: float = Field(..., description="Valor das aquisições de DCs no período em milhões")
    liquidacoes: Optional[float] = Field(
        None, description="Valor das liquidações de DCs no período em milhões"
    )

    @field_validator("aquisicoes")
    @classmethod
    def validate_aquisicoes_positive(cls, v: float) -> float:
        """Valida que o valor das aquisições seja positivo."""
        if v < 0:
            raise ValueError("O valor das aquisições não pode ser negativo.")
        return v

    @field_validator("liquidacoes")
    @classmethod
    def validate_liquidacoes_positive(cls, v: Optional[float]) -> Optional[float]:
        """Valida que o valor das liquidações seja positivo quando informado."""
        if v is not None and v < 0:
            raise ValueError("O valor das liquidações não pode ser negativo.")
        return v


# --- Seção: Direitos Creditórios e PDD ---
class DireitosCreditoriosItem(ValidatedModel):
    """Evolução mensal dos direitos creditórios e provisão para devedores duvidosos."""

    ano: int = Field(..., description="Ano de referência")
    mes: str = Field(..., description="Mês de referência")
    dc_vencidos: Optional[float] = Field(None, description="Valor dos DCs vencidos em milhões")
    dc_a_vencer: float = Field(..., description="Valor dos DCs a vencer em milhões")
    pdd_dc: Optional[float] = Field(
        None, description="Provisão para Devedores Duvidosos sobre DCs em milhões"
    )

    @field_validator("dc_a_vencer")
    @classmethod
    def validate_dc_a_vencer_positive(cls, v: float) -> float:
        """Valida que o valor dos DCs a vencer seja positivo."""
        if v < 0:
            raise ValueError("O valor dos DCs a vencer não pode ser negativo.")
        return v

    @field_validator("dc_vencidos", "pdd_dc")
    @classmethod
    def validate_optional_positive(cls, v: Optional[float]) -> Optional[float]:
        """Valida que valores opcionais sejam positivos quando informados."""
        if v is not None and v < 0:
            raise ValueError("Os valores de DCs e PDD não podem ser negativos.")
        return v


# --- Seção: Prazo Médio dos Recebíveis ---
class PrazoMedioRecebiveisItem(ValidatedModel):
    """Evolução mensal do prazo médio dos recebíveis da carteira."""

    ano: int = Field(..., description="Ano de referência")
    mes: str = Field(..., description="Mês de referência")
    prazo_medio_dias: int = Field(..., description="Prazo médio dos recebíveis em dias")

    @field_validator("prazo_medio_dias")
    @classmethod
    def validate_prazo_medio(cls, v: int) -> int:
        """Valida que o prazo médio não seja negativo."""
        if v < 0:
            raise ValueError("O prazo médio em dias não pode ser negativo.")
        return v


# --- Seção: Taxa Média dos Recebíveis ---
class TaxaMediaRecebiveisItem(ValidatedModel):
    """Evolução mensal da taxa média dos recebíveis da carteira."""

    ano: int = Field(..., description="Ano de referência")
    mes: str = Field(..., description="Mês de referência")
    taxa_media_a_a: float = Field(..., description="Taxa média anual dos recebíveis em percentual")

    @field_validator("taxa_media_a_a")
    @classmethod
    def validate_taxa_media(cls, v: float) -> float:
        """Valida que a taxa média esteja em faixa aceitável."""
        if not 0 <= v <= 100:
            raise ValueError("Taxa média deve estar entre 0% e 100% ao ano.")
        return v


# --- Seção: Contratos Quantidade ---
class ContratosQuantidadeItem(ValidatedModel):
    """Evolução mensal da quantidade de contratos na carteira."""

    ano: int = Field(..., description="Ano de referência")
    mes: str = Field(..., description="Mês de referência")
    quantidade: int = Field(..., description="Quantidade total de contratos na carteira")

    @field_validator("quantidade")
    @classmethod
    def validate_quantidade_positive(cls, v: int) -> int:
        """Valida que a quantidade de contratos seja positiva."""
        if v < 0:
            raise ValueError("A quantidade de contratos não pode ser negativa.")
        return v


# --- Modelo Principal: Estrutura Completa do Relatório ---
class RelatorioFIDCICred(ValidatedModel):
    """
    Modelo raiz que agrega todos os componentes do relatório do FIDC ICRED FGTS.
    Esta é a classe principal a ser usada como response_model na API.
    """

    fluxo_de_caixa_dos_direitos_creditorios: list[FluxoDeCaixaItem] = Field(
        ..., description="Histórico mensal de aquisições e liquidações de direitos creditórios"
    )

    direitos_creditorios_e_pdd: list[DireitosCreditoriosItem] = Field(
        ..., description="Evolução mensal dos DCs vencidos, a vencer e respectiva PDD"
    )

    prazo_medio_dos_recebiveis_dias: list[PrazoMedioRecebiveisItem] = Field(
        ..., description="Histórico do prazo médio dos recebíveis em dias"
    )

    taxa_media_dos_recebiveis_percent_a_a: list[TaxaMediaRecebiveisItem] = Field(
        ..., description="Evolução da taxa média anual dos recebíveis"
    )

    contratos_valor_medio_e_quantidade: list[ContratosQuantidadeItem] = Field(
        ..., description="Histórico da quantidade de contratos na carteira"
    )
