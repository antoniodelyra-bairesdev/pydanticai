# FIDC Bemol - Modelos de Resposta da API (Versão Aprimorada)
# -------------------------------------------------------------
# Este arquivo contém as classes Pydantic que definem a estrutura de dados
# esperada para o relatório do Fundo de Investimento em Direitos Creditórios (FIDC) Bemol.
#
# Melhorias realizadas:
# - Adição de descrições detalhadas para cada campo.
# - Correção e especificação de tipos de dados (date, float).
# - Inclusão de validadores modernos (@field_validator) para garantir a integridade dos dados.
#
# Estas classes são usadas como `response_model` no FastAPI para garantir
# a tipagem, validação e documentação automática dos dados da API.

import re
from datetime import date

from pydantic import Field, field_validator

from modules.util.validators import ValidatedModel


# --- Seção: Dados Cadastrais ---
class DadosCadastrais(ValidatedModel):
    """Informações básicas e de identificação do fundo."""

    administrador: str = Field(..., description="Nome do administrador do fundo.")
    cnpj: str = Field(..., description="CNPJ do fundo no formato XX.XXX.XXX/XXXX-XX.")
    custodiante: str = Field(..., description="Nome do custodiante do fundo.")
    data_base_do_relatorio: date = Field(
        ..., description="Data de referência para os dados do relatório."
    )
    data_envio_relatorio_gestao: date = Field(
        ..., description="Data em que o relatório de gestão foi enviado."
    )
    data_pagamento: date = Field(
        ..., description="Próxima data de pagamento/amortização das cotas."
    )
    data_verificacao: date = Field(
        ..., description="Data da última verificação dos dados."
    )
    gestor: str = Field(..., description="Nome do gestor do fundo.")
    nome_do_fundo: str = Field(..., description="Nome completo do FIDC.")
    tipo_anbima: str = Field(
        ..., description="Classificação do fundo segundo a ANBIMA."
    )

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, v: str) -> str:
        """Valida o formato do CNPJ."""
        if not re.match(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", v):
            raise ValueError("Formato de CNPJ inválido. Use XX.XXX.XXX/XXXX-XX.")
        return v


# --- Seção: Patrimônio Líquido ---
class ParametrosPatrimonioLiquido(ValidatedModel):
    """Parâmetros financeiros relacionados ao patrimônio líquido do fundo."""

    alocacao_liquida: float = Field(
        ..., description="Percentual do patrimônio líquido alocado em ativos."
    )
    caixa: float = Field(
        ..., description="Valor total em caixa e equivalentes de caixa."
    )
    patrimonio_liquido: float = Field(
        ..., description="Valor total do patrimônio líquido do fundo."
    )
    pdd_total: float = Field(
        ..., description="Provisão para Devedores Duvidosos (PDD) total."
    )
    relacao_minima: float = Field(
        ..., description="Relação mínima exigida entre ativos e passivos."
    )
    reserva_de_despesas: float = Field(
        ..., description="Valor reservado para cobrir despesas operacionais."
    )
    reserva_de_liquidez: float = Field(
        ..., description="Valor reservado para garantir a liquidez do fundo."
    )
    total_ativos_financeiros: float = Field(
        ..., description="Soma de todos os ativos financeiros do fundo."
    )
    valor_das_disponibilidades: float = Field(
        ..., description="Valor total das disponibilidades financeiras."
    )
    valor_nominal_dcs_bruto: float = Field(
        ..., description="Valor de face total dos Direitos Creditórios."
    )
    valor_presente_dcs: float = Field(
        ..., description="Valor presente dos Direitos Creditórios."
    )
    valor_presente_dcs_liquido_pdd: float = Field(
        ..., description="Valor presente dos Direitos Creditórios, líquido da PDD."
    )

    @field_validator("alocacao_liquida", "caixa", "patrimonio_liquido", "pdd_total")
    @classmethod
    def validate_positive(cls, v: float) -> float:
        """Valida que os valores sejam positivos."""
        if v < 0:
            raise ValueError("O valor não pode ser negativo.")
        return v


# --- Seção: Histórico de Recompras ---
class Recompra(ValidatedModel):
    """Detalhes sobre as operações de recompra realizadas."""

    ano: int = Field(..., description="Ano da operação de recompra.")
    mes: str = Field(..., description="Mês da operação de recompra")
    valor: float = Field(..., description="Valor da recompra realizada")

    @field_validator("valor")
    @classmethod
    def validate_recompra_value(cls, v: float) -> float:
        """Valida que o valor da recompra é positivo."""
        if v <= 0:
            raise ValueError("O valor da recompra deve ser positivo.")
        return v


# --- Seção: Performance do Agente de Cobrança ---
class ParametrosAgenteCobranca(ValidatedModel):
    """Métricas de desempenho do agente de cobrança responsável."""

    percentual_recuperado: float = Field(
        ..., description="Percentual do valor de face inadimplente que foi recuperado."
    )
    acoes_de_cobranca: str = Field(
        ..., description="Descrição das principais ações de cobrança realizadas."
    )
    faixa_de_atraso: str = Field(
        ..., description="Faixa de dias de atraso dos créditos."
    )
    juros_de_mora_multa_recebido: float = Field(
        ..., description="Valor total recebido a título de juros e multas."
    )
    valor_face_inadimplente: float = Field(
        ..., description="Valor de face total dos créditos inadimplentes na faixa."
    )
    valor_face_recebido: float = Field(
        ..., description="Valor de face total recebido dos créditos na faixa."
    )

    @field_validator("percentual_recuperado")
    @classmethod
    def validate_percentual_recuperado(cls, v: float) -> float:
        """Valida que o percentual de recuperação não seja maior que 100%."""
        if v > 100:
            raise ValueError("O percentual recuperado não pode ser maior que 100%.")
        return v


# --- Seção: Análise de Pagamentos ---
class PagamentoSituacao(ValidatedModel):
    """Distribuição dos pagamentos por situação (ex: em dia, em atraso)."""

    percentual: float = Field(
        ..., description="Percentual que esta situação representa do total."
    )
    situacao: str = Field(..., description="Descrição da situação do pagamento.")
    valor: float = Field(..., description="Valor financeiro total para esta situação.")


# --- Seção: Indicadores de Liquidez ---
class IndiceLiquidez(ValidatedModel):
    """Métricas que avaliam a liquidez das cotas do fundo."""

    data: date = Field(
        ..., description="Data de referência para os índices de liquidez."
    )
    indice_liquidez_mezanino: float = Field(
        ..., description="Índice de liquidez da cota mezanino."
    )
    indice_liquidez_senior: float = Field(
        ..., description="Índice de liquidez da cota sênior."
    )
    indice_mes_horizonte_liquidez: float = Field(
        ..., description="Horizonte de liquidez em meses."
    )

    @field_validator("indice_liquidez_mezanino", "indice_liquidez_senior")
    @classmethod
    def validate_positive_liquidity(cls, v: float) -> float:
        """Valida que os índices de liquidez sejam positivos."""
        if v < 0:
            raise ValueError("Os índices de liquidez não podem ser negativos.")
        return v


# --- Seção: Indicadores Gerais do Fundo ---
class IndicesFundo(ValidatedModel):
    """Compilação dos principais indicadores de performance e risco do fundo."""

    alocacao_bruta: float = Field(
        ..., description="Percentual de alocação bruta dos ativos."
    )
    alocacao_liquida: float = Field(
        ..., description="Percentual de alocação líquida dos ativos."
    )
    data: date = Field(..., description="Data de referência para os índices.")
    excesso_retorno_ativos_fundo: float = Field(
        ..., description="Retorno dos ativos acima do benchmark."
    )
    excesso_retorno_minimo: float = Field(
        ..., description="Excesso de retorno sobre a taxa mínima de atratividade."
    )
    relacao_minima: float = Field(
        ..., description="Relação mínima entre ativos elegíveis e cotas sênior."
    )
    retorno_medio_cotas: float = Field(
        ..., description="Retorno médio histórico das cotas do fundo."
    )
    taxa_interna_retorno_carteira: float = Field(
        ..., description="TIR (Taxa Interna de Retorno) da carteira de crédito."
    )
    indice_cobertura: float = Field(
        ..., description="Índice de cobertura geral (Ativos / Passivos)."
    )
    indice_cobertura_mezanino: float = Field(
        ..., description="Índice de cobertura da cota mezanino."
    )
    indice_cobertura_senior: float = Field(
        ..., description="Índice de cobertura da cota sênior."
    )
    indice_liquidez: float = Field(
        ..., description="Índice geral de liquidez do fundo."
    )
    indice_perdas: float = Field(
        ..., description="Índice de perdas observadas na carteira."
    )

    @field_validator("alocacao_bruta", "alocacao_liquida")
    @classmethod
    def validate_positive(cls, v: float) -> float:
        """Valida que os índices de alocação sejam positivos."""
        if v < 0:
            raise ValueError("Os índices de alocação não podem ser negativos.")
        return v


# --- Modelo Principal: Estrutura Completa do Relatório ---
class RelatorioFIDCBemol(ValidatedModel):
    """
    Modelo raiz que agrega todos os componentes do relatório do FIDC Bemol.
    Esta é a classe principal a ser usada como `response_model` na API.
    """

    dados_cadastrais: DadosCadastrais
    parametros_patrimonio_liquido: ParametrosPatrimonioLiquido
    recompras: list[Recompra]
    parametros_agente_cobranca: list[ParametrosAgenteCobranca]
    pagamentos_por_situacao: list[PagamentoSituacao]
    indices_de_liquidez: list[IndiceLiquidez]
    indices_do_fundo: IndicesFundo
