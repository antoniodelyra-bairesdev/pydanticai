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
