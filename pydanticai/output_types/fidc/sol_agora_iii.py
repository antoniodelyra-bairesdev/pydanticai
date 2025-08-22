# FIDC Sol Agora III - Modelos de Resposta da API
# ------------------------------------------------
# Este arquivo contém as classes Pydantic que definem a estrutura de dados
# esperada para o relatório do Fundo de Investimento em Direitos Creditórios (FIDC) Sol Agora III.
#
# Características do fundo:
# - Foco em crédito com CCBs (Cédulas de Crédito Bancário)
# - Estrutura com cotas Sênior, Mezanino A e Subordinada Jr
# - Relatório diário com indicadores detalhados
# - Sistema de classificação de risco por faixas (AA a G)
#
# Estas classes são usadas como response_model no FastAPI para garantir
# a tipagem, validação e documentação automática dos dados da API.

from modules.util.validators import ValidatedModel
from pydantic import Field, field_validator


# --- Seção: Indicadores da Última Data ---
class IndicadoresUltimaData(ValidatedModel):
    """Principais indicadores financeiros e patrimoniais do fundo na data de fechamento."""

    patrimonio_fundo: float = Field(..., description="Patrimônio total do fundo em reais")
    ativos: float = Field(..., description="Total de ativos do fundo em reais")
    direitos_creditorios: float = Field(
        ..., description="Valor dos direitos creditórios (CCBs) em reais"
    )
    tesouraria: float = Field(..., description="Valor mantido em tesouraria em reais")
    fundo_zeragem: float = Field(
        ..., description="Valor no fundo de zeragem para liquidez em reais"
    )
    titulos_publicos: float = Field(..., description="Investimentos em títulos públicos em reais")
    provisoes: float = Field(..., description="Total de provisões constituídas em reais")
    contas_pagareceber: float = Field(
        ..., description="Saldo líquido de contas a pagar e receber em reais"
    )
    pdd_carteira: float = Field(
        ..., description="Provisão para Devedores Duvidosos da carteira em reais"
    )
    valores_identificar: float = Field(
        ..., description="Valores pendentes de identificação em reais"
    )
    swap_pagareceber: float = Field(
        ..., description="Posição líquida em operações de swap em reais"
    )
    passivos: float = Field(..., description="Total de passivos do fundo em reais")
    patrimonio_solagora_senior: float = Field(
        ..., description="Patrimônio da cota sênior em reais"
    )
    valor_cota_solagora_senior: float = Field(
        ..., description="Valor unitário da cota sênior em reais"
    )
    amortizacao_diaria_solagora_senior: float = Field(
        ..., description="Amortização diária da cota sênior em reais"
    )
    rentabilidade_dia_solagora_senior: float = Field(
        ..., description="Rentabilidade diária da cota sênior em percentual"
    )
    rentabilidade_mes_solagora_senior: float = Field(
        ..., description="Rentabilidade mensal da cota sênior em percentual"
    )
    rentabilidade_ano_solagora_senior: float = Field(
        ..., description="Rentabilidade anual da cota sênior em percentual"
    )
    patrimonio_solagora_mezanino: float = Field(
        ..., description="Patrimônio da cota mezanino em reais"
    )
    valor_cota_solagora_mezanino: float = Field(
        ..., description="Valor unitário da cota mezanino em reais"
    )
    amortizacao_diaria_solagora_mezanino: float = Field(
        ..., description="Amortização diária da cota mezanino em reais"
    )
    rentabilidade_dia_solagora_mezanino: float = Field(
        ..., description="Rentabilidade diária da cota mezanino em percentual"
    )
    rentabilidade_mes_solagora_mezanino: float = Field(
        ..., description="Rentabilidade mensal da cota mezanino em percentual"
    )
    rentabilidade_ano_solagora_mezanino: float = Field(
        ..., description="Rentabilidade anual da cota mezanino em percentual"
    )
    patrimonio_solagora_subordinada_jr: float = Field(
        ..., description="Patrimônio da cota subordinada júnior em reais"
    )
    valor_cota_solagora_subordinada_jr: float = Field(
        ..., description="Valor unitário da cota subordinada júnior em reais"
    )
    aporte_diario_solagora_subordinada_jr: float = Field(
        ..., description="Aporte diário na cota subordinada júnior em reais"
    )
    amortizacao_diaria_solagora_subordinada_jr: float = Field(
        ..., description="Amortização diária da cota subordinada júnior em reais"
    )
    rentabilidade_dia_solagora_subordinada_jr: float = Field(
        ..., description="Rentabilidade diária da cota subordinada júnior em percentual"
    )
    rentabilidade_mes_solagora_subordinada_jr: float = Field(
        ..., description="Rentabilidade mensal da cota subordinada júnior em percentual"
    )
    rentabilidade_ano_solagora_subordinada_jr: float = Field(
        ..., description="Rentabilidade anual da cota subordinada júnior em percentual"
    )

    @field_validator("patrimonio_fundo", "ativos", "direitos_creditorios")
    @classmethod
    def validate_positive_values(cls, v: float) -> float:
        """Valida que valores principais sejam positivos."""
        if v < 0:
            raise ValueError("Valores de patrimônio e ativos não podem ser negativos.")
        return v


# --- Seção: Indicadores de Monitoramento ---
class IndicadoresMonitoramento(ValidatedModel):
    """Indicadores de compliance e monitoramento regulatório do fundo."""

    nome: str = Field(..., description="Nome do indicador de monitoramento")
    limite: str = Field(..., description="Limite ou critério estabelecido para o indicador")
    valor: float = Field(..., description="Valor atual do indicador")

    @field_validator("nome")
    @classmethod
    def validate_nome_not_empty(cls, v: str) -> str:
        """Valida que o nome do indicador não seja vazio."""
        if not v.strip():
            raise ValueError("Nome do indicador não pode ser vazio.")
        return v.strip()


# --- Seção: Indicadores de Concentração PF ---
class IndicadoresConcentracaoPF(ValidatedModel):
    """Indicadores de concentração para pessoas físicas."""

    nome: str = Field(..., description="Nome do indicador de concentração PF")
    limite: str = Field(..., description="Limite estabelecido para concentração em PF")
    valor: float = Field(..., description="Valor atual da concentração em PF")

    @field_validator("valor")
    @classmethod
    def validate_concentracao_positive(cls, v: float) -> float:
        """Valida que valores de concentração sejam positivos."""
        if v < 0:
            raise ValueError("Valores de concentração não podem ser negativos.")
        return v


# --- Seção: Indicadores de Concentração PJ ---
class IndicadoresConcentracaoPJ(ValidatedModel):
    """Indicadores de concentração para pessoas jurídicas."""

    nome: str = Field(..., description="Nome do indicador de concentração PJ")
    limite: str = Field(..., description="Limite estabelecido para concentração em PJ")
    valor: float = Field(..., description="Valor atual da concentração em PJ")

    @field_validator("valor")
    @classmethod
    def validate_concentracao_positive(cls, v: float) -> float:
        """Valida que valores de concentração sejam positivos."""
        if v < 0:
            raise ValueError("Valores de concentração não podem ser negativos.")
        return v


# --- Seção: Indicadores Principais ---
class IndicadoresPrincipais(ValidatedModel):
    """Principais indicadores de performance e risco da carteira."""

    pdd_pl_percent: float = Field(..., description="PDD sobre patrimônio líquido em percentual")
    pdd_direitos_creditorios_percent: float = Field(
        ..., description="PDD sobre direitos creditórios em percentual"
    )
    direitos_creditorios: float = Field(..., description="Valor dos direitos creditórios em reais")
    direitos_creditorios_net_pdd: float = Field(
        ..., description="Direitos creditórios líquidos de PDD em reais"
    )
    direitos_creditorios_net_pdd_pl_percent: float = Field(
        ..., description="DC líquidos de PDD sobre PL em percentual"
    )
    outros_ativos_pl_percent: float = Field(
        ..., description="Outros ativos sobre patrimônio líquido em percentual"
    )
    reserva_de_caixa: float = Field(..., description="Reserva de caixa em reais")
    vp_vencimento_cotas_seniores: float = Field(
        ..., description="Valor presente do vencimento das cotas seniores em reais"
    )
    pmr_dacarteira_dias: int = Field(
        ..., description="Prazo médio de recebimento da carteira em dias"
    )
    pmr_dacarteira_anos: float = Field(
        ..., description="Prazo médio de recebimento da carteira em anos"
    )
    duration_dacarteira_anos: float = Field(..., description="Duration da carteira em anos")
    tir_dacarteira_percent: float = Field(
        ..., description="Taxa interna de retorno da carteira em percentual"
    )
    spread_medio_di_percent: float = Field(
        ..., description="Spread médio sobre DI das aquisições em percentual"
    )
    direitos_creditorios_prefixados_percent: float = Field(
        ..., description="Percentual de direitos creditórios pré-fixados"
    )
    direitos_creditorios_posfixados_percent: float = Field(
        ..., description="Percentual de direitos creditórios pós-fixados"
    )
    indice_de_pre_pagamentos_percent: float = Field(
        ..., description="Índice de pré-pagamentos em percentual"
    )

    @field_validator("pmr_dacarteira_dias")
    @classmethod
    def validate_pmr_positive(cls, v: int) -> int:
        """Valida que o PMR seja positivo."""
        if v < 0:
            raise ValueError("Prazo médio de recebimento não pode ser negativo.")
        return v

    @field_validator("direitos_creditorios", "reserva_de_caixa")
    @classmethod
    def validate_monetary_positive(cls, v: float) -> float:
        """Valida que valores monetários sejam positivos."""
        if v < 0:
            raise ValueError("Valores monetários não podem ser negativos.")
        return v


# --- Seção: Indicadores CVNP ---
class IndicadoresCVNP(ValidatedModel):
    """Indicadores de Cessão em Valor Não Proporcional (CVNP)."""

    cvnp_mil: float = Field(..., description="Valor total de CVNP em milhares de reais")
    cvnp_direitos_creditorios_percent: float = Field(
        ..., description="CVNP sobre direitos creditórios em percentual"
    )
    grupo_cvnp_ate_30_dias_pl_percent: float = Field(
        ..., description="CVNP até 30 dias sobre PL em percentual"
    )
    grupo_cvnp_31_60_dias_pl_percent: float = Field(
        ..., description="CVNP de 31 a 60 dias sobre PL em percentual"
    )
    grupo_cvnp_61_90_dias_pl_percent: float = Field(
        ..., description="CVNP de 61 a 90 dias sobre PL em percentual"
    )
    grupo_cvnp_91_120_dias_pl_percent: float = Field(
        ..., description="CVNP de 91 a 120 dias sobre PL em percentual"
    )
    grupo_cvnp_121_150_dias_pl_percent: float = Field(
        ..., description="CVNP de 121 a 150 dias sobre PL em percentual"
    )
    grupo_cvnp_151_180_dias_pl_percent: float = Field(
        ..., description="CVNP de 151 a 180 dias sobre PL em percentual"
    )
    grupo_cvnp_acima_180_dias_pl_percent: float = Field(
        ..., description="CVNP acima de 180 dias sobre PL em percentual"
    )

    @field_validator("cvnp_mil")
    @classmethod
    def validate_cvnp_positive(cls, v: float) -> float:
        """Valida que valor de CVNP seja positivo."""
        if v < 0:
            raise ValueError("Valor de CVNP não pode ser negativo.")
        return v


# --- Seção: Faixas de PDD ---
class FaixaPDD(ValidatedModel):
    """Distribuição dos direitos creditórios por faixa de risco de PDD."""

    faixa_aa: float = Field(..., description="Valor presente da faixa AA (menor risco) em reais")
    faixa_a: float = Field(..., description="Valor presente da faixa A em reais")
    faixa_b: float = Field(..., description="Valor presente da faixa B em reais")
    faixa_c: float = Field(..., description="Valor presente da faixa C em reais")
    faixa_d: float = Field(..., description="Valor presente da faixa D em reais")
    faixa_e: float = Field(..., description="Valor presente da faixa E em reais")
    faixa_f: float = Field(..., description="Valor presente da faixa F em reais")
    faixa_g: float = Field(..., description="Valor presente da faixa G (maior risco) em reais")
    write_off: float = Field(..., description="Valor de write-off (baixas por perda) em reais")

    @field_validator(
        "faixa_aa",
        "faixa_a",
        "faixa_b",
        "faixa_c",
        "faixa_d",
        "faixa_e",
        "faixa_f",
        "faixa_g",
        "write_off",
    )
    @classmethod
    def validate_faixa_positive(cls, v: float) -> float:
        """Valida que valores de faixas sejam positivos."""
        if v < 0:
            raise ValueError("Valores das faixas de PDD não podem ser negativos.")
        return v


# --- Modelo Principal: Estrutura Completa do Relatório ---
class RelatorioFIDCSolAgoraIII(ValidatedModel):
    """
    Modelo raiz que agrega todos os componentes do relatório do FIDC Sol Agora III.
    Esta é a classe principal a ser usada como response_model na API.
    """

    indicadores_ultima_data: IndicadoresUltimaData = Field(
        ..., description="Indicadores financeiros e patrimoniais da última data de fechamento"
    )
    indicadores_monitoramento: list[IndicadoresMonitoramento] = Field(
        ..., description="Lista de indicadores de compliance e monitoramento regulatório"
    )
    indicadores_concentracao_pf: list[IndicadoresConcentracaoPF] = Field(
        ..., description="Indicadores de concentração para pessoas físicas"
    )
    indicadores_concentracao_pj: list[IndicadoresConcentracaoPJ] = Field(
        ..., description="Indicadores de concentração para pessoas jurídicas"
    )
    indicadores_principais: IndicadoresPrincipais = Field(
        ..., description="Principais indicadores de performance e risco da carteira"
    )
    indicadores_cvnp: IndicadoresCVNP = Field(
        ..., description="Indicadores de Cessão em Valor Não Proporcional"
    )
    faixa_pdd: FaixaPDD = Field(
        ..., description="Distribuição dos direitos creditórios por faixa de risco"
    )

    @field_validator("indicadores_monitoramento")
    @classmethod
    def validate_monitoramento_not_empty(
        cls, v: list[IndicadoresMonitoramento]
    ) -> list[IndicadoresMonitoramento]:
        """Valida que existe pelo menos um indicador de monitoramento."""
        if not v:
            raise ValueError("Deve existir pelo menos um indicador de monitoramento.")
        return v
