from pydantic import BaseModel as Schema

from .model import CategoriaRelatorio, DocumentoRelatorio

from modules.arquivos.schema import ArquivoSchema, ArquivoSemIDSchema


class PlanoDeFundoSchema(Schema):
    id: int
    conteudo_b64: str


class CategoriaRelatorioSchema(Schema):
    id: int
    nome: str
    ordem: int
    plano_de_fundo_id: int | None = None
    plano_de_fundo: PlanoDeFundoSchema | None = None

    documentos: list["DocumentoRelatorioSchema"]

    @staticmethod
    def from_model(model: CategoriaRelatorio):
        pf = model.plano_de_fundo
        return CategoriaRelatorioSchema(
            id=model.id,
            nome=model.nome,
            ordem=model.ordem,
            plano_de_fundo_id=model.plano_de_fundo_id,
            plano_de_fundo=(
                PlanoDeFundoSchema(id=pf.id, conteudo_b64=pf.conteudo_b64)
                if pf
                else None
            ),
            documentos=[
                DocumentoRelatorioSchema.from_model(documento)
                for documento in model.documentos
            ],
        )


class DocumentoRelatorioSchema(Schema):
    id: int
    nome: str
    categoria_id: int

    arquivo: ArquivoSemIDSchema

    @staticmethod
    def from_model(model: DocumentoRelatorio):
        return DocumentoRelatorioSchema(
            id=model.id,
            nome=model.nome,
            categoria_id=model.categoria_id,
            arquivo=ArquivoSemIDSchema.from_model(model.arquivo),
        )


class MetadadosDocumentosRegulatoriosSchema(Schema):
    posicao_arquivo: int
    nome: str


class EnvioDocumentosRegulatoriosSchema(Schema):
    dados: list[MetadadosDocumentosRegulatoriosSchema]


class CriacaoCategoriaRelatoriosSchema(Schema):
    nome: str


class ReordenarCategoriasSchema(Schema):
    id: int
    ordem: int
