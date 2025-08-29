"""
Processor específico para FIDC Verde Card.

Implementa lógica de parseamento e inserção de dados
específica para relatórios do FIDC Verde Card.
"""

from .base import BaseFIDCProcessor


class VerdeCardProcessor(BaseFIDCProcessor):
    """Processor para FIDC Verde Card."""

    async def process_data(
        self, api_response: dict, ativo_codigo: str, filename: str = None
    ) -> int:
        """Processa dados do FIDC Verde Card."""
        resultado = api_response.get("resultado", {})
        metadado = self._create_metadado(api_response)
        total_registros = 0

        # Usa ano e mês do api_response
        ano = api_response.get("ano")
        mes = str(api_response.get("mes")).zfill(2)  # Garante formato MM

        if not ano or not mes:
            # Se não tem ano/mês, não processa
            return 0

        # Indicadores financeiros
        if "indicadores_financeiros" in resultado:
            registros = await self._process_lista_fechamento(
                resultado["indicadores_financeiros"],
                ativo_codigo,
                "VERDE_CARD_FINANCEIRO",
                mes,
                int(ano),
                metadado,
            )
            total_registros += registros

        # Índices de controle
        if "indices_de_controle" in resultado:
            registros = await self._process_lista_indicadores_com_limite(
                resultado["indices_de_controle"],
                ativo_codigo,
                "VERDE_CARD_CONTROLE",
                mes,
                int(ano),
                metadado,
            )
            total_registros += registros

        # Dados cadastrais estruturados
        secoes_cadastrais = ["gestao", "administracao_custodia", "caracteristicas_gerais"]

        for secao in secoes_cadastrais:
            if secao in resultado:
                registros = await self._process_dados_cadastrais_genericos(
                    resultado[secao], ativo_codigo, f"VERDE_CARD_{secao.upper()}"
                )
                total_registros += registros

        return total_registros

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
            indicador_nome = item.get("indicador", "").replace(" ", "_").lower()
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
                        ano=ano,
                    )
                    registros += 1

        return registros

    async def _process_lista_indicadores_com_limite(
        self,
        lista: list[dict],
        ativo_codigo: str,
        categoria: str,
        mes: str,
        ano: int,
        metadado: dict,
    ) -> int:
        """Processa lista de indicadores com valor e limite."""
        registros = 0

        for item in lista:
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
