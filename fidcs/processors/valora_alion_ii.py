"""
Processor específico para FIDC Valora ALION II.

Implementa lógica de parseamento e inserção de dados
específica para relatórios do FIDC Valora ALION II.
"""

from .base import BaseFIDCProcessor


class AlionProcessor(BaseFIDCProcessor):
    """Processor para FIDC Valora ALION II."""

    async def process_data(
        self, api_response: dict, ativo_codigo: str, filename: str = None
    ) -> int:
        """Processa dados do FIDC Valora ALION II."""
        resultado = api_response.get("resultado", {})
        metadado = self._create_metadado(api_response)
        total_registros = 0

        # Estrutura 1: dados_cadastrais + fechamento_ultimo_mes (API original)
        if "dados_cadastrais" in resultado and "fechamento_ultimo_mes" in resultado:
            # Dados cadastrais
            registros = await self._process_dados_cadastrais_genericos(
                resultado["dados_cadastrais"], ativo_codigo, "ALION_CADASTRAL"
            )
            total_registros += registros

            # Fechamento último mês
            # Usa ano e mês do api_response
            ano = api_response.get("ano")
            mes = str(api_response.get("mes")).zfill(2)  # Garante formato MM

            if ano and mes:
                registros = await self._process_lista_fechamento(
                    resultado["fechamento_ultimo_mes"],
                    ativo_codigo,
                    "ALION_FECHAMENTO",
                    mes,
                    int(ano),
                    metadado,
                )
                total_registros += registros

        # Estrutura 2: indicadores_com_limites + séries temporais (nova API)
        else:
            # 1. Indicadores com limites
            if "indicadores_com_limites" in resultado:
                periodo_ref = self._get_periodo_referencia(resultado)
                if periodo_ref:
                    mes_ref, ano_ref = periodo_ref
                    registros = await self._process_indicadores_com_limites(
                        resultado["indicadores_com_limites"],
                        ativo_codigo,
                        mes_ref,
                        int(ano_ref),
                        metadado,
                    )
                    total_registros += registros

            # 2. Séries temporais simples
            series_simples = [
                "quantidade_de_devedores",
                "prazo_medio_da_carteira_meses",
                "credito_vencido_nao_pago_acumulado",
                "pdd_x_dc",
            ]

            for nome_indicador in series_simples:
                if nome_indicador in resultado:
                    registros = await self._process_series_temporais_simples(
                        resultado[nome_indicador], nome_indicador, ativo_codigo, metadado
                    )
                    total_registros += registros

            # 3. Séries temporais complexas
            series_complexas = [
                "credito_vencido_nao_pago_x_vencimento_historico_acumulado",
                "pdd_x_patrimonio_liquido",
            ]

            for nome_base in series_complexas:
                if nome_base in resultado:
                    registros = await self._process_series_temporais_complexas(
                        resultado[nome_base], nome_base, ativo_codigo, metadado
                    )
                    total_registros += registros

        return total_registros

    def _get_periodo_referencia(self, resultado: dict) -> tuple[str, str] | None:
        """
        Obtém período de referência (mais recente) das séries temporais.

        Returns:
            tuple | None: (mes, ano) ou None se não encontrar
        """
        # Procura por séries temporais para pegar o período mais recente
        series_campos = [
            "quantidade_de_devedores",
            "prazo_medio_da_carteira_meses",
            "credito_vencido_nao_pago_acumulado",
            "pdd_x_dc",
            "credito_vencido_nao_pago_x_vencimento_historico_acumulado",
            "pdd_x_patrimonio_liquido",
        ]

        for campo in series_campos:
            if campo in resultado and resultado[campo]:
                # Pega o último item da série (mais recente)
                ultimo_item = resultado[campo][-1]
                ano = str(ultimo_item["ano"])
                mes = self._convert_mes_to_number(ultimo_item["mes"])
                return mes, ano

        return None

    async def _process_dados_cadastrais_genericos(
        self, dados: dict, ativo_codigo: str, categoria: str
    ) -> int:
        """Processa dados cadastrais genéricos."""
        registros = 0

        for campo, valor in dados.items():
            indicador_nome = campo.replace(" ", "_").lower()

            indicador_id = await self._get_or_find_indicador(indicador_nome)

            if indicador_id:
                await self.repository.insert_dados_cadastrais(
                    ativo_codigo, indicador_id, str(valor)
                )
                registros += 1

        return registros

    async def _process_lista_fechamento(
        self,
        lista: list[dict],
        ativo_codigo: str,
        categoria: str,
        mes: str,
        ano: int,
        metadado: dict,
    ) -> int:
        """Processa lista de indicadores com valor."""
        registros = 0

        for item in lista:
            indicador_nome = item.get("Indicador", "").replace(" ", "_").lower()
            valor = float(item.get("Valor", 0)) if item.get("Valor") is not None else None

            if valor is not None:
                indicador_id = await self._get_or_find_indicador(indicador_nome)

                if indicador_id:
                    await self.repository.insert_indicador_valor(
                        ativo_codigo=ativo_codigo,
                        indicador_id=indicador_id,
                        valor=valor,
                        extra_data=metadado,
                        mes=mes,
                        ano=ano,
                    )
                    registros += 1

        return registros

    async def _process_indicadores_com_limites(
        self, indicadores_data: list[dict], ativo_codigo: str, mes: str, ano: int, metadado: dict
    ) -> int:
        """Processa indicadores com limites."""
        registros = 0

        for item in indicadores_data:
            indicador_nome = item.get("indicador", "").replace(" ", "_").lower()
            valor = float(item.get("valor", 0)) if item.get("valor") is not None else None
            limite = item.get("limite", "")

            if valor is not None:
                indicador_id = await self._get_or_find_indicador(indicador_nome)

                if indicador_id:
                    await self.repository.insert_indicador_valor(
                        ativo_codigo=ativo_codigo,
                        indicador_id=indicador_id,
                        valor=valor,
                        limite=limite,
                        extra_data=metadado,
                        mes=mes,
                        ano=ano,
                    )
                    registros += 1

        return registros

    async def _process_series_temporais_simples(
        self, series_data: list[dict], nome_indicador: str, ativo_codigo: str, metadado: dict
    ) -> int:
        """Processa séries temporais simples (ano/mes/valor)."""
        registros = 0

        indicador_id = await self._get_or_find_indicador(nome_indicador)
        if not indicador_id:
            return 0

        for item in series_data:
            ano = str(item["ano"])
            mes = self._convert_mes_to_number(item["mes"])
            valor = float(item["valor"]) if item["valor"] is not None else None

            if valor is not None:
                await self.repository.insert_indicador_valor(
                    ativo_codigo=ativo_codigo,
                    indicador_id=indicador_id,
                    valor=valor,
                    extra_data=metadado,
                    mes=mes,
                    ano=int(ano),
                )
                registros += 1

        return registros

    async def _process_series_temporais_complexas(
        self, series_data: list[dict], nome_base_indicador: str, ativo_codigo: str, metadado: dict
    ) -> int:
        """Processa séries temporais complexas (múltiplos campos por período)."""
        registros = 0

        for item in series_data:
            ano = str(item["ano"])
            mes = self._convert_mes_to_number(item["mes"])

            # Para cada campo que não seja ano/mes, cria um indicador separado
            for campo, valor in item.items():
                if campo in ["ano", "mes"]:
                    continue

                valor_float = float(valor) if valor is not None else None

                if valor_float is not None:
                    indicador_id = await self._get_or_find_indicador(campo)

                    if indicador_id:
                        await self.repository.insert_indicador_valor(
                            ativo_codigo=ativo_codigo,
                            indicador_id=indicador_id,
                            valor=valor_float,
                            extra_data=metadado,
                            mes=mes,
                            ano=int(ano),
                        )
                        registros += 1

        return registros
