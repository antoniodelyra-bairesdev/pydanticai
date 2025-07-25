# FIDC Valora ALION II Consignados - Modelos de Resposta da API
# -------------------------------------------------------------
# Este arquivo contém as classes Pydantic que definem a estrutura de dados
# esperada para o relatório do Fundo de Investimento em Direitos Creditórios
# (FIDC) Valora ALION II.
#
# Características do fundo:
# - Foco na aquisição de Direitos de Crédito representados por CCB.
# - Estrutura com cotas Sênior, Mezanino A, Mezanino B e Subordinada.
# - Gestão: Valora Gestão de Investimentos
# - Administração: Banvox DTVM Ltda
#
# Estas classes são usadas como `response_model` no FastAPI para garantir
# a tipagem, validação e documentação automática dos dados da API.

import re
from pydantic import Field, field_validator

from modules.util.validators import ValidatedModel


# --- Seção: Fechamento do Último Mês ---
class FechamentoUltimoMes(ValidatedModel):
    """Representa um indicador financeiro consolidado no fechamento do último mês de referência."""

    Indicador: str = Field(..., description="Nome do indicador financeiro.")
    Valor: float = Field(..., description="Valor do indicador em milhares de Reais.")

    @field_validator("Indicador")
    @classmethod
    def validate_indicador_not_empty(cls, v: str) -> str:
        """Valida que o nome do indicador não é vazio."""
        if not v.strip():
            raise ValueError("O nome do indicador não pode ser vazio.")
        return v.strip()


# --- Seção: Dados Cadastrais ---
class DadosCadastrais(ValidatedModel):
    """Informações gerais de identificação e administração do fundo."""

    Nome_do_Fundo: str = Field(..., description="Nome completo do Fundo de Investimento.")
    Data_do_Relatorio: str = Field(..., description="Mês e ano de referência do relatório.")
    Data_de_Inicio_do_Fundo: str = Field(
        ..., description="Data de início das operações do fundo no formato 'dd/mm/aaaa'."
    )
    Administrador: str = Field(..., description="Nome da instituição administradora do fundo.")
    Gestor: str = Field(..., description="Nome da instituição gestora do fundo.")
    Custodiante: str = Field(..., description="Nome da instituição custodiante dos ativos.")
    Objetivo_resumido_do_Fundo: str = Field(
        ..., description="Breve descrição do objetivo de investimento do fundo."
    )

    @field_validator("Data_de_Inicio_do_Fundo")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Valida o formato da data para dd/mm/aaaa."""
        if not re.match(r"^\d{2}/\d{2}/\d{4}$", v):
            raise ValueError("Formato de data inválido. Use 'dd/mm/aaaa'.")
        return v


# --- Modelo Principal: Estrutura Completa do Relatório ---
class RelatorioFIDCValoraAlion(ValidatedModel):
    """
    Modelo raiz que agrega todos os componentes do relatório do FIDC Valora ALION II.
    Esta é a classe principal a ser usada como `response_model` na API.
    """

    dados_cadastrais: DadosCadastrais
    fechamento_ultimo_mes: list[FechamentoUltimoMes]

    @field_validator("fechamento_ultimo_mes")
    @classmethod
    def validate_fechamento_not_empty(
        cls, v: list[FechamentoUltimoMes]
    ) -> list[FechamentoUltimoMes]:
        """Valida que a lista de indicadores do fechamento do mês não esteja vazia."""
        if not v:
            raise ValueError("A lista de indicadores de fechamento não pode estar vazia.")
        return v


# --- Modelo para o Graficos ---
class IndicadorComLimite(ValidatedModel):
    """Representa um indicador de acompanhamento do fundo com seu respectivo limite e valor apurado."""
    indicador: str = Field(..., description="Nome do indicador monitorado, como 'Razão de Garantia' ou 'Atraso F30'.")
    limite: str = Field(..., description="O limite de referência para o indicador (ex: '<18%').")
    valor: float = Field(..., description="Valor percentual apurado para o indicador no período.")


class QuantidadeDeDevedores(ValidatedModel):
    """Representa a evolução mensal da quantidade de devedores na carteira do fundo."""
    ano: int = Field(..., description="Ano de referência da medição.")
    mes: str = Field(..., description="Mês de referência da medição.")
    valor: int = Field(..., description="Quantidade total de devedores no período.")

    @field_validator("valor")
    @classmethod
    def validate_valor_not_negative(cls, v: int) -> int:
        """Valida que o valor não seja negativo."""
        if v < 0:
            raise ValueError("A quantidade de devedores não pode ser negativa.")
        return v

class PrazoMedioDaCarteiraMeses(ValidatedModel):
    """Representa a evolução do prazo médio da carteira, em meses."""
    ano: int = Field(..., description="Ano de referência da medição.")
    mes: str = Field(..., description="Mês de referência da medição.")
    valor: float = Field(..., description="Prazo médio da carteira em meses.")

    @field_validator("valor")
    @classmethod
    def validate_valor_not_negative(cls, v: float) -> float:
        """Valida que o valor não seja negativo."""
        if v < 0:
            raise ValueError("O prazo médio da carteira não pode ser negativo.")
        return v


class CreditoVencidoNaoPagoAcumulado(ValidatedModel):
    """Representa o valor acumulado de crédito vencido e não pago, em R$ mil."""
    ano: int = Field(..., description="Ano de referência da medição.")
    mes: str = Field(..., description="Mês de referência da medição.")
    valor: float = Field(..., description="Valor acumulado de crédito vencido e não pago (em R$ mil).")

    @field_validator("valor")
    @classmethod
    def validate_valor_not_negative(cls, v: float) -> float:
        """Valida que o valor não seja negativo."""
        if v < 0:
            raise ValueError("O valor de crédito vencido não pago não pode ser negativo.")
        return v

class CreditoVencidoNaoPagoXVencimentoHistoricoAcumulado(ValidatedModel):
    """Representa a relação entre o volume vencido e o percentual de crédito não pago."""
    ano: int = Field(..., description="Ano de referência da medição.")
    mes: str = Field(..., description="Mês de referência da medição.")
    volume_vencido: float = Field(..., description="Volume total vencido no histórico (em R$ mil).")
    credito_vencido_nao_pago: float = Field(..., description="Percentual de crédito vencido e não pago em relação ao volume vencido.")


class PDDxDC(ValidatedModel):
    """Representa a relação percentual entre a Provisão para Devedores Duvidosos (PDD) e os Direitos Creditórios (DC)."""
    ano: int = Field(..., description="Ano de referência da medição.")
    mes: str = Field(..., description="Mês de referência da medição.")
    valor: float = Field(..., description="Percentual da PDD em relação ao total de Direitos Creditórios.")


class PDDxPatrimonioLiquido(ValidatedModel):
    """Representa a evolução do Patrimônio Líquido e a relação percentual da PDD sobre ele."""
    ano: int = Field(..., description="Ano de referência da medição.")
    mes: str = Field(..., description="Mês de referência da medição.")
    patrimonio_liquido: float = Field(..., description="Valor do Patrimônio Líquido (PL) do fundo (em R$ mil).")
    pdd_pl: float = Field(..., description="Percentual da PDD em relação ao Patrimônio Líquido.")


class RelatorioFIDCValoraAlionIIImage(ValidatedModel):
    """Modelo raiz que agrega os componentes do relatório do FIDC Valora Alion II."""
    indicadores_com_limites: list[IndicadorComLimite]
    quantidade_de_devedores: list[QuantidadeDeDevedores]
    prazo_medio_da_carteira_meses: list[PrazoMedioDaCarteiraMeses]
    credito_vencido_nao_pago_acumulado: list[CreditoVencidoNaoPagoAcumulado]
    credito_vencido_nao_pago_x_vencimento_historico_acumulado: list[CreditoVencidoNaoPagoXVencimentoHistoricoAcumulado]
    pdd_x_dc: list[PDDxDC]
    pdd_x_patrimonio_liquido: list[PDDxPatrimonioLiquido]
