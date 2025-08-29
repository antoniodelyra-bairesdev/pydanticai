"""
Processor específico para FIDC iCred.

Implementa lógica de parseamento e inserção de dados
específica para relatórios do FIDC iCred (texto e imagem).
"""

from .base import BaseFIDCProcessor


class IcredProcessor(BaseFIDCProcessor):
    """Processor para FIDC iCred."""

    async def process_data(
        self, api_response: dict, ativo_codigo: str, filename: str = None
    ) -> int:
        """
        Processa dados específicos do FIDC iCred.

        Args:
            api_response: Resposta da API PydanticAI
            ativo_codigo: Código do ativo

        Returns:
            int: Total de registros inseridos/atualizados
                """
        resultado = api_response.get("resultado", {})

        # Converte objeto Pydantic para dicionário
        resultado_dict = resultado.model_dump()

        metadado = self._create_metadado(api_response)
        total_registros = 0

        # Usa ano e mês do api_response
        ano = api_response.get("ano")
        mes = str(api_response.get("mes")).zfill(2)  # Garante formato MM

        if not ano or not mes:
            # Se não tem ano/mês, não processa
            return 0

        # Determina se é formato texto ou imagem baseado no schema
        schema_usado = api_response.get("schema_utilizado", "")
        is_image_format = "image" in schema_usado.lower()

        if is_image_format:
            total_registros = await self._process_image_format(resultado_dict, ativo_codigo, metadado)
        else:
            total_registros = await self._process_text_format(
                resultado_dict, ativo_codigo, metadado, ano, mes
            )

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
        """Processa formato de imagem (séries temporais)."""
        total_registros = 0

        # 1. Fluxo de caixa dos direitos creditórios
        if "fluxo_de_caixa_dos_direitos_creditorios" in resultado:
            registros = await self._process_fluxo_caixa_creditorios(
                resultado["fluxo_de_caixa_dos_direitos_creditorios"], ativo_codigo, metadado
            )
            total_registros += registros

        # 2. Direitos creditórios e PDD
        if "direitos_creditorios_e_pdd" in resultado:
            registros = await self._process_direitos_creditorios_pdd(
                resultado["direitos_creditorios_e_pdd"], ativo_codigo, metadado
            )
            total_registros += registros

        # 3. Prazo médio dos recebíveis
        if "prazo_medio_dos_recebiveis_dias" in resultado:
            registros = await self._process_prazo_medio_recebiveis(
                resultado["prazo_medio_dos_recebiveis_dias"], ativo_codigo, metadado
            )
            total_registros += registros

        # 4. Taxa média dos recebíveis
        if "taxa_media_dos_recebiveis_percent_a_a" in resultado:
            registros = await self._process_taxa_media_recebiveis(
                resultado["taxa_media_dos_recebiveis_percent_a_a"], ativo_codigo, metadado
            )
            total_registros += registros

        # 5. Quantidade de contratos
        if "contratos_valor_medio_e_quantidade" in resultado:
            registros = await self._process_contratos_quantidade(
                resultado["contratos_valor_medio_e_quantidade"], ativo_codigo, metadado
            )
            total_registros += registros

        return total_registros

    async def _process_dados_cadastrais(self, dados: dict, ativo_codigo: str) -> int:
        """Processa dados cadastrais do iCred."""
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
            indicador_nome = item.get("indice_de_acompanhamento", "").replace(" ", "_").lower()
            limite = item.get("limite", "")
            valor = float(item.get("valor", 0)) if item.get("valor") is not None else None

            # Valida se o nome do indicador não está vazio
            if not indicador_nome or indicador_nome.strip() == "":
                continue

            # Busca indicador
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

    async def _process_fluxo_caixa_creditorios(
        self, fluxo_data: list[dict], ativo_codigo: str, metadado: dict
    ) -> int:
        """Processa fluxo de caixa dos direitos creditórios."""
        registros = 0

        for item in fluxo_data:
            ano = str(item["ano"])
            mes = self._convert_mes_to_number(item["mes"])
            aquisicoes = float(item["aquisicoes"]) if item["aquisicoes"] is not None else None
            liquidacoes = float(item["liquidacoes"]) if item["liquidacoes"] is not None else None

            # Insere aquisições
            if aquisicoes is not None:
                indicador_id = await self._get_or_find_indicador("aquisicoes")

                if indicador_id:
                    await self.repository.insert_indicador_valor(
                        ativo_codigo=ativo_codigo,
                        indicador_id=indicador_id,
                        valor=aquisicoes,
                        extra_data=metadado,
                        mes=mes,
                        ano=int(ano),
                    )
                    registros += 1

            # Insere liquidações
            if liquidacoes is not None:
                indicador_id = await self._get_or_find_indicador("liquidacoes")

                if indicador_id:
                    await self.repository.insert_indicador_valor(
                        ativo_codigo=ativo_codigo,
                        indicador_id=indicador_id,
                        valor=liquidacoes,
                        extra_data=metadado,
                        mes=mes,
                        ano=int(ano),
                    )
                    registros += 1

        return registros

    async def _process_direitos_creditorios_pdd(
        self, dc_pdd_data: list[dict], ativo_codigo: str, metadado: dict
    ) -> int:
        """Processa dados de direitos creditórios e PDD."""
        registros = 0

        for item in dc_pdd_data:
            ano = str(item["ano"])
            mes = self._convert_mes_to_number(item["mes"])

            # Lista de campos para inserir
            campos = ["dc_vencidos", "dc_a_vencer", "pdd_dc"]

            for campo in campos:
                valor = item.get(campo)
                if valor is not None:
                    valor_float = float(valor)

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

    async def _process_prazo_medio_recebiveis(
        self, prazo_data: list[dict], ativo_codigo: str, metadado: dict
    ) -> int:
        """Processa prazo médio dos recebíveis."""
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
        """Processa taxa média dos recebíveis."""
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

    async def _process_contratos_quantidade(
        self, contratos_data: list[dict], ativo_codigo: str, metadado: dict
    ) -> int:
        """Processa quantidade de contratos."""
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
