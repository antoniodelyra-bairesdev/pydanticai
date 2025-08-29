"""
Processor específico para FIDC Valora Noto.

Implementa lógica de parseamento e inserção de dados
específica para relatórios do FIDC Valora Noto.
"""

from .base import BaseFIDCProcessor


class NotoProcessor(BaseFIDCProcessor):
    """Processor para FIDC Valora Noto."""

    async def process_data(self, api_response: dict, ativo_codigo: str, filename: str = None) -> int:
        """Processa dados do FIDC Valora Noto."""
        resultado = api_response.get("resultado", {})
        metadado = self._create_metadado(api_response)
        total_registros = 0

        # Usa ano e mês do api_response
        ano = api_response.get("ano")
        mes = str(api_response.get("mes")).zfill(2)  # Garante formato MM

        if not ano or not mes:
            # Se não tem ano/mês, não processa
            return 0

        # 1. Dados cadastrais (formato antigo)
        if "dados_cadastrais" in resultado:
            registros = await self._process_dados_cadastrais_noto(
                resultado["dados_cadastrais"], ativo_codigo
            )
            total_registros += registros

        # 2. Indicadores com limites (formato antigo)
        if "indicadores_com_limites" in resultado:
            registros = await self._process_indicadores_com_limites_noto(
                resultado["indicadores_com_limites"], ativo_codigo, metadado, mes, int(ano)
            )
            total_registros += registros

        # 3. Fechamento último mês (formato antigo)
        if "fechamento_ultimo_mes" in resultado:
            registros = await self._process_fechamento_ultimo_mes_noto(
                resultado["fechamento_ultimo_mes"], ativo_codigo, metadado, mes, int(ano)
            )
            total_registros += registros

        # 4. Dados históricos mensais (formato novo)
        dados_historicos = {}
        campos_historicos = [
            "quantidade_de_devedores",
            "prazo_medio_da_carteira_meses",
            "volume_operado_mensal",
            "credito_vencido_nao_pago_acumulado",
            "credito_vencido_nao_pago_x_vencimento_historico_acumulado",
            "pdd_x_patrimonio_liquido"
        ]

        for campo in campos_historicos:
            if campo in resultado:
                dados_historicos[campo] = resultado[campo]

        if dados_historicos:
            registros = await self._process_dados_historicos_mensais_noto(
                dados_historicos, ativo_codigo, metadado
            )
            total_registros += registros

        return total_registros

    async def _process_dados_cadastrais_noto(
        self, dados_cadastrais: dict, ativo_codigo: str
    ) -> int:
        """Processa dados cadastrais do Noto."""
        registros = 0

        for campo, valor in dados_cadastrais.items():
            # Pula campos vazios
            if not valor or (isinstance(valor, str) and valor.strip() == ""):
                continue

            indicador_nome = campo.replace(" ", "_").lower()
            valor_str = str(valor)

            indicador_id = await self._get_or_find_indicador(indicador_nome)

            if indicador_id:
                await self.repository.insert_dados_cadastrais(
                    ativo_codigo, indicador_id, valor_str
                )
                registros += 1

        return registros

    async def _process_indicadores_com_limites_noto(
        self, indicadores_data: list[dict], ativo_codigo: str, metadado: dict, mes: str, ano: int
    ) -> int:
        """Processa indicadores com limites do Noto."""
        registros = 0

        for item in indicadores_data:
            indicador_nome = item.get("indicador", "").replace("Atraso", "Atrasos")
            limite = item.get("limite", "")
            valor_str = item.get("valor", "")

            # Extrai valor numérico da string formatada
            valor_numerico = self._extract_numeric_value(valor_str)

            if valor_numerico is not None:
                indicador_id = await self._get_or_find_indicador(indicador_nome)

                if indicador_id:
                    # Adiciona valor original ao metadado para preservar formatação
                    metadado_item = {
                        **metadado,
                        "valor_original_formatado": valor_str
                    }

                    await self.repository.insert_indicador_valor(
                        ativo_codigo=ativo_codigo,
                        indicador_id=indicador_id,
                        valor=valor_numerico,
                        limite=limite,
                        extra_data=metadado_item,
                        mes=mes,
                        ano=ano
                    )
                    registros += 1

        return registros

    async def _process_fechamento_ultimo_mes_noto(
        self, fechamento_data: list[dict], ativo_codigo: str, metadado: dict, mes: str, ano: int
    ) -> int:
        """Processa dados de fechamento do último mês do Noto."""
        registros = 0

        for item in fechamento_data:
            indicador_nome = item.get("indicador", "")
            valor = float(item.get("valor", 0)) if item.get("valor") is not None else None

            if valor is not None:
                indicador_id = await self._get_or_find_indicador(indicador_nome)

                if indicador_id:
                    await self.repository.insert_indicador_valor(
                        ativo_codigo=ativo_codigo,
                        indicador_id=indicador_id,
                        valor=valor,
                        extra_data=metadado,
                        mes=mes,
                        ano=ano
                    )
                    registros += 1

        return registros

    async def _process_dados_historicos_mensais_noto(
        self, dados_historicos: dict, ativo_codigo: str, metadado: dict
    ) -> int:
        """Processa dados históricos mensais do Noto."""
        registros = 0

        for indicador_nome, dados_mensais in dados_historicos.items():
            if not isinstance(dados_mensais, list):
                continue

            indicador_id = await self._get_or_find_indicador(indicador_nome)

            if not indicador_id:
                continue

            for registro in dados_mensais:
                ano = str(registro.get("ano"))
                mes_nome = registro.get("mes", "")
                mes_numero = self._convert_mes_to_number(mes_nome)

                # Para dados simples com apenas 'valor'
                if "valor" in registro and len(registro) == 3:  # ano, mes, valor
                    valor = registro.get("valor")

                    if valor is not None:
                        await self.repository.insert_indicador_valor(
                            ativo_codigo=ativo_codigo,
                            indicador_id=indicador_id,
                            valor=valor,
                            extra_data=metadado,
                            mes=mes_numero,
                            ano=int(ano)
                        )
                        registros += 1

                # Para dados complexos com múltiplos campos
                else:
                    for campo, valor in registro.items():
                        if campo in ["ano", "mes"]:
                            continue

                        # Cria nome do indicador combinando o indicador principal com o campo
                        indicador_composto = f"{indicador_nome}_{campo}"
                        indicador_composto_id = await self._get_or_find_indicador(
                            indicador_composto
                        )

                        if indicador_composto_id and valor is not None:
                            await self.repository.insert_indicador_valor(
                                ativo_codigo=ativo_codigo,
                                indicador_id=indicador_composto_id,
                                valor=valor,
                                extra_data=metadado,
                                mes=mes_numero,
                                ano=int(ano)
                            )
                            registros += 1

        return registros
