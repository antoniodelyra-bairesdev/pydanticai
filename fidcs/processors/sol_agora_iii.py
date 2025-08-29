"""
Processor específico para FIDC Sol Agora III.

Implementa lógica de parseamento e inserção de dados
específica para relatórios do FIDC Sol Agora III.
"""

from .base import BaseFIDCProcessor


class SolAgoraProcessor(BaseFIDCProcessor):
    """Processor para FIDC Sol Agora III."""

    async def process_data(
        self, api_response: dict, ativo_codigo: str, filename: str = None
    ) -> int:
        """Processa dados do FIDC Sol Agora III."""
        resultado = api_response.get("resultado", {})
        metadado = self._create_metadado(api_response)
        total_registros = 0

        # Usa ano e mês do api_response
        ano = api_response.get("ano")
        mes = str(api_response.get("mes")).zfill(2)  # Garante formato MM

        if not ano or not mes:
            # Se não tem ano/mês, não processa
            return 0

        # 1. Indicadores da última data
        if "indicadores_ultima_data" in resultado:
            registros = await self._process_indicadores_ultima_data(
                resultado["indicadores_ultima_data"], ativo_codigo, mes, int(ano), metadado
            )
            total_registros += registros

        # 2. Indicadores de monitoramento
        if "indicadores_monitoramento" in resultado:
            registros = await self._process_indicadores_monitoramento(
                resultado["indicadores_monitoramento"], ativo_codigo, mes, int(ano), metadado
            )
            total_registros += registros

        # 3. Indicadores de concentração PF
        if "indicadores_concentracao_pf" in resultado:
            registros = await self._process_indicadores_concentracao(
                resultado["indicadores_concentracao_pf"],
                ativo_codigo,
                mes,
                int(ano),
                metadado,
                "PF",
            )
            total_registros += registros

        # 4. Indicadores de concentração PJ
        if "indicadores_concentracao_pj" in resultado:
            registros = await self._process_indicadores_concentracao(
                resultado["indicadores_concentracao_pj"],
                ativo_codigo,
                mes,
                int(ano),
                metadado,
                "PJ",
            )
            total_registros += registros

        # 5. Indicadores principais
        if "indicadores_principais" in resultado:
            registros = await self._process_indicadores_principais(
                resultado["indicadores_principais"], ativo_codigo, mes, int(ano), metadado
            )
            total_registros += registros

        # 6. Indicadores CVNP
        if "indicadores_cvnp" in resultado:
            registros = await self._process_indicadores_cvnp(
                resultado["indicadores_cvnp"], ativo_codigo, mes, int(ano), metadado
            )
            total_registros += registros

        # 7. Faixas de PDD
        if "faixa_pdd" in resultado:
            registros = await self._process_faixa_pdd(
                resultado["faixa_pdd"], ativo_codigo, mes, int(ano), metadado
            )
            total_registros += registros

        return total_registros

    async def _process_indicadores_ultima_data(
        self, indicadores_data: dict, ativo_codigo: str, mes: str, ano: int, metadado: dict
    ) -> int:
        """Processa indicadores da última data."""
        registros = 0

        for campo, valor in indicadores_data.items():
            indicador_nome = campo.replace(" ", "_").lower()
            valor_float = float(valor) if valor is not None else None

            if valor_float is not None:
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

    async def _process_indicadores_monitoramento(
        self, indicadores_data: list[dict], ativo_codigo: str, mes: str, ano: int, metadado: dict
    ) -> int:
        """Processa indicadores de monitoramento."""
        registros = 0

        for item in indicadores_data:
            nome = item.get("nome", "")
            limite = item.get("limite", "")
            valor = float(item.get("valor", 0)) if item.get("valor") is not None else None

            if valor is not None:
                indicador_id = await self._get_or_find_indicador(nome)

                if indicador_id:
                    # Adiciona limite ao metadado
                    metadado_item = {
                        **metadado,
                        "limite_estabelecido": limite,
                        "nome_original": nome,
                    }

                    await self.repository.insert_indicador_valor(
                        ativo_codigo=ativo_codigo,
                        indicador_id=indicador_id,
                        valor=valor,
                        limite=limite,
                        extra_data=metadado_item,
                        mes=mes,
                        ano=ano,
                    )
                    registros += 1

        return registros

    async def _process_indicadores_concentracao(
        self,
        indicadores_data: list[dict],
        ativo_codigo: str,
        mes: str,
        ano: int,
        metadado: dict,
        tipo: str,
    ) -> int:
        """Processa indicadores de concentração (PF ou PJ)."""
        registros = 0

        for item in indicadores_data:
            nome = item.get("nome", "")
            limite = item.get("limite", "")
            valor = float(item.get("valor", 0)) if item.get("valor") is not None else None

            if valor is not None:
                indicador_id = await self._get_or_find_indicador(nome)

                if indicador_id:
                    # Adiciona tipo e limite ao metadado
                    metadado_item = {
                        **metadado,
                        "limite_estabelecido": limite,
                        "tipo_concentracao": tipo,
                        "nome_original": nome,
                    }

                    await self.repository.insert_indicador_valor(
                        ativo_codigo=ativo_codigo,
                        indicador_id=indicador_id,
                        valor=valor,
                        limite=limite,
                        extra_data=metadado_item,
                        mes=mes,
                        ano=ano,
                    )
                    registros += 1

        return registros

    async def _process_indicadores_principais(
        self, indicadores_data: dict, ativo_codigo: str, mes: str, ano: int, metadado: dict
    ) -> int:
        """Processa indicadores principais."""
        registros = 0

        for campo, valor in indicadores_data.items():
            indicador_nome = campo.replace(" ", "_").lower()
            valor_float = float(valor) if valor is not None else None

            if valor_float is not None:
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

    async def _process_indicadores_cvnp(
        self, indicadores_data: dict, ativo_codigo: str, mes: str, ano: int, metadado: dict
    ) -> int:
        """Processa indicadores CVNP."""
        registros = 0

        for campo, valor in indicadores_data.items():
            indicador_nome = campo.replace(" ", "_")
            valor_float = float(valor) if valor is not None else None

            if valor_float is not None:
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

    async def _process_faixa_pdd(
        self, faixa_data: dict, ativo_codigo: str, mes: str, ano: int, metadado: dict
    ) -> int:
        """Processa faixas de PDD."""
        registros = 0

        for faixa, valor in faixa_data.items():
            indicador_nome = faixa.lower().replace(" ", "_")
            valor_float = float(valor) if valor is not None else None

            if valor_float is not None:
                indicador_id = await self._get_or_find_indicador(indicador_nome)

                if indicador_id:
                    # Adiciona informação da faixa ao metadado
                    metadado_item = {
                        **metadado,
                        "faixa_original": faixa,
                        "categoria_pdd": faixa.replace("faixa_", "").upper(),
                    }

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
