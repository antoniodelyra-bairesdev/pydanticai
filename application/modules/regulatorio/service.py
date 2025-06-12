from dataclasses import dataclass
from http import HTTPStatus

from fastapi import UploadFile
from fastapi.exceptions import HTTPException

from .repository import RegulatorioRepository
from .schema import (
    CategoriaRelatorioSchema,
    DocumentoRelatorioSchema,
    MetadadosDocumentosRegulatoriosSchema,
    ArquivoSemIDSchema,
    PlanoDeFundoSchema,
    ReordenarCategoriasSchema,
)

from modules.arquivos.repository import ArquivosRepository, Arquivo


@dataclass
class RegulatorioService:
    regulatorio_repository: RegulatorioRepository
    arquivos_repository: ArquivosRepository

    async def buscar_planos_de_fundo(self):
        pfs = await self.regulatorio_repository.buscar_planos_de_fundo()
        return [
            PlanoDeFundoSchema(id=pf.id, conteudo_b64=pf.conteudo_b64) for pf in pfs
        ]

    async def atribuir_plano_de_fundo_a_categoria(
        self, *, categoria_id: int, plano_de_fundo_id: int | None
    ):
        await self.regulatorio_repository.atribuir_plano_de_fundo_a_categoria(
            categoria_id=categoria_id, plano_de_fundo_id=plano_de_fundo_id
        )

    async def categorias_e_documentos(self):
        categorias = await self.regulatorio_repository.categorias_e_documentos()
        return [
            CategoriaRelatorioSchema.from_model(categoria) for categoria in categorias
        ]

    async def criar_categoria(self, nome: str):
        id, ordem = await self.regulatorio_repository.criar_categoria(nome)
        return CategoriaRelatorioSchema(id=id, nome=nome, ordem=ordem, documentos=[])

    async def reordenar_categorias(self, categorias: list[ReordenarCategoriasSchema]):
        await self.regulatorio_repository.reordenar_categorias(categorias)

    async def remover_categoria(self, categoria_id: int):
        async with self.regulatorio_repository.db.begin_nested():
            categorias = await self.regulatorio_repository.categorias_e_documentos(
                [categoria_id]
            )
            if len(categorias) != 1:
                raise HTTPException(HTTPStatus.NOT_FOUND, "Categoria não encontrada")
            categoria = categorias[0]
            await self.regulatorio_repository.apagar_categoria(categoria_id)
            for documento in categoria.documentos:
                await self.arquivos_repository.apagar(documento.arquivo_id)

    async def remover_documentacao(self, documento_id: int):
        async with self.regulatorio_repository.db.begin_nested():
            documento = await self.regulatorio_repository.documento(documento_id)
            if documento == None:
                raise HTTPException(HTTPStatus.NOT_FOUND, "Documento não encontrado")
            await self.regulatorio_repository.apagar_documento(documento_id)
            await self.arquivos_repository.apagar(documento.arquivo_id)

    async def adicionar_documentacao(
        self,
        categoria_id: int,
        arquivos: list[UploadFile],
        metadados: list[MetadadosDocumentosRegulatoriosSchema],
    ):
        if len(arquivos) != len(metadados):
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                "Quantidade de metadados de documentos diferente de quantidade de arquivos.",
            )
        async with self.regulatorio_repository.db.begin_nested():
            descricoes: list[RegulatorioRepository.DescricaoArquivo] = []
            for i, informacoes in enumerate(metadados):
                arquivo = arquivos[informacoes.posicao_arquivo]
                id_arquivo = await self.arquivos_repository.criar(
                    arquivo.file, arquivo.filename, arquivo.content_type
                )
                descricoes.append({"arquivo_id": id_arquivo, "nome": metadados[i].nome})

            ids_documentos_criados = (
                await self.regulatorio_repository.adicionar_documentos(
                    categoria_id, descricoes
                )
            )
            novos_documentos: list[DocumentoRelatorioSchema] = []
            for i, id_documento in enumerate(ids_documentos_criados):
                novos_documentos.append(
                    DocumentoRelatorioSchema(
                        id=id_documento,
                        nome=descricoes[i]["nome"],
                        categoria_id=categoria_id,
                        arquivo=ArquivoSemIDSchema(
                            nome=arquivos[i].filename or "unknown",
                            extensao=arquivos[i].content_type
                            or "application/octet-stream",
                        ),
                    )
                )
            return novos_documentos

    @dataclass
    class DocumentoReturnType:
        arquivo: Arquivo
        conteudo: bytes

    async def baixar_relatorio(self, documento_id: int) -> DocumentoReturnType | None:
        documento = await self.regulatorio_repository.documento(documento_id)
        if not documento:
            return None
        arquivo = documento.arquivo
        conteudo = await self.arquivos_repository.decodificar(arquivo)
        return self.DocumentoReturnType(arquivo=arquivo, conteudo=conteudo)
