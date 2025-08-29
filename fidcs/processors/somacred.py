"""
Processor específico para FIDC Somacred.

Implementa lógica de parseamento e inserção de dados
específica para relatórios do FIDC Somacred.
"""

from .base import BaseFIDCProcessor


class SomacredProcessor(BaseFIDCProcessor):
    """Processor para FIDC Somacred."""

    async def process_data(
        self, api_response: dict, ativo_codigo: str, filename: str = None
    ) -> int:
        """
        Processa dados específicos do FIDC Somacred.

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

        # Determina se é formato texto ou imagem
        schema_usado = api_response.get("schema_utilizado", "")
        is_image_format = "image" in schema_usado.lower()

        if is_image_format:
            total_registros = await self._process_image_format(resultado, ativo_codigo, metadado)
        else:
            total_registros = await self._process_text_format(resultado, ativo_codigo, metadado, ano, mes)

        return total_registros

    async def _process_text_format(
        self, resultado: dict, ativo_codigo: str, metadado: dict, ano: int, mes: str
    ) -> int:
        """Processa formato de texto (dados cadastrais + índices)."""
        total_registros = 0

        # 1. Dados cadastrais
        if "dados_cadastrais" in resultado:
            registros = await self._process_dados_cadastrais(
                resultado["dados_cadastrais"], ativo_codigo
            )
            total_registros += registros

        # 2. Índices de acompanhamento
        if "indices_acompanhamento" in resultado:
            registros = await self._process_indices_acompanhamento(
                resultado["indices_acompanhamento"], ativo_codigo, mes, ano, metadado
            )
            total_registros += registros

        return total_registros

    async def _process_image_format(
        self, resultado: dict, ativo_codigo: str, metadado: dict
    ) -> int:
        """Processa formato de imagem (séries temporais de gráficos)."""
        total_registros = 0

        # 1. Contratos mensais
        if "contratos_mensal" in resultado:
            registros = await self._process_contratos_mensal(
                resultado["contratos_mensal"], ativo_codigo, metadado
            )
            total_registros += registros

        # 2. Prazo médio dos recebíveis
        if "prazo_medio_recebiveis" in resultado:
            registros = await self._process_prazo_medio_recebiveis(
                resultado["prazo_medio_recebiveis"], ativo_codigo, metadado
            )
            total_registros += registros

        # 3. Taxa média dos recebíveis
        if "taxa_media_recebiveis" in resultado:
            registros = await self._process_taxa_media_recebiveis(
                resultado["taxa_media_recebiveis"], ativo_codigo, metadado
            )
            total_registros += registros

        return total_registros

    async def _process_dados_cadastrais(self, dados: dict, ativo_codigo: str) -> int:
        """Processa dados cadastrais do Somacred."""
        registros = 0

        for campo, valor in dados.items():
            # Normaliza nome do indicador em snake_case
            indicador_nome = campo.replace(" ", "_").lower()

            # Busca indicador
            indicador_id = await self._get_or_find_indicador(indicador_nome)

            if indicador_id:
                await self.repository.insert_dados_cadastrais(
                    ativo_codigo, indicador_id, str(valor)
                )
                registros += 1

        return registros

    async def _process_indices_acompanhamento(
        self, indices: list[dict], ativo_codigo: str, mes: str, ano: int, metadado: dict
    ) -> int:
        """Processa índices de acompanhamento."""
        registros = 0

        for item in indices:
            nome = item.get("nome", "")
            limite = item.get("limite", "")
            valor = float(item.get("valor", 0)) if item.get("valor") is not None else None

            # Busca indicador
            indicador_id = await self._get_or_find_indicador(nome)

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

    async def _process_contratos_mensal(
        self, contratos_data: list[dict], ativo_codigo: str, metadado: dict
    ) -> int:
        """Processa dados de contratos mensais."""
        registros = 0

        indicador_id = await self._get_or_find_indicador("num_contratos")

        if not indicador_id:
            return 0

        for item in contratos_data:
            ano = str(item["ano"])
            mes = self._convert_mes_to_number(item["mes"])
            quantidade = int(item["quantidade"]) if item["quantidade"] is not None else None

            if quantidade is not None:
                await self.repository.insert_indicador_valor(
                    ativo_codigo=ativo_codigo,
                    indicador_id=indicador_id,
                    valor=quantidade,
                    extra_data=metadado,
                    mes=mes,
                    ano=int(ano),
                )
                registros += 1

        return registros

    async def _process_prazo_medio_recebiveis(
        self, prazo_data: list[dict], ativo_codigo: str, metadado: dict
    ) -> int:
        """Processa dados de prazo médio dos recebíveis."""
        registros = 0

        indicador_id = await self._get_or_find_indicador("prazo_medio_recebiveis_dias")

        if not indicador_id:
            return 0

        for item in prazo_data:
            ano = str(item["ano"])
            mes = self._convert_mes_to_number(item["mes"])
            prazo_medio = (
                float(item["prazo_medio_dias"]) if item["prazo_medio_dias"] is not None else None
            )

            if prazo_medio is not None:
                await self.repository.insert_indicador_valor(
                    ativo_codigo=ativo_codigo,
                    indicador_id=indicador_id,
                    valor=prazo_medio,
                    extra_data=metadado,
                    mes=mes,
                    ano=int(ano),
                )
                registros += 1

        return registros

    async def _process_taxa_media_recebiveis(
        self, taxa_data: list[dict], ativo_codigo: str, metadado: dict
    ) -> int:
        """Processa dados de taxa média dos recebíveis."""
        registros = 0

        indicador_id = await self._get_or_find_indicador("taxa_media_recebiveis_a_a")

        if not indicador_id:
            return 0

        for item in taxa_data:
            ano = str(item["ano"])
            mes = self._convert_mes_to_number(item["mes"])
            taxa_media = (
                float(item["taxa_media_a_a"]) if item["taxa_media_a_a"] is not None else None
            )

            if taxa_media is not None:
                await self.repository.insert_indicador_valor(
                    ativo_codigo=ativo_codigo,
                    indicador_id=indicador_id,
                    valor=taxa_media,
                    extra_data=metadado,
                    mes=mes,
                    ano=int(ano),
                )
                registros += 1

        return registros
