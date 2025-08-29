"""
Processor específico para FIDC BRZ Consignados V.

Implementa lógica de parseamento e inserção de dados
específica para relatórios do FIDC BRZ Consignados V.
"""

from .base import BaseFIDCProcessor


class BrzProcessor(BaseFIDCProcessor):
    """Processor para FIDC BRZ Consignados V."""

    async def process_data(self, api_response: dict, ativo_codigo: str, filename: str = None) -> int:
        """Processa dados do FIDC BRZ Consignados V."""
        resultado = api_response.get("resultado", {})
        metadado = self._create_metadado(api_response)
        total_registros = 0

        # Usa ano e mês do api_response
        ano = api_response.get("ano")
        mes = str(api_response.get("mes")).zfill(2)  # Garante formato MM

        if not ano or not mes:
            # Se não tem ano/mês, não processa
            return 0

        # 1. Características gerais (dados cadastrais)
        if "caracteristicas_gerais" in resultado:
            registros = await self._process_caracteristicas_gerais(
                resultado["caracteristicas_gerais"], ativo_codigo
            )
            total_registros += registros

        # 2. Textos descritivos (dados cadastrais)
        registros = await self._process_textos_descritivos(resultado, ativo_codigo)
        total_registros += registros

        # 3. Informações da carteira (valores periódicos)
        if "informacoes_carteira" in resultado:
            registros = await self._process_informacoes_carteira(
                resultado["informacoes_carteira"], ativo_codigo, mes, int(ano), metadado
            )
            total_registros += registros

        # 4. Indicadores de controle (valores periódicos)
        if "indicadores" in resultado:
            registros = await self._process_indicadores_controle(
                resultado["indicadores"], ativo_codigo, mes, int(ano), metadado
            )
            total_registros += registros

        # 5. Parcelas liquidadas (valor periódico)
        if "parcelas_liquidadas" in resultado:
            valor_liquidado = float(resultado["parcelas_liquidadas"])
            registros = await self._process_parcelas_liquidadas(
                valor_liquidado, ativo_codigo, mes, int(ano), metadado
            )
            total_registros += registros

        # 6. Parcelas inadimplentes (valores periódicos)
        if "parcelas_inadimplentes" in resultado:
            registros = await self._process_parcelas_inadimplentes(
                resultado["parcelas_inadimplentes"], ativo_codigo, mes, int(ano), metadado
            )
            total_registros += registros

        return total_registros

    async def _process_caracteristicas_gerais(
        self, caracteristicas_data: dict, ativo_codigo: str
    ) -> int:
        """Processa características gerais (dados cadastrais)."""
        registros = 0

        for campo, valor in caracteristicas_data.items():
            indicador_nome = campo.replace(" ", "_")
            valor_str = str(valor)

            indicador_id = await self._get_or_find_indicador(indicador_nome)

            if indicador_id:
                await self.repository.insert_dados_cadastrais(
                    ativo_codigo, indicador_id, valor_str
                )
                registros += 1

        return registros

    async def _process_textos_descritivos(self, resultado: dict, ativo_codigo: str) -> int:
        """Processa textos descritivos (objetivo, política, público)."""
        registros = 0

        campos_texto = {
            "objetivo_fundo": "Objetivo do Fundo",
            "politica_investimento": "Política de Investimento",
            "publico_alvo": "Público Alvo"
        }

        for campo, nome_indicador in campos_texto.items():
            if campo in resultado:
                valor_str = str(resultado[campo])

                indicador_id = await self._get_or_find_indicador(nome_indicador)

                if indicador_id:
                    await self.repository.insert_dados_cadastrais(
                        ativo_codigo, indicador_id, valor_str
                    )
                    registros += 1

        return registros

    async def _process_informacoes_carteira(
        self, carteira_data: dict, ativo_codigo: str, mes: str, ano: int, metadado: dict
    ) -> int:
        """Processa informações da carteira (valores periódicos)."""
        registros = 0

        for campo, valor in carteira_data.items():
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
                        ano=ano
                    )
                    registros += 1

        return registros

    async def _process_indicadores_controle(
        self, indicadores_data: list[dict], ativo_codigo: str, mes: str, ano: int, metadado: dict
    ) -> int:
        """Processa indicadores de controle (valores periódicos)."""
        registros = 0

        for item in indicadores_data:
            indicador_nome = item.get("Indicador", "").replace(" ", "_")
            valor_exigido = float(item.get("exigido", 0)) if item.get("exigido") is not None else None
            valor_atual = float(item.get("atual", 0)) if item.get("atual") is not None else None
            situacao = item.get("situacao", "")

            if valor_atual is not None:
                indicador_id = await self._get_or_find_indicador(indicador_nome)

                if indicador_id:
                    # Adiciona situação e tipo ao metadado
                    metadado_item = {
                        **metadado,
                        "situacao": situacao,
                        "indicador_base": indicador_nome
                    }

                    await self.repository.insert_indicador_valor(
                        ativo_codigo=ativo_codigo,
                        indicador_id=indicador_id,
                        valor=valor_atual,
                        limite=str(valor_exigido) if valor_exigido is not None else None,
                        extra_data=metadado_item,
                        mes=mes,
                        ano=ano
                    )
                    registros += 1

        return registros

    async def _process_parcelas_liquidadas(
        self, valor_liquidado: float, ativo_codigo: str, mes: str, ano: int, metadado: dict
    ) -> int:
        """Processa valor de parcelas liquidadas."""
        indicador_id = await self._get_or_find_indicador("parcelas_liquidadas")

        if indicador_id:
            await self.repository.insert_indicador_valor(
                ativo_codigo=ativo_codigo,
                indicador_id=indicador_id,
                valor=valor_liquidado,
                extra_data=metadado,
                mes=mes,
                ano=ano
            )
            return 1

        return 0

    async def _process_parcelas_inadimplentes(
        self, inadimplentes_data: list[dict], ativo_codigo: str, mes: str, ano: int, metadado: dict
    ) -> int:
        """Processa parcelas inadimplentes como um único registro com detalhamento nos metadados."""
        indicador_id = await self._get_or_find_indicador("parcelas_inadimplentes")

        if not indicador_id:
            return 0

        # Calcula total de inadimplência
        total_inadimplentes = sum(
            float(item.get("valor", 0)) for item in inadimplentes_data
            if item.get("valor") is not None
        )

        # Cria estrutura detalhada nos metadados
        detalhamento_inadimplencia = {}
        for item in inadimplentes_data:
            periodo = item.get("periodo", "")
            valor = float(item.get("valor", 0)) if item.get("valor") is not None else 0

            # Adiciona ao detalhamento
            detalhamento_inadimplencia[periodo] = {
                "valor": valor,
                "percentual_do_total": round((valor / total_inadimplentes * 100), 2) if total_inadimplentes > 0 else 0
            }

        # Metadado completo com detalhamento
        metadado_completo = {
            **metadado,
            "detalhamento_por_periodo": detalhamento_inadimplencia,
            "total_inadimplentes": total_inadimplentes,
            "quantidade_periodos": len(inadimplentes_data)
        }

        await self.repository.insert_indicador_valor(
            ativo_codigo=ativo_codigo,
            indicador_id=indicador_id,
            valor=total_inadimplentes,
            extra_data=metadado_completo,
            mes=mes,
            ano=ano
        )

        return 1
