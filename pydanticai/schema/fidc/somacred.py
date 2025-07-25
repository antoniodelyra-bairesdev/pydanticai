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
    indices_acompanhamento: list[IndiceAcompanhamento]

    @field_validator("indices_acompanhamento")
    @classmethod
    def validate_indices_not_empty(
        cls, v: list[IndiceAcompanhamento]
    ) -> list[IndiceAcompanhamento]:
        """Valida que a lista de indicadores de acompanhamento não esteja vazia."""
        if not v:
            raise ValueError("A lista de indicadores de acompanhamento não pode estar vazia.")
        return v


# --- Modelo para o Graficos ---


class FluxoCaixaMensal(ValidatedModel):
    """
    Representa a movimentação mensal de aquisições e liquidações de direitos creditórios.
    """

    ano: int = Field(..., description="Ano de referência do fluxo de caixa.")
    mes: str = Field(..., description="Mês de referência do fluxo de caixa.")
    aquisicoes: float = Field(
        ..., description="Valor das aquisições de direitos creditórios no período (em R$ milhões)."
    )
    liquidacoes: float = Field(
        ...,
        description="Valor das liquidações de direitos creditórios no período (em R$ milhões).",
    )

    @field_validator("ano")
    @classmethod
    def validate_year(cls, v: int) -> int:
        """Valida se o ano é um valor positivo."""
        if v < 2000:
            raise ValueError("O ano deve ser um valor válido.")
        return v


class ContratosMensal(ValidatedModel):
    """
    Representa a quantidade de contratos em um determinado período.
    """

    quantidade: int = Field(..., description="Quantidade total de contratos na carteira.")
    mes: str = Field(..., description="Mês de referência para a contagem de contratos.")
    ano: int = Field(..., description="Ano de referência para a contagem de contratos.")

    @field_validator("quantidade")
    @classmethod
    def validate_quantidade_not_negative(cls, v: int) -> int:
        """Valida que a quantidade de contratos não seja negativa."""
        if v < 0:
            raise ValueError("A quantidade de contratos não pode ser negativa.")
        return v


class PrazoMedioRecebiveis(ValidatedModel):
    """
    Representa a evolução mensal do prazo médio de recebimento da carteira.
    """

    prazo_medio_dias: float = Field(
        ..., description="Prazo médio de recebimento da carteira, em dias."
    )
    mes: str = Field(..., description="Mês de referência para o prazo médio.")
    ano: int = Field(..., description="Ano de referência para o prazo médio.")

    @field_validator("prazo_medio_dias")
    @classmethod
    def validate_prazo_not_negative(cls, v: float) -> float:
        """Valida que o prazo médio não seja negativo."""
        if v < 0:
            raise ValueError("O prazo médio de recebíveis não pode ser negativo.")
        return v


class TaxaMediaRecebiveis(ValidatedModel):
    """
    Representa a evolução mensal da taxa média dos recebíveis.
    """

    taxa_media_a_a: float = Field(
        ..., description="Taxa média anual dos recebíveis, em percentual."
    )
    mes: str = Field(..., description="Mês de referência para a taxa média.")
    ano: int = Field(..., description="Ano de referência para a taxa média.")

    @field_validator("taxa_media_a_a")
    @classmethod
    def validate_taxa_not_negative(cls, v: float) -> float:
        """Valida que a taxa média não seja negativa."""
        if v < 0:
            raise ValueError("A taxa média de recebíveis não pode ser negativa.")
        return v


class RelatorioCompletoSomacredImage(ValidatedModel):
    """
    Modelo raiz que agrega todos os componentes de dados históricos extraídos de gráficos e imagens do relatório do FIDC Somacred.
    Esta é a classe principal a ser usada como `response_model` na API.
    """

    fluxo_caixa_mensal: list[FluxoCaixaMensal] = Field(
        ..., description="Histórico mensal do fluxo de caixa dos direitos creditórios."
    )
    contratos_mensal: list[ContratosMensal] = Field(
        ..., description="Histórico mensal da quantidade de contratos."
    )
    prazo_medio_recebiveis: list[PrazoMedioRecebiveis] = Field(
        ..., description="Evolução mensal do prazo médio dos recebíveis."
    )
    taxa_media_recebiveis: list[TaxaMediaRecebiveis] = Field(
        ..., description="Evolução mensal da taxa média dos recebíveis."
    )
