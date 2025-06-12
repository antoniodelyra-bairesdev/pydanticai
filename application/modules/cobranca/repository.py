from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict
from sqlalchemy import bindparam, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from .schema import CriacaoDadosExecucaoDaycovalSchema, PassoExecucaoDaycovalSchema
from .model import DadosExecucaoDaycoval, ExecucaoDaycoval, Inquilino, PassoExecucaoDaycoval, TipoExecucaoDaycoval, ContratoLocacao

@dataclass
class CobrancaRepository:
    db: AsyncSession

    async def inquilinos_fundo(self, fundo_id: int):
        resultado = await self.db.execute(
            select(Inquilino)
            .outerjoin(Inquilino.contratos)
            .outerjoin(ContratoLocacao.faixas_cobranca_multa_mora)
            .options(
                contains_eager(Inquilino.contratos).contains_eager(
                    ContratoLocacao.faixas_cobranca_multa_mora
                )
            )
            .where(ContratoLocacao.fundo_id == fundo_id)
        )
        return resultado.unique().scalars().all()

    async def boletos(self, ids_boletos: list[int] | None = None):
        query = (
            select(DadosExecucaoDaycoval)
            .outerjoin(DadosExecucaoDaycoval.contrato)
            .outerjoin(DadosExecucaoDaycoval.execucao)
            .outerjoin(ExecucaoDaycoval.usuario)
            .options(
                contains_eager(DadosExecucaoDaycoval.contrato),
                contains_eager(DadosExecucaoDaycoval.execucao).contains_eager(
                    ExecucaoDaycoval.usuario
                ),
            )
        )
        if ids_boletos:
            query = query.where(DadosExecucaoDaycoval.id.in_(ids_boletos))
        result = await self.db.execute(query)
        return result.unique().scalars().all()
    
    async def execucoes_daycoval(self, ids_execucoes: list[int] | None = None):
        query = (
            select(ExecucaoDaycoval)
            .outerjoin(ExecucaoDaycoval.tipo_execucao)
            .outerjoin(ExecucaoDaycoval.passos)
            .outerjoin(ExecucaoDaycoval.dados)
            .outerjoin(ExecucaoDaycoval.usuario)
            .options(
                contains_eager(ExecucaoDaycoval.tipo_execucao),
                contains_eager(ExecucaoDaycoval.passos),
                contains_eager(ExecucaoDaycoval.dados),
                contains_eager(ExecucaoDaycoval.usuario)
            )
        )
        if ids_execucoes:
            query = query.where(ExecucaoDaycoval.id.in_(ids_execucoes))
        result = await self.db.execute(query)
        return result.unique().scalars().all()

    async def criar_execucao_daycoval(
        self,
        dados: list[CriacaoDadosExecucaoDaycovalSchema],
        tipo_execucao_id: int,
        usuario_id: int,
        agora: datetime | None = None
    ):
        if agora == None:
            agora = datetime.now()
            
        async with self.db.begin_nested():
            resultado = await self.db.execute(
                insert(ExecucaoDaycoval).values({
                    ExecucaoDaycoval.inicio.name: agora,
                    ExecucaoDaycoval.tipo_execucao_id.name: tipo_execucao_id,
                    ExecucaoDaycoval.usuario_id.name: usuario_id
                }).returning(ExecucaoDaycoval.id)
            )
            id_execucao = resultado.scalar_one()
            
            ids_dados_execucao: list[int] = []
            if dados:
                resultados = await self.db.execute(
                    insert(DadosExecucaoDaycoval).values([
                        {
                            DadosExecucaoDaycoval.execucao_daycoval_id.name: id_execucao,
                            DadosExecucaoDaycoval.identificador_titulo.name: dado.identificador_titulo,
                            DadosExecucaoDaycoval.identificador_documento_cobranca.name: dado.identificador_documento_cobranca,
                            DadosExecucaoDaycoval.vencimento.name: dado.vencimento,
                            DadosExecucaoDaycoval.valor.name: dado.valor,
                            DadosExecucaoDaycoval.percentual_juros_mora_ao_mes.name: dado.percentual_juros_mora_ao_mes,
                            DadosExecucaoDaycoval.percentual_sobre_valor_multa_mora.name: dado.percentual_sobre_valor_multa_mora,
                            DadosExecucaoDaycoval.contrato_id.name: dado.contrato_id
                        }
                        for dado in dados
                    ]).returning(DadosExecucaoDaycoval.id)
                )
                ids_dados_execucao = [*resultados.scalars().all()]

        @dataclass
        class ResultadoCriacaoExecucao:
            id_execucao: int
            ids_dados_execucao: list[int]
            
        return ResultadoCriacaoExecucao(
            id_execucao=id_execucao,
            ids_dados_execucao=[*ids_dados_execucao]
        )
    
    async def buscar_tipo_execucao(self, tipo_execucao_id: int):
        result = await self.db.execute(
            select(TipoExecucaoDaycoval).where(TipoExecucaoDaycoval.id == tipo_execucao_id)
        )
        return result.scalar_one()
    
    async def finalizar_execucoes_daycoval(
        self,
        execucoes_ids: list[int] | None = None,
        fim: datetime | None = None,
        erro: str | None = None
    ):
        if fim == None:
            fim = datetime.now()
        query = update(ExecucaoDaycoval)
        if execucoes_ids == None:
            query = query.where(ExecucaoDaycoval.fim == None)
        else:
            query = query.where(ExecucaoDaycoval.id.in_(execucoes_ids))
        await self.db.execute(
            query
            .values({
                ExecucaoDaycoval.fim.name: fim,
                ExecucaoDaycoval.erro.name: erro
            })
        )
    
    async def contratos(self, contratos_ids: list[int]):
        result = await self.db.execute(
            select(ContratoLocacao)
            .outerjoin(ContratoLocacao.inquilino)
            .outerjoin(ContratoLocacao.faixas_cobranca_multa_mora)
            .options(
                contains_eager(ContratoLocacao.inquilino),
                contains_eager(ContratoLocacao.faixas_cobranca_multa_mora),
            )
            .where(ContratoLocacao.id.in_(contratos_ids))
        )
        return result.unique().scalars().all()
    
    async def criar_passo_execucao_daycoval(
        self,
        execucao_id: int,
        nome: str,
        inicio: datetime | None = None
    ):
        if inicio == None:
            inicio = datetime.now()
        result = await self.db.execute(
            insert(PassoExecucaoDaycoval)
            .values({
                PassoExecucaoDaycoval.execucao_daycoval_id.name: execucao_id,
                PassoExecucaoDaycoval.nome.name: nome,
                PassoExecucaoDaycoval.inicio.name: inicio,
                PassoExecucaoDaycoval.fim.name: None,
                PassoExecucaoDaycoval.erro.name: None,
            })
            .returning(PassoExecucaoDaycoval.id)
        )
        id = result.scalar_one()
        return PassoExecucaoDaycovalSchema(
            id=id,
            execucao_daycoval_id=execucao_id,
            nome=nome,
            inicio=inicio
        )
    
    async def reiniciar_execucao_daycoval(
        self,
        execucao_id: int,
        inicio: datetime | None = None
    ):
        if inicio == None:
            inicio = datetime.now()
        async with self.db.begin_nested():
            await self.db.execute(
                delete(PassoExecucaoDaycoval)
                .where(PassoExecucaoDaycoval.execucao_daycoval_id == execucao_id)
            )
            await self.db.execute(
                update(ExecucaoDaycoval)
                .where(ExecucaoDaycoval.id == execucao_id)
                .values({
                    ExecucaoDaycoval.inicio.name: inicio,
                    ExecucaoDaycoval.fim.name: None,
                    ExecucaoDaycoval.erro.name: None
                })
            )

    async def reiniciar_passo_execucao_daycoval(
        self,
        passo_id: int,
        inicio: datetime | None = None
    ):
        if inicio == None:
            inicio = datetime.now()
        await self.db.execute(
            update(PassoExecucaoDaycoval)
            .where(PassoExecucaoDaycoval.id == passo_id)
            .values({
                PassoExecucaoDaycoval.inicio.name: inicio,
                PassoExecucaoDaycoval.fim.name: None,
                PassoExecucaoDaycoval.erro.name: None,
            })
        )
    
    async def finalizar_passos_execucao_daycoval(
        self,
        passos_execucao_ids: list[int] | None = None,
        fim: datetime | None = None,
        erro: str | None = None
    ):
        if fim == None:
            fim = datetime.now()
        query = update(PassoExecucaoDaycoval)
        if passos_execucao_ids == None:
            query = query.where(PassoExecucaoDaycoval.fim == None)
        else:
            query = query.where(PassoExecucaoDaycoval.id.in_(passos_execucao_ids))
        await self.db.execute(
            query
            .values({
                PassoExecucaoDaycoval.fim.name: fim,
                PassoExecucaoDaycoval.erro.name: erro
            })
        )

    async def salvar_informacoes_remessa(self, dado_execucao_id_conteudo_remessa: dict[int, str]):
        await self.db.execute(
            update(DadosExecucaoDaycoval),
            [
                {
                    DadosExecucaoDaycoval.id.name: id,
                    DadosExecucaoDaycoval.conteudo_arquivo_remessa.name: conteudo_remessa
                }
                for id, conteudo_remessa in dado_execucao_id_conteudo_remessa.items()
            ]
        )

    async def salvar_informacoes_boleto_parcial(self, dado_execucao_id: int, arquivo_id: str):
        await self.db.execute(
            update(DadosExecucaoDaycoval)
            .where(DadosExecucaoDaycoval.id == dado_execucao_id)
            .values({
                DadosExecucaoDaycoval.arquivo_id_boleto_parcial_pdf.name: arquivo_id
            })
        )

    class _InfosArquivoRetorno(TypedDict):
        nome_arquivo: str
        conteudo: str

    async def salvar_informacoes_retorno(self, dado_execucao_id_conteudo_retorno: dict[int, _InfosArquivoRetorno]):
        await self.db.execute(
            update(DadosExecucaoDaycoval),
            [
                {
                    DadosExecucaoDaycoval.id.name: id,
                    DadosExecucaoDaycoval.conteudo_arquivo_retorno.name: dados['conteudo'],
                    DadosExecucaoDaycoval.nome_arquivo_retorno.name: dados['nome_arquivo']
                }
                for id, dados in dado_execucao_id_conteudo_retorno.items()
            ]
        )

    async def salvar_informacoes_boleto_completo(self, dado_execucao_id: int, arquivo_id: str):
        await self.db.execute(
            update(DadosExecucaoDaycoval)
            .where(DadosExecucaoDaycoval.id == dado_execucao_id)
            .values({
                DadosExecucaoDaycoval.arquivo_id_boleto_completo_pdf.name: arquivo_id
            })
        )

    async def salvar_nome_arquivo_remessa(self, dado_execucao_id: int, nome_arquivo_remessa: str):
        await self.db.execute(
            update(DadosExecucaoDaycoval)
            .where(DadosExecucaoDaycoval.id == dado_execucao_id)
            .values({
                DadosExecucaoDaycoval.nome_arquivo_remessa.name: nome_arquivo_remessa
            })
        )