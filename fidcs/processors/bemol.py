"""
Processor específico para FIDC Bemol.

Implementa lógica de parseamento e inserção de dados
específica para relatórios do FIDC Bemol.
"""

from .base import BaseFIDCProcessor


class BemolProcessor(BaseFIDCProcessor):
    """Processor para FIDC Bemol."""

    async def process_data(
        self, api_response: dict, ativo_codigo: str, filename: str = None
    ) -> int:
        """
        Processa dados específicos do FIDC Bemol.

        Args:
            api_response: Resposta da API PydanticAI
            ativo_codigo: Código do ativo

        Returns:
            int: Total de registros inseridos/atualizados
        """
        resultado = api_response.get("resultado", {})
        metadado = self._create_metadado(api_response)
        total_registros = 0

        # Usa ano e mês do api_response
        ano = api_response.get("ano")
        mes = str(api_response.get("mes")).zfill(2)  # Garante formato MM

        if not ano or not mes:
            # Se não tem ano/mês, não processa
            return 0

        dados_cadastrais = resultado.get("dados_cadastrais", {})

        # 1. Processa dados cadastrais
        if dados_cadastrais:
            registros = await self._process_dados_cadastrais(dados_cadastrais, ativo_codigo)
            total_registros += registros

        # 2. Processa parâmetros de patrimônio líquido
        if "parametros_patrimonio_liquido" in resultado:
            registros = await self._process_patrimonio_liquido(
                resultado["parametros_patrimonio_liquido"], ativo_codigo, mes, int(ano), metadado
            )
            total_registros += registros

        # 3. Processa recompras (série temporal)
        if "recompras" in resultado:
            registros = await self._process_recompras(
                resultado["recompras"], ativo_codigo, metadado
            )
            total_registros += registros

        # 4. Processa parâmetros agente cobrança
        if "parametros_agente_cobranca" in resultado:
            registros = await self._process_agente_cobranca(
                resultado["parametros_agente_cobranca"], ativo_codigo, mes, int(ano), metadado
            )
            total_registros += registros

        # 5. Processa pagamentos por situação
        if "pagamentos_por_situacao" in resultado:
            registros = await self._process_pagamentos_situacao(
                resultado["pagamentos_por_situacao"], ativo_codigo, mes, int(ano), metadado
            )
            total_registros += registros

        # 6. Processa índices de liquidez
        if "indices_de_liquidez" in resultado:
            registros = await self._process_indices_liquidez(
                resultado["indices_de_liquidez"], ativo_codigo, metadado
            )
            total_registros += registros

        # 7. Processa índices do fundo
        if "indices_do_fundo" in resultado:
            registros = await self._process_indices_fundo(
                resultado["indices_do_fundo"], ativo_codigo, metadado
            )
            total_registros += registros

        return total_registros

    async def _process_dados_cadastrais(self, dados: dict, ativo_codigo: str) -> int:
        """Processa dados cadastrais do Bemol."""
        registros = 0

        for campo, valor in dados.items():
            # Cria nome do indicador em snake_case
            indicador_nome = campo.replace(" ", "_").lower()

            # Busca indicador
            indicador_id = await self._get_or_find_indicador(indicador_nome)

            if indicador_id:
                await self.repository.insert_dados_cadastrais(
                    ativo_codigo, indicador_id, str(valor)
                )
                registros += 1

        return registros

    async def _process_patrimonio_liquido(
        self, dados: dict, ativo_codigo: str, mes: str, ano: int, metadado: dict
    ) -> int:
        """Processa parâmetros de patrimônio líquido."""
        registros = 0

        for campo, valor in dados.items():
            indicador_nome = campo.replace(" ", "_").lower()
            valor_float = float(valor) if valor is not None else None

            indicador_id = await self._get_or_find_indicador(indicador_nome)

            if indicador_id:
                await self.repository.insert_indicador_valor(
                    ativo_codigo=ativo_codigo,
                    indicador_id=indicador_id,
                    valor=valor_float,
                    extra_data=metadado,
                    mes=mes,
                    ano=ano,
                )
                registros += 1

        return registros

    async def _process_recompras(
        self, recompras: list[dict], ativo_codigo: str, metadado: dict
    ) -> int:
        """Processa dados de recompras (série temporal)."""
        registros = 0

        indicador_id = await self._get_or_find_indicador("recompras")

        if indicador_id:
            for item in recompras:
                ano = str(item["ano"])
                mes = self._convert_mes_to_number(item["mes"])
                valor = float(item["valor"]) if item["valor"] is not None else None

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

    async def _process_agente_cobranca(
        self, dados: list[dict], ativo_codigo: str, mes: str, ano: int, metadado: dict
    ) -> int:
        """Processa parâmetros de agente de cobrança."""
        indicador_id = await self._get_or_find_indicador("parametros_agente_cobranca")

        if indicador_id:
            # Salva todos os dados como extra_data
            metadado_completo = {**metadado, "parametros_agente_cobranca": dados}

            await self.repository.insert_indicador_valor(
                ativo_codigo=ativo_codigo,
                indicador_id=indicador_id,
                valor=1,  # Valor simbólico
                extra_data=metadado_completo,
                mes=mes,
                ano=ano,
            )
            return 1

        return 0

    async def _process_pagamentos_situacao(
        self, dados: list[dict], ativo_codigo: str, mes: str, ano: int, metadado: dict
    ) -> int:
        """Processa pagamentos por situação."""
        indicador_id = await self._get_or_find_indicador("pagamentos_por_situacao")

        if indicador_id:
            # Salva todos os dados como extra_data
            metadado_completo = {**metadado, "pagamentos_por_situacao": dados}

            await self.repository.insert_indicador_valor(
                ativo_codigo=ativo_codigo,
                indicador_id=indicador_id,
                valor=1,  # Valor simbólico
                extra_data=metadado_completo,
                mes=mes,
                ano=ano,
            )
            return 1

        return 0

    async def _process_indices_liquidez(
        self, dados: list[dict], ativo_codigo: str, metadado: dict
    ) -> int:
        """Processa índices de liquidez."""
        indicador_id = await self._get_or_find_indicador("indices_liquidez")

        if indicador_id and dados:
            # Extrai data de referência do primeiro item
            primeiro_item = dados[0]
            data_ref = primeiro_item.get("data", "")

            if data_ref:
                try:
                    from datetime import datetime

                    data_obj = datetime.strptime(data_ref, "%Y-%m-%d")
                    mes = f"{data_obj.month:02d}"
                    ano = data_obj.year
                except:
                    # Se não conseguir extrair data, não processa
                    return 0
            else:
                # Se não há data de referência, não processa
                return 0

            metadado_completo = {**metadado, "indices_liquidez": dados}

            await self.repository.insert_indicador_valor(
                ativo_codigo=ativo_codigo,
                indicador_id=indicador_id,
                valor=1,  # Valor simbólico
                extra_data=metadado_completo,
                mes=mes,
                ano=ano,
            )
            return 1

        return 0

    async def _process_indices_fundo(self, dados: dict, ativo_codigo: str, metadado: dict) -> int:
        """Processa índices do fundo."""
        registros = 0

        # Extrai data e período
        data_ref = dados.get("data", "")
        if data_ref:
            try:
                from datetime import datetime

                data_obj = datetime.strptime(data_ref, "%Y-%m-%d")
                mes = f"{data_obj.month:02d}"
                ano = data_obj.year
            except:
                # Se não conseguir extrair data, não processa
                return 0
        else:
            # Se não há data de referência, não processa
            return 0

        for campo, valor in dados.items():
            if campo == "data":
                continue

            indicador_nome = campo.replace(" ", "_").lower()
            valor_float = float(valor) if valor is not None else None

            indicador_id = await self._get_or_find_indicador(indicador_nome)

            if indicador_id:
                metadado_item = {**metadado, "data_referencia": data_ref}

                await self.repository.insert_indicador_valor(
                    ativo_codigo=ativo_codigo,
                    indicador_id=indicador_id,
                    valor=valor_float,
                    extra_data=metadado_item,
                    mes=mes,
                    ano=ano,
                )
                registros += 1

        return registros
