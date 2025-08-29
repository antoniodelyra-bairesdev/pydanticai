"""
Classe base para processadores de FIDC.

Define interface comum e métodos utilitários para todos os processadores específicos.
"""

import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.fidcs.repository import FidcsRepository


class BaseFIDCProcessor(ABC):
    """
    Classe base abstrata para processadores de FIDC.

    Fornece métodos utilitários comuns e define interface
    que deve ser implementada por cada processador específico.
    """

    def __init__(self, repository: "FidcsRepository"):
        """
        Inicializa o processador com repository.

        Args:
            repository: Repository para operações de banco
        """
        self.repository = repository

    @abstractmethod
    async def process_data(
        self, api_response: dict, ativo_codigo: str, filename: str = None
    ) -> int:
        """
        Processa dados da API e insere no banco.

        Método abstrato que deve ser implementado por cada processador específico.

        Args:
            api_response: Resposta completa da API PydanticAI
            ativo_codigo: Código do ativo no banco
            filename: Nome do arquivo PDF (opcional, usado para extrair período)

        Returns:
            int: Número total de registros inseridos/atualizados

        Raises:
            NotImplementedError: Se não implementado pela subclasse
        """
        raise NotImplementedError("Subclasses devem implementar process_data")

    def _convert_mes_to_number(self, mes: str) -> str:
        """
        Converte nome ou abreviação do mês para número.

        Args:
            mes: Nome do mês (ex: "janeiro", "jan", "mai")

        Returns:
            str: Número do mês formatado (ex: "01", "05")
        """
        meses = {
            # Abreviações
            "jan": "01",
            "fev": "02",
            "mar": "03",
            "abr": "04",
            "mai": "05",
            "jun": "06",
            "jul": "07",
            "ago": "08",
            "set": "09",
            "out": "10",
            "nov": "11",
            "dez": "12",
            # Nomes completos
            "janeiro": "01",
            "fevereiro": "02",
            "março": "03",
            "abril": "04",
            "maio": "05",
            "junho": "06",
            "julho": "07",
            "agosto": "08",
            "setembro": "09",
            "outubro": "10",
            "novembro": "11",
            "dezembro": "12",
        }
        return meses.get(mes.lower(), mes)

    def _is_date_string(self, value: str) -> bool:
        """
        Verifica se uma string representa uma data.

        Args:
            value: Valor a ser verificado

        Returns:
            bool: True se for uma string de data válida
        """
        if not isinstance(value, str):
            return False

        date_patterns = [
            r"\d{2}/\d{2}/\d{4}",  # DD/MM/YYYY
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{1,2}/\d{1,2}/\d{4}",  # D/M/YYYY
            r"\w+/\d{2}",  # Maio/25
        ]

        for pattern in date_patterns:
            if re.match(pattern, value.strip()):
                return True

        return False

    def _extract_periodo_from_filename(self, filename: str) -> tuple[str, str] | None:
        """
        Extrai período de referência do nome do arquivo.

        Formato esperado: FIDC_XXX_ANO_MES.pdf
        Exemplo: FIDC_SOMACRED_2024_05.pdf

        Args:
            filename: Nome do arquivo PDF

        Returns:
            tuple | None: (mes, ano) como strings ou None se não encontrado
        """
        try:
            # Remove extensão .pdf
            name_without_ext = filename.removesuffix(".pdf")

            # Divide por underscore
            parts = name_without_ext.split("_")

            # Verifica se tem pelo menos 4 partes: FIDC, NOME, ANO, MES
            if len(parts) >= 4:
                ano = parts[-2]  # Penúltimo item
                mes = parts[-1]  # Último item

                # Valida se ano é numérico
                if ano.isdigit() and len(ano) == 4:
                    # Converte mês para número se necessário
                    mes_numero = self._convert_mes_to_number(mes)
                    return mes_numero, ano

            return None

        except Exception:
            return None

    def _extract_numeric_value(self, value_str: str) -> float | None:
        """
        Extrai valor numérico de string formatada.

        Args:
            value_str: String com valor formatado (ex: "R$ 1.234,56", "45,67%")

        Returns:
            float | None: Valor numérico extraído ou None se inválido
        """
        if not isinstance(value_str, str):
            return float(value_str) if value_str is not None else None

        # Remove símbolos e formatação brasileira
        cleaned = (
            value_str.replace("R$", "")
            .replace("%", "")
            .replace(".", "")  # Remove separador de milhares
            .replace(",", ".")  # Troca vírgula decimal por ponto
            .strip()
        )

        # Remove caracteres não numéricos exceto ponto e sinal negativo
        cleaned = re.sub(r"[^\d\.-]", "", cleaned)

        try:
            return float(cleaned) if cleaned else None
        except ValueError:
            return None

    def _create_metadado(self, api_response: dict, **kwargs) -> dict:
        """
        Cria dicionário de metadados padrão.

        Args:
            api_response: Resposta da API
            **kwargs: Metadados adicionais específicos

        Returns:
            dict: Metadados consolidados
        """
        metadado = {
            "tempo_execucao": api_response.get("tempo_execucao"),
            "tokens_utilizados": api_response.get("tokens_utilizados"),
            "modelo_utilizado": api_response.get("modelo_utilizado"),
            "schema_utilizado": api_response.get("schema_utilizado"),
            "data_processamento": datetime.now().isoformat(),
        }

        # Adiciona metadados específicos
        metadado.update(kwargs)

        return metadado

    async def _get_or_find_indicador(self, nome: str) -> int | None:
        """
        Busca indicador existente ou retorna None.

        Args:
            nome: Nome do indicador

        Returns:
            int | None: ID do indicador encontrado ou None
        """
        indicador = await self.repository.get_or_find_indicador(nome)

        if indicador:
            print(f"✅ Indicador encontrado: '{nome}' (ID: {indicador.indicador_fidc_id})")
            return indicador.indicador_fidc_id
        else:
            print(f"❌ Indicador não encontrado: '{nome}'")
            return None

    def _determine_tipo_dado(self, valor) -> str:
        """
        Determina tipo de dado baseado no valor.

        Args:
            valor: Valor a ser analisado

        Returns:
            str: Tipo de dado ('int', 'float', 'date', 'str')
        """
        if isinstance(valor, int):
            return "int"
        elif isinstance(valor, float):
            return "float"
        elif isinstance(valor, str) and self._is_date_string(valor):
            return "date"
        else:
            return "str"
