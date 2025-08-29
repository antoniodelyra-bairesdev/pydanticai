"""
Service principal do módulo FIDCS.

Contém lógica de negócio, factory de processadores e orquestração do processamento de arquivos FIDC.
"""

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from modules.integrations.enums import FerramentaExtracaoEnum, TipoExtracaoEnum
from modules.pydanticai.service import PydanticAIService

if TYPE_CHECKING:
    from modules.fidcs.processors.base import BaseFIDCProcessor
    from modules.fidcs.repository import FidcsRepository

from .processors.bemol import BemolProcessor
from .processors.brz_consignados_v import BrzProcessor
from .processors.icred import IcredProcessor
from .processors.sol_agora_iii import SolAgoraProcessor
from .processors.somacred import SomacredProcessor
from .processors.valora_alion_ii import AlionProcessor
from .processors.valora_noto import NotoProcessor
from .processors.verde_card import VerdeCardProcessor
from .schema import (
    ArquivoPromptInfoSchema,
    DadosCadastraisResponseSchema,
    DadosConsolidadosSchema,
    ProcessamentoDetalheSchema,
    ProcessarRequestSchema,
    ProcessarResponseSchema,
)


class FIDCProcessorFactory:
    """Factory para criação de processadores específicos de FIDC."""

    # Mapeamento schema → processor
    SCHEMA_PROCESSOR_MAP = {
        "bemol": BemolProcessor,
        "icred": IcredProcessor,
        "icred_image": IcredProcessor,
        "somacred": SomacredProcessor,
        "somacred_image": SomacredProcessor,
        "valora_noto": NotoProcessor,
        "valora_noto_image": NotoProcessor,
        "sol_agora_iii": SolAgoraProcessor,
        "brz_consignados_v": BrzProcessor,
        "valora_alion_ii": AlionProcessor,
        "valora_alion_ii_image": AlionProcessor,
        "verde_card": VerdeCardProcessor,
    }

    @classmethod
    def create_processor(
        cls, schema_name: str, repository: "FidcsRepository"
    ) -> "BaseFIDCProcessor":
        """
        Cria processador específico baseado no schema.

        Args:
            schema_name: Nome do schema da API
            repository: Repository para operações de banco

        Returns:
            BaseFIDCProcessor: Processador específico

        Raises:
            ValueError: Se schema não for suportado
        """
        processor_class = cls.SCHEMA_PROCESSOR_MAP.get(schema_name)

        if not processor_class:
            available = ", ".join(cls.SCHEMA_PROCESSOR_MAP.keys())
            raise ValueError(
                f"Schema '{schema_name}' não suportado. Schemas disponíveis: {available}"
            )

        return processor_class(repository)

    @classmethod
    def get_supported_schemas(cls) -> list[str]:
        """Retorna lista de schemas suportados."""
        return list(cls.SCHEMA_PROCESSOR_MAP.keys())


class FidcsService:
    """Service principal do módulo FIDCS."""

    def __init__(self, repository: "FidcsRepository", pydantic_ai_service: PydanticAIService):
        """
        Inicializa service com dependências.

        Args:
            repository: Repository para operações de banco
            pydantic_ai_service: Service do PydanticAI para chamadas de API
        """
        self.repository = repository
        self.pydantic_ai_service = pydantic_ai_service
        self.factory = FIDCProcessorFactory()

    def get_arquivos_do_diretorio(self, diretorio: str = "files/fidcs") -> list[dict]:
        """
        Lista arquivos PDF no diretório especificado.

        Args:
            diretorio: Caminho do diretório com arquivos

        Returns:
            list[dict]: Lista com informações dos arquivos
        """
        arquivos = []
        diretorio_path = Path(diretorio)

        if not diretorio_path.exists():
            return arquivos

        for arquivo_path in diretorio_path.glob("*.pdf"):
            try:
                stat = arquivo_path.stat()
                arquivos.append(
                    {
                        "nome_arquivo": arquivo_path.name,
                        "caminho_completo": str(arquivo_path),
                        "tamanho": stat.st_size,
                        "data_modificacao": datetime.fromtimestamp(stat.st_mtime),
                    }
                )
            except Exception:
                continue  # Pula arquivos com problemas

        return sorted(arquivos, key=lambda x: x["nome_arquivo"])

    def extrair_info_arquivo(self, nome_arquivo: str) -> dict | None:
        """
        Extrai informações do nome do arquivo FIDC.

        Padrão esperado: FIDC_[NOME]_[ANO]_[MES].pdf

        Args:
            nome_arquivo: Nome do arquivo

        Returns:
            dict | None: Informações extraídas ou None se padrão inválido
        """
        # Remove extensão .pdf
        nome_sem_ext = nome_arquivo.replace(".pdf", "")

        # Divide por underscore
        parts = nome_sem_ext.split("_")

        if len(parts) < 4 or parts[0].upper() != "FIDC":
            return None

        try:
            # FIDC_NOME_ANO_MES ou FIDC_NOME_COMPOSTO_ANO_MES
            ano = int(parts[-2])
            mes = int(parts[-1])

            # Nome do FIDC pode ter múltiplas partes
            fidc_nome = "_".join(parts[1:-2])

            return {"fidc_nome": fidc_nome, "ano": ano, "mes": mes}
        except (ValueError, IndexError):
            return None

    async def listar_arquivos_e_prompts(self) -> list[ArquivoPromptInfoSchema]:
        """
        Lista arquivos na pasta e busca prompts correspondentes.

        Returns:
            list[ArquivoPromptInfoSchema]: Lista com informações dos arquivos e prompts
        """
        resultado = []

        # Lista arquivos do diretório
        arquivos = self.get_arquivos_do_diretorio()

        for arquivo_info in arquivos:
            nome_arquivo = arquivo_info["nome_arquivo"]

            # Extrai informações do nome do arquivo
            info_arquivo = self.extrair_info_arquivo(nome_arquivo)

            if not info_arquivo:
                # Arquivo não segue padrão esperado
                resultado.append(
                    ArquivoPromptInfoSchema(
                        arquivo=nome_arquivo,
                        fidc_nome="FORMATO_INVALIDO",
                        ano=0,
                        mes=0,
                        prompt_encontrado=False,
                    )
                )
                continue

            # Busca prompts correspondentes
            prompts = await self.repository.get_prompts_by_fidc_info(info_arquivo["fidc_nome"])

            if prompts:
                # Cria um registro para cada prompt encontrado
                for prompt in prompts:
                    # Combina PromptInfoSchema com dados do arquivo
                    arquivo_prompt = ArquivoPromptInfoSchema(
                        arquivo=nome_arquivo,
                        fidc_nome=info_arquivo["fidc_nome"],
                        ano=info_arquivo["ano"],
                        mes=info_arquivo["mes"],
                        prompt_encontrado=True,
                        # Herda campos do PromptInfoSchema
                        model_name=prompt.model_name,
                        schema_name=prompt.schema_name,
                        is_image=prompt.is_image,
                        temperatura=prompt.temperatura,
                        max_tokens=prompt.max_tokens,
                        system_prompt=prompt.system_prompt,
                        user_prompt=prompt.user_prompt,
                    )
                    resultado.append(arquivo_prompt)
            else:
                resultado.append(
                    ArquivoPromptInfoSchema(
                        arquivo=nome_arquivo,
                        fidc_nome=info_arquivo["fidc_nome"],
                        ano=info_arquivo["ano"],
                        mes=info_arquivo["mes"],
                        prompt_encontrado=False,
                    )
                )

        return resultado

    async def processar_arquivos(self, request: ProcessarRequestSchema) -> ProcessarResponseSchema:
        """
        Processa lista de arquivos selecionados.

        Args:
            request: Request com lista de arquivos e prompts

        Returns:
            ProcessarResponseSchema: Resultado do processamento
        """
        sucessos = 0
        falhas = 0
        detalhes = []
        erros_gerais = []

        for item in request.itens:
            try:
                # Processa um arquivo individual
                detalhe = await self._processar_arquivo_individual(item)

                detalhes.append(detalhe)

                if detalhe.sucesso:
                    sucessos += 1
                else:
                    falhas += 1

            except Exception as e:
                # Erro geral no processamento
                erros_gerais.append(f"Erro ao processar {item.arquivo}: {str(e)}")
                falhas += 1

                detalhes.append(
                    ProcessamentoDetalheSchema(arquivo=item.arquivo, sucesso=False, erro=str(e))
                )

        return ProcessarResponseSchema(
            total_processados=len(request.itens),
            sucessos=sucessos,
            falhas=falhas,
            erros_gerais=erros_gerais,
            detalhes=detalhes,
        )

    async def _processar_arquivo_individual(
        self, item: ArquivoPromptInfoSchema
    ) -> ProcessamentoDetalheSchema:
        """
        Processa um arquivo individual.

        Args:
            item: Item com informações do arquivo e prompt

        Returns:
            ProcessamentoDetalheSchema: Resultado do processamento individual
        """
        try:
            # Valida se o prompt foi encontrado
            if not item.prompt_encontrado or not item.schema_name:
                return ProcessamentoDetalheSchema(
                    arquivo=item.arquivo,
                    sucesso=False,
                    erro="Prompt não encontrado ou schema não definido",
                )

            # Prepara parâmetros para a API
            caminho_arquivo = f"files/fidcs/{item.arquivo}"

            # Determina tipo de extração baseado no is_image
            tipo_extracao = (
                TipoExtracaoEnum.IMAGENS if item.is_image else TipoExtracaoEnum.MARKDOWN
            )

            # Cria arquivo mock para upload (FastAPI UploadFile)
            import io

            from fastapi import UploadFile
            from starlette.datastructures import Headers

            with open(caminho_arquivo, "rb") as f:
                file_content = f.read()

            # Cria headers com content-type
            headers = Headers({"content-type": "application/pdf"})

            file_obj = UploadFile(
                filename=item.arquivo,
                file=io.BytesIO(file_content),
                headers=headers,
            )

            # Chama API do PydanticAI
            api_response = await self.pydantic_ai_service.executar_consulta_com_arquivo(
                user_prompt=item.user_prompt,
                arquivo=file_obj,
                ferramenta_extracao=FerramentaExtracaoEnum.DOCLING,
                tipo_extracao=tipo_extracao,
                model=item.model_name,
                system_prompt=item.system_prompt,
                retries=2,
                max_tokens=item.max_tokens or 2440,
                temperature=item.temperatura or 0.1,
                schema_name=item.schema_name,
            )

            # Converte response para dict
            api_dict = {
                "resultado": api_response.resultado,
                "tempo_execucao": api_response.tempo_execucao,
                "tokens_utilizados": api_response.tokens_utilizados,
                "modelo_utilizado": api_response.modelo_utilizado,
                "schema_utilizado": api_response.schema_utilizado,
                "ano": item.ano,
                "mes": item.mes,
            }

            # Busca código do ativo
            ativo_codigo = await self.repository.get_ativo_codigo_by_schema(
                api_response.schema_utilizado
            )

            if not ativo_codigo:
                return ProcessamentoDetalheSchema(
                    arquivo=item.arquivo,
                    sucesso=False,
                    erro=f"Código do ativo não encontrado para schema {api_response.schema_utilizado}",
                )

            # Cria processador específico
            processor = self.factory.create_processor(
                api_response.schema_utilizado, self.repository
            )

            # Processa dados
            registros_inseridos = await processor.process_data(
                api_dict, ativo_codigo, item.arquivo
            )

            # Commit das transações
            await self.repository.commit()

            return ProcessamentoDetalheSchema(
                arquivo=item.arquivo,
                sucesso=True,
                registros_inseridos=registros_inseridos,
                tempo_execucao=api_response.tempo_execucao,
                tokens_utilizados=api_response.tokens_utilizados,
                modelo_utilizado=api_response.modelo_utilizado,
                schema_utilizado=api_response.schema_utilizado,
            )

        except Exception as e:
            # Rollback em caso de erro
            await self.repository.rollback()

            return ProcessamentoDetalheSchema(arquivo=item.arquivo, sucesso=False, erro=str(e))

    async def get_dados_consolidados(self) -> list[DadosConsolidadosSchema]:
        """
        Retorna dados consolidados da consulta SQL.

        Returns:
            list[DadosConsolidadosSchema]: Dados consolidados
        """
        dados = await self.repository.get_dados_consolidados()

        return [
            DadosConsolidadosSchema(
                apelido=item["apelido"],
                indicador_fidc_nm=item["indicador_fidc_nm"],
                valor=item["valor"],
                limite=item["limite"],
                limite_superior=item["limite_superior"],
                extra_data=item["extra_data"],
                mes=item["mes"],
                ano=item["ano"],
                data_captura=item["data_captura"],
            )
            for item in dados
        ]

    async def get_dados_cadastrais(self) -> list[DadosCadastraisResponseSchema]:
        """
        Retorna dados cadastrais da consulta SQL.

        Returns:
            list[DadosCadastraisResponseSchema]: Dados cadastrais
        """
        return await self.repository.get_dados_cadastrais()
