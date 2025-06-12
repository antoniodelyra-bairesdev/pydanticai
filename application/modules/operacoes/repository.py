from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import logging
from typing import Any
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import insert, select, update
from sqlalchemy.orm import aliased, contains_eager

from modules.ativos.model import TipoAtivo
from modules.b3.model import (
    AlocacoesInternasCasamentos,
    B3RegistroNoMe,
    B3Voice,
    CasamentoAlocacaoB3Voice,
)

from .model import (
    AlocacaoAdministrador,
    AlocacaoInterna,
    B3Corretora,
    B3Mesa,
    B3Usuarios,
    Boleta,
    CancelamentoAlocacaoAdministrador,
    CancelamentoAlocacaoInterna,
    Corretora,
    LiquidacaoAlocacaoAdministrador,
    MercadoNegociado,
    Usuario,
    Fundo,
)
from .schema import IdentificadorCorretora, ResultadoBuscaBoleta


@dataclass
class CriarBoleta:
    tipo_ativo_id: int
    natureza_operacao_id: int
    mercado_negociado_id: int
    corretora_id: int
    data_negociacao: date
    data_liquidacao: date


@dataclass
class CriarAlocacao:
    codigo_ativo: str
    vanguarda_compra: bool
    preco_unitario: Decimal
    quantidade: Decimal
    alocado_em: datetime
    data_negociacao: date
    data_liquidacao: date
    aprovado_em: datetime | None
    fundo_id: int
    tipo_ativo_id: int
    boleta_id: int
    alocacao_usuario_id: int
    aprovacao_usuario_id: int | None
    alocacao_anterior_id: int | None
    corretora_id: int


@dataclass
class OperacoesRepository:
    db: AsyncSession

    async def buscar_corretoras(self, ids_corretoras: list[IdentificadorCorretora]):
        corretora_apelido = [
            ic.valor for ic in ids_corretoras if ic.tipo == "APELIDO_VANGUARDA"
        ]
        corretora_id_b3 = [
            ic.valor for ic in ids_corretoras if ic.tipo == "ID_INSTITUICAO"
        ]
        corretora_nome_b3 = [
            ic.valor for ic in ids_corretoras if ic.tipo == "NOME_INSTITUICAO"
        ]
        mesa_id_b3 = [ic.valor for ic in ids_corretoras if ic.tipo == "ID_DESK"]
        mesa_nome_b3 = [ic.valor for ic in ids_corretoras if ic.tipo == "NOME_DESK"]
        usuario_id_b3 = [ic.valor for ic in ids_corretoras if ic.tipo == "ID_USUARIO"]
        usuario_nome_b3 = [
            ic.valor for ic in ids_corretoras if ic.tipo == "NOME_USUARIO"
        ]

        results = await self.db.execute(
            select(Corretora)
            .outerjoin(Corretora.b3_corretora)
            .outerjoin(B3Corretora.b3_mesas)
            .outerjoin(B3Mesa.b3_usuarios)
            .options(
                contains_eager(Corretora.b3_corretora),
                contains_eager(Corretora.b3_corretora, B3Corretora.b3_mesas),
                contains_eager(
                    Corretora.b3_corretora, B3Corretora.b3_mesas, B3Mesa.b3_usuarios
                ),
            )
            .where(
                Corretora.nome.in_(corretora_apelido)
                | B3Corretora.id_b3.in_(corretora_id_b3)
                | B3Corretora.nome.in_(corretora_nome_b3)
                | B3Mesa.id_b3.in_(mesa_id_b3)
                | B3Mesa.nome.in_(mesa_nome_b3)
                | B3Usuarios.id_b3.in_(usuario_id_b3)
                | B3Usuarios.nome.in_(usuario_nome_b3)
            )
        )

        return results.unique().scalars().all()

    async def criar_boletas(self, boletas: list[CriarBoleta]):
        results = await self.db.execute(
            insert(Boleta)
            .values(
                [
                    {
                        Boleta.data_negociacao.name: boleta.data_negociacao,
                        Boleta.data_liquidacao.name: boleta.data_liquidacao,
                        Boleta.tipo_ativo_id.name: boleta.tipo_ativo_id,
                        Boleta.natureza_operacao_id.name: boleta.natureza_operacao_id,
                        Boleta.mercado_negociado_id.name: boleta.mercado_negociado_id,
                        Boleta.corretora_id.name: boleta.corretora_id,
                    }
                    for boleta in boletas
                ]
            )
            .returning(Boleta.id)
        )
        return results.scalars().all()

    async def criar_alocacoes(self, alocacoes: list[CriarAlocacao]):
        results = await self.db.execute(
            insert(AlocacaoInterna)
            .values(
                [
                    {
                        AlocacaoInterna.boleta_id.name: alocacao.boleta_id,
                        AlocacaoInterna.codigo_ativo.name: alocacao.codigo_ativo,
                        AlocacaoInterna.vanguarda_compra.name: alocacao.vanguarda_compra,
                        AlocacaoInterna.preco_unitario.name: alocacao.preco_unitario,
                        AlocacaoInterna.quantidade.name: alocacao.quantidade,
                        AlocacaoInterna.data_negociacao.name: alocacao.data_negociacao,
                        AlocacaoInterna.data_liquidacao.name: alocacao.data_liquidacao,
                        AlocacaoInterna.alocado_em.name: alocacao.alocado_em,
                        AlocacaoInterna.aprovado_em.name: alocacao.aprovado_em,
                        AlocacaoInterna.fundo_id.name: alocacao.fundo_id,
                        AlocacaoInterna.tipo_ativo_id.name: alocacao.tipo_ativo_id,
                        AlocacaoInterna.alocacao_usuario_id.name: alocacao.alocacao_usuario_id,
                        AlocacaoInterna.aprovacao_usuario_id.name: alocacao.aprovacao_usuario_id,
                        AlocacaoInterna.alocacao_anterior_id.name: alocacao.alocacao_anterior_id,
                        AlocacaoInterna.corretora_id.name: alocacao.corretora_id,
                    }
                    for alocacao in alocacoes
                ]
            )
            .returning(AlocacaoInterna.id)
        )
        return results.scalars().all()

    async def buscar_boletas(
        self,
        *,
        data_liquidacao: date | None = None,
        ids_boletas: list[int] | None = None,
    ):
        usuario_que_alocou = aliased(Usuario)
        usuario_que_aprovou = aliased(Usuario)

        original = aliased(AlocacaoInterna)
        registro_original = aliased(B3RegistroNoMe)
        quebras = aliased(AlocacaoInterna)
        registro_quebra = aliased(B3RegistroNoMe)

        query = (
            select(Boleta)
            .outerjoin(Boleta.corretora)
            .outerjoin(Boleta.alocacoes.of_type(original))
            .outerjoin(original.fundo)
            .outerjoin(Fundo.administrador)
            # Infos originais
            .outerjoin(original.alocacao_usuario.of_type(usuario_que_alocou))
            .outerjoin(original.aprovacao_usuario.of_type(usuario_que_aprovou))
            .outerjoin(original.cancelamento)
            .outerjoin(original.alocacao_administrador)
            .outerjoin(original.pivot_casamento_voice)
            .outerjoin(AlocacoesInternasCasamentos.casamento)
            .outerjoin(CasamentoAlocacaoB3Voice.voice)
            .outerjoin(B3Voice.envios_pre_trade)
            .outerjoin(B3Voice.envios_post_trade)
            .outerjoin(AlocacaoAdministrador.cancelamento)
            .outerjoin(AlocacaoAdministrador.liquidacao)
            .outerjoin(original.registro_NoMe.of_type(registro_original))
            .outerjoin(original.quebras.of_type(quebras))
            # Infos quebras (herdarão informações da original, exceto quantidade e Registro NoMe)
            .outerjoin(quebras.registro_NoMe.of_type(registro_quebra))
            .options(
                contains_eager(Boleta.corretora),
                contains_eager(Boleta.alocacoes.of_type(original)),
                contains_eager(Boleta.alocacoes.of_type(original), original.fundo),
                contains_eager(
                    Boleta.alocacoes.of_type(original),
                    original.fundo,
                    Fundo.administrador,
                ),
                contains_eager(
                    Boleta.alocacoes.of_type(original),
                    original.alocacao_usuario.of_type(usuario_que_alocou),
                ),
                contains_eager(
                    Boleta.alocacoes.of_type(original),
                    original.aprovacao_usuario.of_type(usuario_que_aprovou),
                ),
                contains_eager(
                    Boleta.alocacoes.of_type(original), original.cancelamento
                ),
                contains_eager(
                    Boleta.alocacoes.of_type(original), original.alocacao_administrador
                ),
                contains_eager(
                    Boleta.alocacoes.of_type(original), original.pivot_casamento_voice
                ),
                contains_eager(
                    Boleta.alocacoes.of_type(original),
                    original.pivot_casamento_voice,
                    AlocacoesInternasCasamentos.casamento,
                ),
                contains_eager(
                    Boleta.alocacoes.of_type(original),
                    original.pivot_casamento_voice,
                    AlocacoesInternasCasamentos.casamento,
                    CasamentoAlocacaoB3Voice.voice,
                ),
                contains_eager(
                    Boleta.alocacoes.of_type(original),
                    original.pivot_casamento_voice,
                    AlocacoesInternasCasamentos.casamento,
                    CasamentoAlocacaoB3Voice.voice,
                    B3Voice.envios_pre_trade,
                ),
                contains_eager(
                    Boleta.alocacoes.of_type(original),
                    original.pivot_casamento_voice,
                    AlocacoesInternasCasamentos.casamento,
                    CasamentoAlocacaoB3Voice.voice,
                    B3Voice.envios_post_trade,
                ),
                contains_eager(
                    Boleta.alocacoes.of_type(original),
                    original.alocacao_administrador,
                    AlocacaoAdministrador.cancelamento,
                ),
                contains_eager(
                    Boleta.alocacoes.of_type(original),
                    original.alocacao_administrador,
                    AlocacaoAdministrador.liquidacao,
                ),
                contains_eager(
                    Boleta.alocacoes.of_type(original),
                    original.registro_NoMe.of_type(registro_original),
                ),
                contains_eager(
                    Boleta.alocacoes.of_type(original),
                    original.quebras.of_type(quebras),
                    quebras.registro_NoMe.of_type(registro_quebra),
                ),
            )
        )

        if data_liquidacao != None:
            query = query.where(Boleta.data_liquidacao == data_liquidacao)
        if ids_boletas != None:
            query = query.where(Boleta.id.in_(ids_boletas))

        self.db.expunge_all()

        results = await self.db.execute(query)
        return [
            ResultadoBuscaBoleta.from_model(resultado)
            for resultado in results.unique().scalars().all()
        ]

    async def aprovar_alocacoes(self, usuario_id: int, ids_alocacoes: list[int]):
        await self.db.execute(
            update(AlocacaoInterna),
            [
                {
                    AlocacaoInterna.id.name: id,
                    AlocacaoInterna.aprovado_em.name: datetime.now(),
                    AlocacaoInterna.aprovacao_usuario_id.name: usuario_id,
                }
                for id in ids_alocacoes
            ],
        )

    async def alocar_administrador(self, usuario_id: int, ids_alocacoes: list[int]):
        await self.db.execute(
            insert(AlocacaoAdministrador).values(
                [
                    {
                        AlocacaoAdministrador.alocacao_id.name: id,
                        AlocacaoAdministrador.alocado_em.name: datetime.now(),
                        AlocacaoAdministrador.alocacao_usuario_id.name: usuario_id,
                        AlocacaoAdministrador.codigo_administrador.name: None,
                    }
                    for id in ids_alocacoes
                ]
            )
        )

    async def alocacoes(self, ids_alocacoes: list[int]):
        results = await self.db.execute(
            select(AlocacaoInterna)
            .outerjoin(AlocacaoInterna.boleta)
            .outerjoin(Boleta.corretora)
            .outerjoin(AlocacaoInterna.fundo)
            .outerjoin(AlocacaoInterna.cancelamento)
            .outerjoin(AlocacaoInterna.alocacao_administrador)
            .outerjoin(AlocacaoInterna.registro_NoMe)
            .outerjoin(AlocacaoAdministrador.cancelamento)
            .outerjoin(AlocacaoAdministrador.liquidacao)
            .options(
                contains_eager(AlocacaoInterna.boleta),
                contains_eager(AlocacaoInterna.boleta, Boleta.corretora),
                contains_eager(AlocacaoInterna.fundo),
                contains_eager(AlocacaoInterna.cancelamento),
                contains_eager(AlocacaoInterna.alocacao_administrador),
                contains_eager(AlocacaoInterna.registro_NoMe),
                contains_eager(
                    AlocacaoInterna.alocacao_administrador,
                    AlocacaoAdministrador.cancelamento,
                ),
                contains_eager(
                    AlocacaoInterna.alocacao_administrador,
                    AlocacaoAdministrador.liquidacao,
                ),
            )
            .where(AlocacaoInterna.id.in_(ids_alocacoes))
        )
        return results.scalars().all()

    async def alocacoes_disponiveis_para_casamento(
        self, data_negociacao: date, ids_boletas: list[int] | None = None
    ):
        query = (
            select(Boleta)
            .outerjoin(Boleta.alocacoes)
            .outerjoin(AlocacaoInterna.cancelamento)
            .outerjoin(AlocacaoInterna.fundo)
            .outerjoin(AlocacaoInterna.corretora)
            .outerjoin(Corretora.b3_corretora)
            .outerjoin(AlocacaoInterna.pivot_casamento_voice)
            .outerjoin(AlocacoesInternasCasamentos.casamento)
            .outerjoin(CasamentoAlocacaoB3Voice.voice)
            .options(
                contains_eager(Boleta.alocacoes),
                contains_eager(Boleta.alocacoes, AlocacaoInterna.cancelamento),
                contains_eager(Boleta.alocacoes, AlocacaoInterna.fundo),
                contains_eager(Boleta.alocacoes, AlocacaoInterna.corretora),
                contains_eager(
                    Boleta.alocacoes, AlocacaoInterna.corretora, Corretora.b3_corretora
                ),
                contains_eager(Boleta.alocacoes, AlocacaoInterna.pivot_casamento_voice),
                contains_eager(
                    Boleta.alocacoes,
                    AlocacaoInterna.pivot_casamento_voice,
                    AlocacoesInternasCasamentos.casamento,
                ),
                contains_eager(
                    Boleta.alocacoes,
                    AlocacaoInterna.pivot_casamento_voice,
                    AlocacoesInternasCasamentos.casamento,
                    CasamentoAlocacaoB3Voice.voice,
                ),
            )
            .where(
                # Fluxo II
                Boleta.tipo_ativo_id.in_(
                    [
                        id.value
                        for id in [
                            TipoAtivo.ID.CRA,
                            TipoAtivo.ID.CRI,
                            TipoAtivo.ID.Debênture,
                            TipoAtivo.ID.FIDC,
                        ]
                    ]
                ),
                Boleta.mercado_negociado_id == MercadoNegociado.ID.SECUNDARIO,
                # Aprovado internamente
                AlocacaoInterna.aprovado_em != None,
                AlocacaoInterna.aprovacao_usuario_id != None,
                # Não pode ser quebra
                AlocacaoInterna.alocacao_anterior_id == None,
                # Precisa ter corretora
                Corretora.b3_corretora != None,
                # Negociado na data correta
                AlocacaoInterna.data_negociacao == data_negociacao,
                # Sem solicitação de cancelamento
                AlocacaoInterna.cancelamento == None,
                # Não pode estar casado
                AlocacaoInterna.pivot_casamento_voice == None,
            )
        )
        if ids_boletas:
            query = query.where(Boleta.id.in_(ids_boletas))
        self.db.expunge_all()
        results = await self.db.execute(query)
        alocacoes: list[AlocacaoInterna] = []
        for boleta in results.unique().scalars().all():
            logging.info(f"{boleta.id}: {len(boleta.alocacoes)}")
            alocacoes += boleta.alocacoes
        return alocacoes

    async def cancelar_alocacoes(
        self, usuario_id: int, ids_alocacoes: list[int], motivo: str | None = None
    ):
        await self.db.execute(
            insert(CancelamentoAlocacaoInterna).values(
                [
                    {
                        CancelamentoAlocacaoInterna.alocacao_id.name: id,
                        CancelamentoAlocacaoInterna.cancelado_em.name: datetime.now(),
                        CancelamentoAlocacaoInterna.motivo.name: motivo,
                        CancelamentoAlocacaoInterna.usuario_id.name: usuario_id,
                    }
                    for id in ids_alocacoes
                ]
            )
        )

    async def cancelar_alocacoes_administrador(
        self,
        usuario_id: int,
        ids_alocacoes_administrador: list[int],
        motivo: str | None = None,
    ):
        await self.db.execute(
            insert(CancelamentoAlocacaoAdministrador).values(
                [
                    {
                        CancelamentoAlocacaoAdministrador.alocacao_administrador_id.name: id,
                        CancelamentoAlocacaoAdministrador.cancelado_em.name: datetime.now(),
                        CancelamentoAlocacaoAdministrador.motivo.name: motivo,
                        CancelamentoAlocacaoAdministrador.usuario_id.name: usuario_id,
                    }
                    for id in ids_alocacoes_administrador
                ]
            )
        )

    async def sinalizar_liquidacao(
        self,
        usuario_id: int,
        ids_alocacoes_administrador: list[int],
    ):
        await self.db.execute(
            insert(LiquidacaoAlocacaoAdministrador).values(
                [
                    {
                        LiquidacaoAlocacaoAdministrador.alocacao_administrador_id.name: id,
                        LiquidacaoAlocacaoAdministrador.liquidado_em.name: datetime.now(),
                        CancelamentoAlocacaoAdministrador.usuario_id.name: usuario_id,
                    }
                    for id in ids_alocacoes_administrador
                ]
            )
        )

    async def criar_quebras(
        self, ids_alocacoes_anteriores_para_quantidades: dict[int, list[Decimal]]
    ):
        async with self.db.begin_nested():
            ids_para_alocacoes = {
                alocacao.id: alocacao
                for alocacao in await self.alocacoes(
                    [*ids_alocacoes_anteriores_para_quantidades.keys()]
                )
            }
            values: list[dict] = []
            for (
                id_anterior,
                quantidades,
            ) in ids_alocacoes_anteriores_para_quantidades.items():
                alocacao = ids_para_alocacoes[id_anterior]
                for quantidade in quantidades:
                    values.append(
                        {
                            # Informações das quebras
                            AlocacaoInterna.alocacao_anterior_id.name: id_anterior,
                            AlocacaoInterna.quantidade.name: quantidade,
                            # Dados "clonados" da alocação anterior
                            AlocacaoInterna.boleta_id.name: alocacao.boleta_id,
                            AlocacaoInterna.codigo_ativo.name: alocacao.codigo_ativo,
                            AlocacaoInterna.vanguarda_compra.name: alocacao.vanguarda_compra,
                            AlocacaoInterna.preco_unitario.name: alocacao.preco_unitario,
                            AlocacaoInterna.data_negociacao.name: alocacao.data_negociacao,
                            AlocacaoInterna.data_liquidacao.name: alocacao.data_liquidacao,
                            AlocacaoInterna.alocado_em.name: alocacao.alocado_em,
                            AlocacaoInterna.aprovado_em.name: alocacao.aprovado_em,
                            AlocacaoInterna.fundo_id.name: alocacao.fundo_id,
                            AlocacaoInterna.tipo_ativo_id.name: alocacao.tipo_ativo_id,
                            AlocacaoInterna.alocacao_usuario_id.name: alocacao.alocacao_usuario_id,
                            AlocacaoInterna.aprovacao_usuario_id.name: alocacao.aprovacao_usuario_id,
                            AlocacaoInterna.corretora_id.name: alocacao.corretora_id,
                        }
                    )
            results = await self.db.execute(
                insert(AlocacaoInterna)
                .values(values)
                .returning(
                    AlocacaoInterna.alocacao_anterior_id,
                    AlocacaoInterna.id,
                    AlocacaoInterna.quantidade,
                )
            )
            ids_antigos_para_novos_ids: dict[int, list[tuple[int, Decimal]]] = {}
            for id_antigo, id_novo, quantidade in results.tuples().all():
                if id_antigo not in ids_antigos_para_novos_ids:
                    ids_antigos_para_novos_ids[id_antigo or -1] = []
                ids_antigos_para_novos_ids[id_antigo or -1].append(
                    (id_novo, quantidade)
                )
            return ids_antigos_para_novos_ids
