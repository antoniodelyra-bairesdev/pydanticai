from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus
import math
import pandas as pd
import logging

from dataclasses import dataclass
from datetime import datetime, date
from http import HTTPStatus
from fastapi import UploadFile
from fastapi.exceptions import HTTPException

from modules.rentabilidades.service import RentabilidadesService
from modules.arquivos.repository import ArquivosRepository
from modules.arquivos.model import Arquivo
from modules.util.feriados_financeiros_numpy import feriados
from modules.calculos.service import CalculosService
from .repository import FundosRepository
from .schema import (
    AtualizacaoInternaFundosSchema,
    FundoAdministradorSchema,
    FundoControladorSchema,
    FundoDocumentoSchema,
    IndiceBenchmarkSchema,
    InsertFundoInstitucionalSchema,
    PatchDetalhesFundoSiteInstitucionalSchema,
    PostDetalhesFundoSiteInstitucionalSchema,
    UpdateFundo,
    CreateFundoResponse,
    FundoCustodianteSchema,
    FundoSchema,
    UpdateFundoInstitucionalSchema,
    ArquivoSchema,
    PublicacaoMateriaisMassaSchema,
)
from .model import FundoCategoriaDocumento


@dataclass
class FundosService:
    fundos_repository: FundosRepository
    arquivos_repository: ArquivosRepository

    async def fundos_tipos_site_institucional(self):
        return await self.fundos_repository.lista_tipos_fundos_site_institucional()

    async def fundos_classificacoes_site_institucional(self):
        return (
            await self.fundos_repository.lista_classificacao_fundos_site_institucional()
        )

    async def fundos_site_institucional(self):
        relacionamentos = await self.fundos_repository.lista_fundos_site_institucional()
        return relacionamentos

    async def detalhes_fundo_site_institucional(self, nome_ou_ticker: str):
        fundo = await self.fundos_repository.lista_fundo_site_institucional_por_nome_ou_ticker_ou_id(
            nome_ou_ticker
        )
        if fundo == None:
            raise HTTPException(HTTPStatus.NOT_FOUND, "Fundo não encontrado")
        return fundo

    async def fundos(self):
        results = await self.fundos_repository.fundos()
        serialized = [
            FundoSchema.from_model(fundo).com_indices().com_publicacao()
            for fundo in results
        ]
        return serialized

    async def inserir_fundo(self, body: UpdateFundo):
        [id] = await self.fundos_repository.inserir_fundo(body)
        return CreateFundoResponse(id=id)

    async def _atualizar_documentos(
        self,
        id: int,
        dados_atualizacao: AtualizacaoInternaFundosSchema,
        arquivos: list[UploadFile],
    ):
        metadados = dados_atualizacao.metadados_documentos
        if len(arquivos) != len(metadados):
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                "Quantidade de metadados de documentos diferente de quantidade de arquivos.",
            )
        async with self.fundos_repository.db.begin_nested():
            await self.fundos_repository.remover_documentos(
                dados_atualizacao.atualizacao_fundo.remover_documentos
            )

            fundos_documentos: list[FundosRepository.InserirFundoDocumento] = []
            for informacoes in metadados:
                arquivo = arquivos[informacoes.posicao_arquivo]
                id_arquivo = await self.arquivos_repository.criar(
                    arquivo.file, arquivo.filename, arquivo.content_type
                )
                fundos_documentos.append(
                    {
                        "fundo_id": id,
                        "arquivo_id": id_arquivo,
                        "fundo_categoria_documento_id": informacoes.fundo_categoria_id,
                        "titulo": informacoes.titulo,
                        "criado_em": datetime.now(),
                        "data_referencia": informacoes.data_referencia,
                    }
                )
            ids_fundos_documentos = await self.fundos_repository.inserir_documentos(
                fundos_documentos
            )
            fundos_documentos_criados = [
                FundoDocumentoSchema(
                    id=ids_fundos_documentos[i],
                    criado_em=fundo_documento["criado_em"],
                    data_referencia=fundo_documento["data_referencia"],
                    titulo=fundo_documento["titulo"],
                    arquivo=ArquivoSchema(
                        id=fundo_documento["arquivo_id"],
                        nome=arquivos[i].filename or "unknown",
                        extensao=arquivos[i].content_type or "application/octet-stream",
                    ),
                )
                for i, fundo_documento in enumerate(fundos_documentos)
            ]
            return fundos_documentos_criados

    async def atualizar_fundo(
        self,
        id: int,
        dados_atualizacao: AtualizacaoInternaFundosSchema,
        arquivos: list[UploadFile],
    ):
        async with self.fundos_repository.db.begin_nested():
            novos_documentos = await self._atualizar_documentos(
                id, dados_atualizacao, arquivos
            )
            await self.fundos_repository.atualizar_fundo(
                id, dados_atualizacao.atualizacao_fundo
            )
            return novos_documentos

    async def fundos_custodiantes(self):
        results = await self.fundos_repository.fundos_custodiantes()
        serialized = [FundoCustodianteSchema.from_model(fundo) for fundo in results]
        return serialized

    async def fundos_controladores(self):
        results = await self.fundos_repository.fundos_controladores()
        serialized = [FundoControladorSchema.from_model(fundo) for fundo in results]
        return serialized

    async def fundos_administradores(self):
        results = await self.fundos_repository.fundos_administradores()
        serialized = [FundoAdministradorSchema.from_model(fundo) for fundo in results]
        return serialized

    async def get_fundo(self, id: int):
        fundo = await self.fundos_repository.fundo_detalhes(id)
        if not fundo:
            raise HTTPException(HTTPStatus.NOT_FOUND, "Fundo não encontrado.")
        detalhes_publicacao = await self.fundos_repository.lista_fundo_site_institucional_por_nome_ou_ticker_ou_id(
            fundo.id
        )
        if detalhes_publicacao:
            fundo.fundo_site_institucional = detalhes_publicacao
        return fundo

    async def fundo_categorias_documentos(self):
        return await self.fundos_repository.fundo_categorias_documentos()

    async def fundo_caracteristicas_extras(self):
        return await self.fundos_repository.fundo_caracteristicas_extras()

    @dataclass
    class DocumentoReturnType:
        arquivo: Arquivo
        conteudo: bytes

    async def fundo_documento(self, id: int, acesso_privado: bool = False):
        documento = await self.fundos_repository.fundo_documento(id)
        # Documento inexistente
        if documento == None:
            return None
        publicacao = documento.fundo.fundo_site_institucional
        # Fundo não foi publicado no site e o usuário não tem acesso interno
        if publicacao == None and not acesso_privado:
            return None
        ids_listados_publicamente = {
            relacionamento.fundos_documento_id
            for relacionamento in (publicacao.fundos_documentos if publicacao else [])
        }
        # Fundo foi publicado no site mas o documento não está listado como público
        if id not in ids_listados_publicamente:
            return None
        conteudo = await self.arquivos_repository.decodificar(documento.arquivo)
        return self.DocumentoReturnType(arquivo=documento.arquivo, conteudo=conteudo)

    async def get_fundos_cotas_rentabilidades(
        self, data_referencia: date | None, fundos_ids: list[int]
    ):
        if data_referencia is None:
            data_referencia = date.today()

        cotas_rentabilidades = (
            await self.fundos_repository.lista_cotas_rentabilidades_by_data_referencia(
                data_referencia=data_referencia, fundos_ids=fundos_ids
            )
        )
        return cotas_rentabilidades

    async def inserir_fundo_cotas_rentabilidades(
        self, arquivo_rentabilidades: UploadFile, *, persist=False
    ) -> dict | list[FundosRepository.InserirFundoCotaRentabilidade]:
        fundos_ids_cnpjs = await self.fundos_repository.lista_fundos_ids_cnpjs()
        dataframe = RentabilidadesService.get_dataframe(
            arquivo_rentabilidades=arquivo_rentabilidades.file,
            nome_sheet="Cota",
            skip_rows=7,
        )
        fundos_cotas_rentabilidades = []
        fundos_ids_cotas_rentabilidades_inseridos: list[int] = []
        fundos_ids_cotas_rentabilidades_nao_inseridos: list[int] = []
        for id_cnpj in fundos_ids_cnpjs:
            try:
                fundo_cota_rentabilidade = self._get_fundo_cota_rentabilidade(
                    tuple(id_cnpj), dataframe
                )

                fundos_cotas_rentabilidades.append(fundo_cota_rentabilidade)
                fundos_ids_cotas_rentabilidades_inseridos.append(id_cnpj[0])
            except Exception as e:
                if isinstance(e, KeyError):
                    logging.warn(
                        f"Fundo {id_cnpj[0]} não encontrado na sheet de cotas do arquivo enviado",
                        exc_info=True,
                    )
                else:
                    logging.error(
                        f"Houve um problema ao calcular as rentabilidades da cota do fundo {id_cnpj[0]}",
                        exc_info=True,
                    )

                fundos_ids_cotas_rentabilidades_nao_inseridos.append(id_cnpj[0])
                continue

        if not persist:
            return fundos_cotas_rentabilidades

        await self.fundos_repository.inserir_cotas_rentabilidades(
            fundos_cotas_rentabilidades
        )
        return {
            "fundos_ids_cotas_rentabilidades_inseridos": fundos_ids_cotas_rentabilidades_inseridos,
            "fundos_ids_cotas_rentabilidades_nao_inseridos": fundos_ids_cotas_rentabilidades_nao_inseridos,
        }

    async def get_patrimonio_liquido_rentabilidades(
        self, data_referencia: date | None, fundos_ids: list[int]
    ):
        if data_referencia is None:
            data_referencia = date.today()

        patrimonio_liquido_rentabilidades = await self.fundos_repository.lista_patrimonio_liquido_rentabilidades_by_data_referencia(
            data_referencia=data_referencia, fundos_ids=fundos_ids
        )
        return patrimonio_liquido_rentabilidades

    async def inserir_fundo_patrimonio_liquido_rentabilidades(
        self, arquivo_rentabilidades: UploadFile, *, persist=False
    ) -> dict | list[dict]:
        fundos_ids_cnpjs = await self.fundos_repository.lista_fundos_ids_cnpjs()
        dataframe = RentabilidadesService.get_dataframe(
            arquivo_rentabilidades=arquivo_rentabilidades.file,
            nome_sheet="PL",
            skip_rows=7,
        )

        fundos_patrimonio_liquido_rentabilidades = []
        fundos_ids_patrimonio_liquido_rentabilidades_inseridos: list[int] = []
        fundos_ids_patrimonio_liquido_rentabilidades_nao_inseridos: list[int] = []

        for id_cnpj in fundos_ids_cnpjs:
            try:
                medias_pl = self._get_fundo_patrimonio_liquido_rentabilidade(
                    tuple(id_cnpj), dataframe
                )

                fundos_patrimonio_liquido_rentabilidades.append(medias_pl)
                fundos_ids_patrimonio_liquido_rentabilidades_inseridos.append(
                    id_cnpj[0]
                )
            except Exception as e:
                if isinstance(e, KeyError):
                    logging.warn(
                        f"Fundo {id_cnpj[0]} não encontrado na sheet de PL do arquivo enviado",
                        exc_info=True,
                    )
                else:
                    logging.error(
                        f"Houve um problema ao calcular as médias do PL do fundo {id_cnpj[0]}",
                        exc_info=True,
                    )

                fundos_ids_patrimonio_liquido_rentabilidades_nao_inseridos.append(
                    id_cnpj[0]
                )
                continue

        if not persist:
            return fundos_patrimonio_liquido_rentabilidades

        await self.fundos_repository.inserir_patrimonio_liquido_rentabilidades(
            fundos_patrimonio_liquido_rentabilidades
        )
        return {
            "fundos_ids_patrimonio_liquido_rentabilidades_inseridos": fundos_ids_patrimonio_liquido_rentabilidades_inseridos,
            "fundos_ids_patrimonio_liquido_rentabilidades_nao_inseridos": fundos_ids_patrimonio_liquido_rentabilidades_nao_inseridos,
        }

    def _get_fundo_cota_rentabilidade(
        self,
        id_cnpj_fundo: tuple[int, str],
        dataframe: pd.DataFrame,
    ) -> FundosRepository.InserirFundoCotaRentabilidade:
        df = dataframe

        id_fundo = id_cnpj_fundo[0]
        cnpj_fundo = id_cnpj_fundo[1]

        QTD_DIAS_CORRIDOS = 365
        data_ultima_posicao: date = df[cnpj_fundo].last_valid_index()  # type: ignore

        data_rentabilidade_dia = CalculosService.get_data_d_util_menos_x_dias(
            x_dias=1, data_input=data_ultima_posicao, feriados=feriados
        )

        data_rentabilidade_mes = CalculosService.get_ultimo_dia_util_mes_anterior(
            data_input=data_ultima_posicao,
        )

        data_rentabilidade_ano = CalculosService.get_ultimo_dia_util_ano_anterior(
            data_input=data_ultima_posicao,
        )

        data_rentabilidade_12m = CalculosService.get_data_d_util_menos_x_dias(
            x_dias=QTD_DIAS_CORRIDOS,
            data_input=data_ultima_posicao,
            feriados=feriados,
            roll="forward",
        )

        data_rentabilidade_24m = CalculosService.get_data_d_util_menos_x_dias(
            x_dias=QTD_DIAS_CORRIDOS * 2,
            data_input=data_ultima_posicao,
            feriados=feriados,
            roll="forward",
        )

        data_rentabilidade_36m = CalculosService.get_data_d_util_menos_x_dias(
            x_dias=QTD_DIAS_CORRIDOS * 3,
            data_input=data_ultima_posicao,
            feriados=feriados,
            roll="forward",
        )

        ultima_cota = (
            None
            if math.isnan(df.loc[data_ultima_posicao, cnpj_fundo]) == True  # type: ignore
            else df.loc[data_ultima_posicao, cnpj_fundo]  # type: ignore
        )

        rentabilidade_cota_dia = (
            ultima_cota / df.loc[data_rentabilidade_dia, cnpj_fundo]  # type: ignore
        )
        rentabilidade_cota_mes = (
            ultima_cota / df.loc[data_rentabilidade_mes, cnpj_fundo]  # type: ignore
        )
        rentabilidade_cota_ano = (
            ultima_cota / df.loc[data_rentabilidade_ano, cnpj_fundo]  # type: ignore
        )
        rentabilidade_cota_12m = (
            ultima_cota / df.loc[data_rentabilidade_12m, cnpj_fundo]  # type: ignore
        )
        rentabilidade_cota_24m = (
            ultima_cota / df.loc[data_rentabilidade_24m, cnpj_fundo]  # type: ignore
        )
        rentabilidade_cota_36m = (
            ultima_cota / df.loc[data_rentabilidade_36m, cnpj_fundo]  # type: ignore
        )

        rentabilidade_cota_dia = (
            None
            if math.isnan(rentabilidade_cota_dia) == True
            else rentabilidade_cota_dia
        )
        rentabilidade_cota_mes = (
            None
            if math.isnan(rentabilidade_cota_mes) == True
            else rentabilidade_cota_mes
        )
        rentabilidade_cota_ano = (
            None
            if math.isnan(rentabilidade_cota_ano) == True
            else rentabilidade_cota_ano
        )
        rentabilidade_cota_12m = (
            None
            if math.isnan(rentabilidade_cota_12m) == True
            else rentabilidade_cota_12m
        )
        rentabilidade_cota_24m = (
            None
            if math.isnan(rentabilidade_cota_24m) == True
            else rentabilidade_cota_24m
        )
        rentabilidade_cota_36m = (
            None
            if math.isnan(rentabilidade_cota_36m) == True
            else rentabilidade_cota_36m
        )

        fundo_cota_rentabilidade: FundosRepository.InserirFundoCotaRentabilidade = {
            "fundo_id": id_fundo,
            "data_posicao": data_ultima_posicao,
            "preco_cota": ultima_cota,
            "rentabilidade_dia": rentabilidade_cota_dia,
            "rentabilidade_mes": rentabilidade_cota_mes,
            "rentabilidade_ano": rentabilidade_cota_ano,
            "rentabilidade_12meses": rentabilidade_cota_12m,
            "rentabilidade_24meses": rentabilidade_cota_24m,
            "rentabilidade_36meses": rentabilidade_cota_36m,
        }

        return fundo_cota_rentabilidade

    def _get_fundo_patrimonio_liquido_rentabilidade(
        self,
        id_cnpj_fundo: tuple[int, str],
        dataframe: pd.DataFrame,
    ) -> FundosRepository.InserirFundoPatrimonioLiquidoRentabilidade:
        df = dataframe

        id_fundo = id_cnpj_fundo[0]
        cnpj_fundo = id_cnpj_fundo[1]

        df[cnpj_fundo] = pd.to_numeric(df[cnpj_fundo], errors="coerce")

        QTD_DIAS_CORRIDOS = 365
        data_ultima_posicao: date = df[cnpj_fundo].last_valid_index()  # type: ignore

        data_media_12m = CalculosService.get_data_d_util_menos_x_dias(
            x_dias=QTD_DIAS_CORRIDOS,
            data_input=data_ultima_posicao,
            feriados=feriados,
            roll="forward",
        )

        data_media_24m = CalculosService.get_data_d_util_menos_x_dias(
            x_dias=QTD_DIAS_CORRIDOS * 2,
            data_input=data_ultima_posicao,
            feriados=feriados,
            roll="forward",
        )

        data_media_36m = CalculosService.get_data_d_util_menos_x_dias(
            x_dias=QTD_DIAS_CORRIDOS * 3,
            data_input=data_ultima_posicao,
            feriados=feriados,
            roll="forward",
        )

        df_periodo_12m = df.loc[data_media_12m:data_ultima_posicao, cnpj_fundo]
        df_periodo_24m = df.loc[data_media_24m:data_ultima_posicao, cnpj_fundo]
        df_periodo_36m = df.loc[data_media_36m:data_ultima_posicao, cnpj_fundo]

        pl_12m_atras = df.loc[data_media_12m, cnpj_fundo]  # type: ignore
        pl_24m_atras = df.loc[data_media_24m, cnpj_fundo]  # type: ignore
        pl_36m_atras = df.loc[data_media_36m, cnpj_fundo]  # type: ignore

        pl_atual = (
            None
            if math.isnan(df.loc[data_ultima_posicao, cnpj_fundo]) == True  # type: ignore
            else df.loc[data_ultima_posicao, cnpj_fundo]  # type: ignore
        )
        pl_medio_12m = (
            None if math.isnan(pl_12m_atras) == True else df_periodo_12m.mean()
        )
        pl_medio_24m = (
            None if math.isnan(pl_24m_atras) == True else df_periodo_24m.mean()
        )
        pl_medio_36m = (
            None if math.isnan(pl_36m_atras) == True else df_periodo_36m.mean()
        )

        fundo_patrimonio_liquido_rentabilidade: (
            FundosRepository.InserirFundoPatrimonioLiquidoRentabilidade
        ) = {
            "fundo_id": id_fundo,
            "data_posicao": data_ultima_posicao,
            "patrimonio_liquido": pl_atual,
            "media_12meses": pl_medio_12m,
            "media_24meses": pl_medio_24m,
            "media_36meses": pl_medio_36m,
        }

        return fundo_patrimonio_liquido_rentabilidade

    async def publica_fundo_site_institucional(
        self,
        fundo_id: int,
        detalhes_fundo: PostDetalhesFundoSiteInstitucionalSchema,
        caracteristicas_extras_ids: list[int] | None,
        documentos_ids: list[int] | None,
        indices_benchmark: list[IndiceBenchmarkSchema] | None,
        distribuidores_ids: list[int] | None,
    ):
        async with self.fundos_repository.db.begin_nested():
            fundo_cnpj = await self.fundos_repository.lista_fundo_cnpj_por_id(fundo_id)
            site_institucional_fundo_id = (
                await self.fundos_repository.insere_site_institucional_fundo(
                    fundo_id=fundo_id,
                    fundo_cnpj=fundo_cnpj,
                    detalhes=detalhes_fundo,
                )
            )

            if caracteristicas_extras_ids:
                await self.fundos_repository.insere_site_institucional_fundo_caracteristicas_extras(
                    site_institucional_fundo_id=site_institucional_fundo_id,
                    caracteristicas_extras_ids=caracteristicas_extras_ids,
                )

            if documentos_ids:
                await self.fundos_repository.insere_site_institucional_fundo_documentos(
                    site_institucional_fundo_id=site_institucional_fundo_id,
                    fundos_documento_ids=documentos_ids,
                )

            if indices_benchmark:
                await self.fundos_repository.insere_site_institucional_fundo_indices_benchmark(
                    site_institucional_fundo_id=site_institucional_fundo_id,
                    indices=indices_benchmark,
                )

            if distribuidores_ids:
                await self.fundos_repository.insere_site_institucional_fundo_distribuidores(
                    site_institucional_fundo_id=site_institucional_fundo_id,
                    distribuidores_ids=distribuidores_ids,
                )

        return site_institucional_fundo_id

    async def edita_fundo_site_institucional(
        self,
        site_institucional_fundo_id: int,
        detalhes_fundo: PatchDetalhesFundoSiteInstitucionalSchema | None,
        caracteristicas_extras_para_publicacao_ids: list[int] | None,
        caracteristicas_extras_para_despublicacao_ids: list[int] | None,
        documentos_para_publicacao_ids: list[int] | None,
        documentos_para_despublicacao_ids: list[int] | None,
        indices_benchmark_para_publicacao: list[IndiceBenchmarkSchema] | None,
        indices_benchmark_para_despublicacao: list[IndiceBenchmarkSchema] | None,
        distribuidores_para_publicacao_ids: list[int] | None,
        distribuidores_para_despublicacao_ids: list[int] | None,
    ):
        async with self.fundos_repository.db.begin_nested():
            if documentos_para_despublicacao_ids:
                await self.fundos_repository.deleta_site_institucional_fundos_documentos(
                    site_institucional_fundo_id,
                    documentos_para_despublicacao_ids,
                )
            if documentos_para_publicacao_ids:
                await self.fundos_repository.insere_site_institucional_fundo_documentos(
                    site_institucional_fundo_id, documentos_para_publicacao_ids
                )

            if caracteristicas_extras_para_despublicacao_ids:
                await self.fundos_repository.deleta_site_institucional_fundo_caracteristicas_extras(
                    site_institucional_fundo_id,
                    caracteristicas_extras_para_despublicacao_ids,
                )
            if caracteristicas_extras_para_publicacao_ids:
                await self.fundos_repository.insere_site_institucional_fundo_caracteristicas_extras(
                    site_institucional_fundo_id,
                    caracteristicas_extras_para_publicacao_ids,
                )

            if indices_benchmark_para_despublicacao:
                await self.fundos_repository.deleta_site_institucional_fundo_indices_benchmark(
                    site_institucional_fundo_id,
                    [
                        indice_benchmark.indice_benchmark_id
                        for indice_benchmark in indices_benchmark_para_despublicacao
                    ],
                )
            if indices_benchmark_para_publicacao:
                await self.fundos_repository.insere_site_institucional_fundo_indices_benchmark(
                    site_institucional_fundo_id,
                    indices_benchmark_para_publicacao,
                )

            if distribuidores_para_despublicacao_ids:
                await self.fundos_repository.deleta_site_institucional_fundo_distribuidores(
                    site_institucional_fundo_id,
                    distribuidores_para_despublicacao_ids,
                )
            if distribuidores_para_publicacao_ids:
                await self.fundos_repository.insere_site_institucional_fundo_distribuidores(
                    site_institucional_fundo_id,
                    distribuidores_para_publicacao_ids,
                )

            if detalhes_fundo is not None:
                await self.fundos_repository.edita_site_institucional_fundo_por_id(
                    id=site_institucional_fundo_id,
                    detalhes=detalhes_fundo,
                )

    async def despublica_fundo_site_institucional(
        self, site_institucional_fundo_id: int
    ):
        async with self.fundos_repository.db.begin_nested():
            return await self.fundos_repository.deleta_site_institucional_fundo(
                site_institucional_fundo_id
            )

    async def publicacao_massa(
        self, dados: PublicacaoMateriaisMassaSchema, arquivos: list[UploadFile]
    ):
        async with self.fundos_repository.db.begin_nested():
            fundos = await self.fundos_repository.fundos(
                [info.fundo_id for info in dados.informacoes]
            )
            for fundo in fundos:
                if fundo.fundo_site_institucional:
                    detalhes = await self.fundos_repository.fundo_detalhes(fundo.id)
                    materiais = [
                        documento
                        for documento in detalhes.documentos
                        if documento.fundo_categoria_documento_id
                        == FundoCategoriaDocumento.MATERIAL_PUBLICITARIO
                    ]
                    await self.fundos_repository.deleta_site_institucional_fundos_documentos(
                        fundo.fundo_site_institucional.id,
                        [material.id for material in materiais],
                    )
                fundos_documentos: list[FundosRepository.InserirFundoDocumento] = []
                # Quais os arquivos desta request pertencem a este fundo?
                materiais_do_fundo = [
                    informacao
                    for informacao in dados.informacoes
                    if informacao.fundo_id == fundo.id
                ]
                for informacoes in materiais_do_fundo:
                    arquivo = arquivos[informacoes.posicao_arquivo]
                    id_arquivo = await self.arquivos_repository.criar(
                        arquivo.file, arquivo.filename, arquivo.content_type
                    )
                    fundos_documentos.append(
                        {
                            "fundo_id": informacoes.fundo_id,
                            "arquivo_id": id_arquivo,
                            "fundo_categoria_documento_id": FundoCategoriaDocumento.MATERIAL_PUBLICITARIO,
                            "titulo": informacoes.titulo_material,
                            "criado_em": datetime.now(),
                            "data_referencia": informacoes.data_referencia,
                        }
                    )
                ids_fundos_documentos = await self.fundos_repository.inserir_documentos(
                    fundos_documentos
                )
                if fundo.fundo_site_institucional:
                    await self.fundos_repository.publicacao_documentos(
                        fundo.fundo_site_institucional.id, ids_fundos_documentos
                    )
