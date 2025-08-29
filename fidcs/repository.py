"""
Repository para operações de banco de dados do módulo FIDCS.

Centraliza todas as operações de banco usando SQLAlchemy ORM.
"""

from datetime import datetime

from modules.ativos.model import Ativo
from modules.pydanticai.entity import ClientIa, ClientModel, ModelSchema, Prompt
from sqlalchemy import and_, func, or_, select
from sqlalchemy.dialects.postgresql import aggregate_order_by, insert
from sqlalchemy.ext.asyncio import AsyncSession

from .entity import FIDCDadosCadastrais, IndicadorFIDC, IndicadorFIDCValor
from .schema import DadosCadastraisResponseSchema, PromptInfoSchema


class FidcsRepository:
    """Repository para operações do módulo FIDCS."""

    def __init__(self, session: AsyncSession):
        """
        Inicializa repository com sessão do banco.

        Args:
            session: Sessão assíncrona do SQLAlchemy
        """
        self.session = session

    async def get_prompts_by_fidc_info(self, fidc_nome: str) -> list[PromptInfoSchema]:
        """
        Busca prompts baseado no nome do FIDC.

        Args:
            fidc_nome: Nome do FIDC extraído do arquivo

        Returns:
            list[PromptInfoSchema]: Lista de prompts encontrados (pode ser vazia)
        """
        query = (
            select(
                Prompt.temperatura,
                Prompt.max_tokens,
                Prompt.prompt_sistema,
                Prompt.prompt_usuario,
                Prompt.is_image,
                func.array_agg(
                    aggregate_order_by(
                        func.concat(ClientIa.client_abrev, ":", ClientModel.model_nm),
                        ClientModel.ordenacao, ClientIa.client_id
                    )
                )[1:3].label("model_nm"),
                ModelSchema.model_nm.label("schema_name"),
            )
            .select_from(Prompt)
            .join(ModelSchema, Prompt.model_schema_id == ModelSchema.model_schema_id)
            .join(ClientModel, Prompt.client_model_id == ClientModel.client_model_id)
            .join(ClientIa, ClientModel.client_id == ClientIa.client_id)
            .where(
                and_(
                    Prompt.ativo == True,
                    Prompt.codigo_ativo.isnot(None),
                    ModelSchema.model_nm.ilike(f"%{fidc_nome.lower()}%"),
                )
            )
            .group_by(
                Prompt.is_image,
                Prompt.temperatura,
                Prompt.max_tokens,
                Prompt.prompt_sistema,
                Prompt.prompt_usuario,
                ModelSchema.model_nm,
            )
            .order_by(Prompt.is_image)
        )

        result = await self.session.execute(query)
        prompts = []
        for row in result:
            prompt_data = dict(row._mapping)
            prompts.append(
                PromptInfoSchema(
                    model_name=prompt_data["model_nm"],
                    schema_name=prompt_data["schema_name"],
                    is_image=prompt_data["is_image"],
                    temperatura=prompt_data["temperatura"],
                    max_tokens=prompt_data["max_tokens"],
                    system_prompt=prompt_data["prompt_sistema"],
                    user_prompt=prompt_data["prompt_usuario"],
                )
            )
        return prompts

    async def get_ativo_codigo_by_schema(self, schema_name: str) -> str | None:
        """
        Busca código do ativo através do schema utilizado.

        Args:
            schema_name: Nome do schema da resposta da API

        Returns:
            str | None: Código do ativo ou None se não encontrado
        """
        query = (
            select(Prompt.codigo_ativo)
            .join(ModelSchema, Prompt.model_schema_id == ModelSchema.model_schema_id)
            .where(
                and_(
                    ModelSchema.model_nm == schema_name,
                    Prompt.ativo == True,
                    Prompt.codigo_ativo.isnot(None),
                )
            )
            .order_by(Prompt.prompt_id)
            .limit(1)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_or_find_indicador(
        self, nome: str, categoria: str = "FIDC"
    ) -> IndicadorFIDC | None:
        """
        Busca indicador existente na tabela.

        Args:
            nome: Nome do indicador
            categoria: Categoria do indicador

        Returns:
            IndicadorFIDC | None: Indicador encontrado ou None
        """
        # Valida se o nome não está vazio
        if not nome or nome.strip() == "":
            return None

        # Busca exata (case-insensitive)
        query = select(IndicadorFIDC).where(IndicadorFIDC.indicador_fidc_nm.ilike(nome))

        result = await self.session.execute(query)
        indicador = result.scalar_one_or_none()

        if indicador:
            return indicador

        # Busca por ILIKE (bilateral) - apenas se nome não for muito curto
        if len(nome.strip()) >= 2:  # Evita buscas muito amplas
            query = (
                select(IndicadorFIDC)
                .where(
                    or_(
                        IndicadorFIDC.indicador_fidc_nm.ilike(f"%{nome}%"),
                        func.lower(nome).like(f"%{func.lower(IndicadorFIDC.indicador_fidc_nm)}%"),
                    )
                )
                .order_by(func.length(IndicadorFIDC.indicador_fidc_nm))
            )

            result = await self.session.execute(query)
            indicador = result.scalar_one_or_none()

        return indicador

    async def insert_indicador_valor(
        self,
        ativo_codigo: str,
        indicador_id: int,
        valor: float | None = None,
        limite: str | None = None,
        limite_superior: bool | None = None,
        extra_data: dict | None = None,
        mes: str = None,
        ano: int = None,
    ) -> None:
        """
        Insere ou atualiza valor de indicador.

        Args:
            ativo_codigo: Código do ativo
            indicador_id: ID do indicador
            valor: Valor do indicador
            limite: Limite do indicador
            limite_superior: Se é limite superior
            extra_data: Dados extras em JSON
            mes: Mês de referência
            ano: Ano de referência
        """

        # Se não fornecido, usa período atual
        if not mes or not ano:
            now = datetime.now()
            mes = mes or f"{now.month:02d}"
            ano = ano or now.year

        # Prepara dados para insert
        dados = {
            "ativo_codigo": ativo_codigo,
            "indicador_fidc_id": indicador_id,
            "valor": valor,
            "limite": limite,
            "limite_superior": limite_superior,
            "extra_data": extra_data,
            "mes": mes,
            "ano": ano,
            "data_captura": datetime.now(),
        }

        # Insert com ON CONFLICT usando PostgreSQL dialect
        stmt = insert(IndicadorFIDCValor).values(dados)
        stmt = stmt.on_conflict_do_update(
            index_elements=["ativo_codigo", "indicador_fidc_id", "mes", "ano"],
            set_={
                "valor": stmt.excluded.valor,
                "limite": stmt.excluded.limite,
                "limite_superior": stmt.excluded.limite_superior,
                "extra_data": stmt.excluded.extra_data,
                "data_captura": stmt.excluded.data_captura,
            },
        )

        await self.session.execute(stmt)

    async def insert_dados_cadastrais(
        self, ativo_codigo: str, indicador_id: int, valor: str
    ) -> None:
        """
        Insere ou atualiza dados cadastrais.

        Args:
            ativo_codigo: Código do ativo
            indicador_id: ID do indicador
            valor: Valor como string
        """

        dados = {"ativo_codigo": ativo_codigo, "indicador_fidc_id": indicador_id, "valor": valor}

        # Insert com ON CONFLICT
        stmt = insert(FIDCDadosCadastrais).values(dados)
        stmt = stmt.on_conflict_do_update(
            index_elements=["ativo_codigo", "indicador_fidc_id"],
            set_={"valor": stmt.excluded.valor},
        )

        await self.session.execute(stmt)

    async def get_dados_consolidados(self) -> list[dict]:
        """
        Executa consulta consolidada dos dados FIDC usando ORM.

        Returns:
            list[dict]: Dados consolidados
        """
        query = (
            select(
                Ativo.apelido,
                IndicadorFIDC.indicador_fidc_nm,
                IndicadorFIDCValor.valor,
                IndicadorFIDCValor.limite,
                IndicadorFIDCValor.limite_superior,
                IndicadorFIDCValor.extra_data,
                IndicadorFIDCValor.mes,
                IndicadorFIDCValor.ano,
                IndicadorFIDCValor.data_captura,
            )
            .select_from(IndicadorFIDCValor)
            .join(
                IndicadorFIDC,
                IndicadorFIDCValor.indicador_fidc_id == IndicadorFIDC.indicador_fidc_id,
            )
            .join(Ativo, Ativo.codigo == IndicadorFIDCValor.ativo_codigo)
            .order_by(
                Ativo.apelido,
                IndicadorFIDC.indicador_fidc_nm,
                IndicadorFIDCValor.ano.desc(),
                IndicadorFIDCValor.mes.desc(),
            )
        )

        result = await self.session.execute(query)

        dados = []
        for row in result:
            dados.append(
                {
                    "apelido": row.apelido,
                    "indicador_fidc_nm": row.indicador_fidc_nm,
                    "valor": row.valor,
                    "limite": row.limite,
                    "limite_superior": row.limite_superior,
                    "extra_data": row.extra_data,
                    "mes": row.mes,
                    "ano": row.ano,
                    "data_captura": row.data_captura,
                }
            )

        return dados

    async def get_dados_cadastrais(self) -> list[DadosCadastraisResponseSchema]:
        """
        Executa consulta de dados cadastrais usando ORM.

        Returns:
            list[DadosCadastraisResponseSchema]: Dados cadastrais
        """
        query = (
            select(
                Ativo.apelido,
                IndicadorFIDC.indicador_fidc_nm,
                FIDCDadosCadastrais.valor,
            )
            .select_from(FIDCDadosCadastrais)
            .join(
                IndicadorFIDC,
                FIDCDadosCadastrais.indicador_fidc_id == IndicadorFIDC.indicador_fidc_id,
            )
            .join(Ativo, Ativo.codigo == FIDCDadosCadastrais.ativo_codigo)
            .order_by(
                Ativo.apelido,
                IndicadorFIDC.indicador_fidc_nm,
            )
        )

        result = await self.session.execute(query)

        dados = []
        for row in result:
            dados.append(
                DadosCadastraisResponseSchema(
                    apelido=row.apelido,
                    indicador_fidc_nm=row.indicador_fidc_nm,
                    valor=row.valor,
                )
            )

        return dados

    async def commit(self) -> None:
        """Efetua commit das transações pendentes."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Efetua rollback das transações pendentes."""
        await self.session.rollback()
