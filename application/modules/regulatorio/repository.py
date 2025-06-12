from dataclasses import dataclass
from typing import TypedDict
from sqlalchemy import delete, func, insert, select, case, update
from sqlalchemy.orm import contains_eager
from sqlalchemy.ext.asyncio import AsyncSession

from .model import CategoriaRelatorio, DocumentoRelatorio, PlanoDeFundo
from .schema import ReordenarCategoriasSchema


@dataclass
class RegulatorioRepository:
    db: AsyncSession

    async def buscar_planos_de_fundo(self):
        results = await self.db.execute(select(PlanoDeFundo))
        return results.scalars().all()

    async def atribuir_plano_de_fundo_a_categoria(
        self, *, categoria_id: int, plano_de_fundo_id: int | None
    ):
        await self.db.execute(
            update(CategoriaRelatorio),
            [{"id": categoria_id, "plano_de_fundo_id": plano_de_fundo_id}],
        )

    async def criar_categoria(self, nome: str):
        results = await self.db.execute(
            insert(CategoriaRelatorio)
            .values(
                {
                    "nome": nome,
                    "ordem": select(
                        case(
                            (
                                func.max(CategoriaRelatorio.ordem) != None,
                                func.max(CategoriaRelatorio.ordem) + 1,
                            ),
                            else_=1,
                        )
                    ).scalar_subquery(),
                }
            )
            .returning(CategoriaRelatorio.id, CategoriaRelatorio.ordem)
        )
        dados = results.tuples().one()
        return dados

    async def reordenar_categorias(self, categorias: list[ReordenarCategoriasSchema]):
        async with self.db.begin_nested():
            for _ in range(2):
                for categoria in categorias:
                    categoria.ordem *= -1
                await self.db.execute(
                    update(CategoriaRelatorio),
                    [categoria.model_dump() for categoria in categorias],
                )

    async def categorias_e_documentos(self, ids: list[int] = []):
        query = (
            select(CategoriaRelatorio)
            .outerjoin(CategoriaRelatorio.plano_de_fundo)
            .outerjoin(CategoriaRelatorio.documentos)
            .outerjoin(DocumentoRelatorio.arquivo)
            .options(
                contains_eager(CategoriaRelatorio.plano_de_fundo),
                contains_eager(CategoriaRelatorio.documentos),
                contains_eager(
                    CategoriaRelatorio.documentos, DocumentoRelatorio.arquivo
                ),
            )
        )
        if len(ids) > 0:
            query = query.where(CategoriaRelatorio.id.in_(ids))

        results = await self.db.execute(query)
        return results.unique().scalars().all()

    async def documento(self, id: int):
        results = await self.db.execute(
            select(DocumentoRelatorio)
            .join(DocumentoRelatorio.arquivo)
            .options(contains_eager(DocumentoRelatorio.arquivo))
            .where(DocumentoRelatorio.id == id)
        )
        return results.scalars().one_or_none()

    async def apagar_documento(self, id: int):
        await self.db.execute(
            delete(DocumentoRelatorio).where(DocumentoRelatorio.id == id)
        )

    async def apagar_categoria(self, id: int):
        await self.db.execute(
            delete(CategoriaRelatorio).where(CategoriaRelatorio.id == id)
        )

    class DescricaoArquivo(TypedDict):
        nome: str
        arquivo_id: str

    async def adicionar_documentos(
        self, categoria_id: int, arquivos: list[DescricaoArquivo]
    ):
        results = await self.db.execute(
            insert(DocumentoRelatorio)
            .values(
                [
                    {
                        "nome": descricao["nome"],
                        "categoria_id": categoria_id,
                        "arquivo_id": descricao["arquivo_id"],
                    }
                    for descricao in arquivos
                ]
            )
            .returning(DocumentoRelatorio.id)
        )
        return results.scalars().all()
