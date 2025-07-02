# FIDC Valora Noto Consignados - Modelos de Resposta da API
# ----------------------------------------------------------
# Este arquivo contém as classes Pydantic que definem a estrutura de dados
# esperada para o relatório do Fundo de Investimento em Direitos Creditórios (FIDC) Valora Noto.
#
# Características do fundo:
# - Início: 16/06/2024 (fundo recente)
# - Foco em crédito consignado público federal
# - Estrutura com cotas Sênior, Mezanino A, Mezanino B e Subordinada
# - Gestão: Valora Gestão de Investimentos Renda Fixa Ltda
# - Administração: Banvox DTVM
#
# Estas classes são usadas como response_model no FastAPI para garantir
# a tipagem, validação e documentação automática dos dados da API.

from pydantic import Field, field_validator
from modules.util.validators import ValidatedModel


# --- Seção: Quantidade de Devedores ---
class QuantidadeDeDevedores(ValidatedModel):
    """Evolução mensal da quantidade de devedores na carteira."""

    ano: int = Field(..., description="Ano de referência")
    mes: str = Field(..., description="Mês de referência")
    valor: float = Field(..., description="Número de devedores no período")

    @field_validator("valor")
    @classmethod
    def validate_quantidade_positive(cls, v: float) -> float:
        """Valida que a quantidade de devedores seja positiva."""
        if v < 0:
            raise ValueError("Quantidade de devedores não pode ser negativa")
        return v


# --- Seção: Prazo Médio da Carteira ---
class PrazoMedioDaCarteiraMeses(ValidatedModel):
    """Evolução mensal do prazo médio de vencimento da carteira."""

    ano: int = Field(..., description="Ano de referência")
    mes: str = Field(..., description="Mês de referência")
    valor: float = Field(..., description="Prazo médio da carteira em meses")

    @field_validator("valor")
    @classmethod
    def validate_prazo_range(cls, v: float) -> float:
        """Valida que o prazo médio esteja em faixa razoável."""
        if not 1 <= v <= 240:  # Entre 1 mês e 20 anos
            raise ValueError("Prazo médio deve estar entre 1 e 240 meses")
        return v


# --- Seção: Volume Operado Mensal ---
class VolumeOperadoMensal(ValidatedModel):
    """Volume financeiro operado mensalmente pelo fundo."""

    ano: int = Field(..., description="Ano de referência")
    mes: str = Field(..., description="Mês de referência")
    valor: float = Field(..., description="Volume operado no mês em reais (milhares)")

    @field_validator("valor")
    @classmethod
    def validate_volume_positive(cls, v: float) -> float:
        """Valida que o volume operado seja positivo."""
        if v < 0:
            raise ValueError("Volume operado não pode ser negativo")
        return v


# --- Seção: Crédito Vencido e Não Pago Acumulado ---
class CreditoVencidoNaoPagoAcumulado(ValidatedModel):
    """Evolução do crédito vencido e não pago acumulado."""

    ano: int = Field(..., description="Ano de referência")
    mes: str = Field(..., description="Mês de referência")
    valor: float = Field(
        ..., description="Valor acumulado de crédito vencido e não pago em reais (milhares)"
    )

    @field_validator("valor")
    @classmethod
    def validate_credito_vencido_positive(cls, v: float) -> float:
        """Valida que o crédito vencido seja positivo ou zero."""
        if v < 0:
            raise ValueError("Crédito vencido não pode ser negativo")
        return v


# --- Seção: Crédito Vencido vs Vencimento Histórico ---
class CreditoVencidoNaoPagoXVencimentoHistoricoAcumulado(ValidatedModel):
    """Comparativo entre volume vencido e crédito vencido não pago."""

    ano: int = Field(..., description="Ano de referência")
    mes: str = Field(..., description="Mês de referência")
    volume_vencido: float = Field(
        ..., description="Volume total vencido no período em reais (milhares)"
    )
    credito_vencido_nao_pago: float = Field(
        ..., description="Percentual de crédito vencido não pago"
    )

    @field_validator("volume_vencido")
    @classmethod
    def validate_volume_vencido_positive(cls, v: float) -> float:
        """Valida que o volume vencido seja positivo ou zero."""
        if v < 0:
            raise ValueError("Volume vencido não pode ser negativo")
        return v

    @field_validator("credito_vencido_nao_pago")
    @classmethod
    def validate_percentual_range(cls, v: float) -> float:
        """Valida que o percentual esteja entre 0% e 100%."""
        if not 0 <= v <= 100:
            raise ValueError("Percentual de crédito vencido deve estar entre 0% e 100%")
        return v


# --- Seção: PDD vs Patrimônio Líquido ---
class PDDxPatrimonioLiquido(ValidatedModel):
    """Evolução da relação entre PDD e patrimônio líquido."""

    ano: int = Field(..., description="Ano de referência")
    mes: str = Field(..., description="Mês de referência")
    patrimonio_liquido: float = Field(
        ..., description="Patrimônio líquido do fundo em reais (milhares)"
    )
    pdd_pl: float = Field(..., description="Percentual de PDD sobre patrimônio líquido")

    @field_validator("patrimonio_liquido")
    @classmethod
    def validate_patrimonio_positive(cls, v: float) -> float:
        """Valida que o patrimônio líquido seja positivo."""
        if v <= 0:
            raise ValueError("Patrimônio líquido deve ser positivo")
        return v

    @field_validator("pdd_pl")
    @classmethod
    def validate_pdd_range(cls, v: float) -> float:
        """Valida que o percentual de PDD esteja em faixa razoável."""
        if not 0 <= v <= 50:  # Máximo 50% seria extremo
            raise ValueError("Percentual de PDD deve estar entre 0% e 50%")
        return v


# --- Modelo Principal: Estrutura Completa do Relatório ---
class RelatorioFIDCNoto(ValidatedModel):
    """
    Modelo raiz que agrega todos os componentes do relatório do FIDC Valora Noto.
    Esta é a classe principal a ser usada como response_model na API.
    """

    quantidade_de_devedores: list[QuantidadeDeDevedores] = Field(
        ..., description="Evolução mensal da quantidade de devedores"
    )
    prazo_medio_da_carteira_meses: list[PrazoMedioDaCarteiraMeses] = Field(
        ..., description="Evolução do prazo médio da carteira em meses"
    )
    volume_operado_mensal: list[VolumeOperadoMensal] = Field(
        ..., description="Volume financeiro operado mensalmente"
    )
    credito_vencido_nao_pago_acumulado: list[CreditoVencidoNaoPagoAcumulado] = Field(
        ..., description="Evolução do crédito vencido e não pago acumulado"
    )
    credito_vencido_nao_pago_x_vencimento_historico_acumulado: list[
        CreditoVencidoNaoPagoXVencimentoHistoricoAcumulado
    ] = Field(..., description="Comparativo entre volume vencido e crédito não pago")
    pdd_x_patrimonio_liquido: list[PDDxPatrimonioLiquido] = Field(
        ..., description="Evolução da relação PDD vs patrimônio líquido"
    )

    @field_validator(
        "quantidade_de_devedores", "prazo_medio_da_carteira_meses", "volume_operado_mensal"
    )
    @classmethod
    def validate_listas_not_empty(cls, v: list) -> list:
        """Valida que as listas principais não sejam vazias."""
        if not v:
            raise ValueError("Lista não pode ser vazia")
        return v
