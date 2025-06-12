from dataclasses import dataclass
from datetime import date, datetime
import json
import logging
from typing import Any, Literal
from sqlalchemy import DATE, ColumnElement, insert, or_, select, cast, update
from sqlalchemy.ext.asyncio.session import AsyncSession

from modules.operacoes.model import AlocacaoInterna, B3Mesa, B3Corretora, Corretora
from sqlalchemy.orm import aliased, joinedload, selectinload
from sqlalchemy.orm.strategy_options import contains_eager
from sqlalchemy.sql.functions import count

from .schema import (
    InfosMinimasRegistroNoMe,
    EstadoVoiceEnum,
    RelatorioVoicePreTradeSchema,
    RelatorioVoicePostTradeSchema,
)
from .model import (
    AlocacoesInternasCasamentos,
    B3Voice,
    B3RegistroNoMe,
    CasamentoAlocacaoB3Voice,
    EnvioAlocacaoB3Voice,
    EnvioDecisaoB3Voice,
)

from generated.bvmf_234_01 import Document as BVMF_234_01


@dataclass
class IDVoiceTrade:
    data_negociacao: date
    id_trader: str


@dataclass
class AtualizarRegistroNoMe:
    deve_atualizar_posicao_custodia: bool
    novo_valor_posicao_custodia: bool | None

    deve_atualizar_posicao_custodia_contraparte: bool
    novo_valor_posicao_custodia_contraparte: bool | None


@dataclass
class B3Repository:
    db: AsyncSession

    async def detalhes_voices(self, data: date):
        results = await self.db.execute(
            select(B3Voice)
            .outerjoin(B3Voice.envios_pre_trade)
            .outerjoin(B3Voice.envios_post_trade)
            .outerjoin(B3Voice.casamento)
            .outerjoin(CasamentoAlocacaoB3Voice.pivot_alocacoes)
            .outerjoin(AlocacoesInternasCasamentos.alocacao)
            .options(
                contains_eager(B3Voice.envios_pre_trade),
                contains_eager(B3Voice.envios_post_trade),
                contains_eager(B3Voice.casamento),
                contains_eager(
                    B3Voice.casamento, CasamentoAlocacaoB3Voice.pivot_alocacoes
                ),
                contains_eager(
                    B3Voice.casamento,
                    CasamentoAlocacaoB3Voice.pivot_alocacoes,
                    AlocacoesInternasCasamentos.alocacao,
                ),
            )
            .where(B3Voice.data_negociacao == data)
        )
        return results.unique().scalars().all()

    async def voices_casados_candidatos_a_envio_de_decisao(self, data_negociacao: date):
        results = await self.db.execute(
            select(B3Voice)
            .outerjoin(B3Voice.casamento)
            .outerjoin(B3Voice.envios_pre_trade)
            .options(
                contains_eager(B3Voice.casamento),
                contains_eager(B3Voice.envios_pre_trade),
            )
            .where(
                B3Voice.casamento != None,
                B3Voice.aprovado_em == None,
                B3Voice.cancelado_em == None,
                B3Voice.data_negociacao == data_negociacao,
            )
            .group_by(
                B3Voice.id,
                CasamentoAlocacaoB3Voice.voice_id,
                EnvioDecisaoB3Voice.id,
            )
            .having(count(B3Voice.envios_pre_trade) == 0)
        )
        return results.unique().scalars().all()

    async def voices_casados_candidatos_a_envio_de_alocacao(
        self, data_negociacao: date
    ):
        results = await self.db.execute(
            select(B3Voice)
            .outerjoin(B3Voice.casamento)
            .outerjoin(B3Voice.envios_post_trade)
            .options(
                contains_eager(B3Voice.casamento),
                contains_eager(B3Voice.envios_post_trade),
            )
            .where(
                B3Voice.horario_recebimento_post_trade != None,
                B3Voice.casamento != None,
                B3Voice.data_negociacao == data_negociacao,
            )
            .group_by(
                B3Voice.id, CasamentoAlocacaoB3Voice.voice_id, EnvioAlocacaoB3Voice.id
            )
            .having(count(B3Voice.envios_post_trade) == 0)
        )
        return results.unique().scalars().all()

    async def voices_disponiveis_para_casamento(
        self, data_negociacao: date, voice_id: int | None = None
    ):
        b3_corretora_order_entry = aliased(B3Corretora)
        corretora_order_entry = aliased(Corretora)

        b3_corretora_post_trade = aliased(B3Corretora)
        corretora_post_trade = aliased(Corretora)

        query = (
            select(B3Voice)
            .outerjoin(B3Voice.casamento)
            .outerjoin(B3Voice.b3_mesa_order_entry)
            # Informações cruzadas Order Entry (só temos ID da mesa na B3)
            .outerjoin(B3Mesa.b3_corretora.of_type(b3_corretora_order_entry))
            .outerjoin(
                b3_corretora_order_entry.corretora.of_type(corretora_order_entry)
            )
            # Informações cruzadas Post Trade (só temos nome da instituição na B3)
            .outerjoin(B3Voice.b3_corretora_post_trade.of_type(b3_corretora_post_trade))
            .outerjoin(b3_corretora_post_trade.corretora.of_type(corretora_post_trade))
            .options(
                contains_eager(B3Voice.casamento),
                contains_eager(B3Voice.b3_mesa_order_entry),
                contains_eager(
                    B3Voice.b3_mesa_order_entry,
                    B3Mesa.b3_corretora.of_type(b3_corretora_order_entry),
                ),
                contains_eager(
                    B3Voice.b3_mesa_order_entry,
                    B3Mesa.b3_corretora.of_type(b3_corretora_order_entry),
                    b3_corretora_order_entry.corretora.of_type(corretora_order_entry),
                ),
                contains_eager(
                    B3Voice.b3_corretora_post_trade.of_type(b3_corretora_post_trade),
                    b3_corretora_post_trade.corretora.of_type(corretora_post_trade),
                ),
            )
            .where(
                B3Voice.cancelado_em == None,
                B3Voice.data_negociacao == data_negociacao,
                B3Voice.casamento == None,
                or_(
                    b3_corretora_order_entry.corretora != None,
                    b3_corretora_post_trade.corretora != None,
                ),
            )
        )
        if voice_id:
            query = query.where(B3Voice.id == voice_id)
        self.db.expunge_all()
        results = await self.db.execute(query)
        return results.unique().scalars().all()

    async def voices(self, ids: list[IDVoiceTrade | int]):
        conditions: list[ColumnElement[bool]] = []
        for id in ids:
            if type(id) == int:
                conditions.append(B3Voice.id == id)
            elif type(id) == IDVoiceTrade:
                conditions.append(
                    (B3Voice.data_negociacao == id.data_negociacao)
                    & (B3Voice.id_trader == id.id_trader)
                )
        original = aliased(AlocacaoInterna)
        registro_original = aliased(B3RegistroNoMe)
        quebras = aliased(AlocacaoInterna)
        registro_quebra = aliased(B3RegistroNoMe)
        query = (
            select(B3Voice)
            .outerjoin(B3Voice.casamento)
            .outerjoin(CasamentoAlocacaoB3Voice.pivot_alocacoes)
            .outerjoin(AlocacoesInternasCasamentos.alocacao.of_type(original))
            .outerjoin(original.fundo)
            .outerjoin(original.registro_NoMe.of_type(registro_original))
            .outerjoin(original.quebras.of_type(quebras))
            .outerjoin(quebras.registro_NoMe.of_type(registro_quebra))
            .options(
                contains_eager(B3Voice.casamento),
                contains_eager(
                    B3Voice.casamento, CasamentoAlocacaoB3Voice.pivot_alocacoes
                ),
                contains_eager(
                    B3Voice.casamento,
                    CasamentoAlocacaoB3Voice.pivot_alocacoes,
                    AlocacoesInternasCasamentos.alocacao.of_type(original),
                ),
                contains_eager(
                    B3Voice.casamento,
                    CasamentoAlocacaoB3Voice.pivot_alocacoes,
                    AlocacoesInternasCasamentos.alocacao.of_type(original),
                    original.fundo,
                ),
                contains_eager(
                    B3Voice.casamento,
                    CasamentoAlocacaoB3Voice.pivot_alocacoes,
                    AlocacoesInternasCasamentos.alocacao.of_type(original),
                    original.registro_NoMe.of_type(registro_original),
                ),
                contains_eager(
                    B3Voice.casamento,
                    CasamentoAlocacaoB3Voice.pivot_alocacoes,
                    AlocacoesInternasCasamentos.alocacao.of_type(original),
                    original.quebras.of_type(quebras),
                ),
                contains_eager(
                    B3Voice.casamento,
                    CasamentoAlocacaoB3Voice.pivot_alocacoes,
                    AlocacoesInternasCasamentos.alocacao.of_type(original),
                    original.quebras.of_type(quebras),
                    quebras.registro_NoMe.of_type(registro_quebra),
                ),
            )
        )
        if conditions:
            query = query.where(or_(*conditions))

        # Invalidando objetos existentes na sessão para retornar resultados "frescos" do banco
        self.db.expunge_all()

        results = await self.db.execute(query)
        return results.unique().scalars().all()

    async def criar_voice_a_partir_de_relatorio_pre_trade(
        self, voice: RelatorioVoicePreTradeSchema
    ):
        agora = datetime.now()
        results = await self.db.execute(
            insert(B3Voice)
            .values(
                {
                    B3Voice.id_ordem.name: voice.id_ordem,
                    B3Voice.id_ordem_secundario.name: voice.id_ordem_secundario,
                    B3Voice.id_trader.name: voice.id_trader,
                    B3Voice.id_execucao.name: voice.id_execucao,
                    B3Voice.codigo_ativo.name: voice.codigo_ativo,
                    B3Voice.vanguarda_compra.name: voice.vanguarda_compra,
                    B3Voice.preco_unitario.name: voice.preco_unitario,
                    B3Voice.quantidade.name: voice.quantidade,
                    B3Voice.data_negociacao.name: voice.data_negociacao,
                    B3Voice.data_liquidacao.name: voice.data_liquidacao,
                    B3Voice.contraparte_b3_mesa_id.name: voice.contraparte_b3_mesa_id,
                    B3Voice.horario_recebimento_order_entry.name: agora,
                    B3Voice.horario_recebimento_post_trade.name: None,
                    B3Voice.aprovado_em.name: (
                        agora if voice.status == EstadoVoiceEnum.ACATADO else None
                    ),
                    B3Voice.cancelado_em.name: (
                        agora if voice.status == EstadoVoiceEnum.CANCELADO else None
                    ),
                }
            )
            .returning(B3Voice.id)
        )
        return results.scalars().one()

    async def salvar_envio_decisao_voice(
        self,
        usuario_id: int,
        decisao: Literal["ACATO", "REJEIÇÃO"],
        voice_id: int,
        sequencia_fix: int,
    ):
        agora = datetime.now()
        result = await self.db.execute(
            insert(EnvioDecisaoB3Voice)
            .values(
                {
                    EnvioDecisaoB3Voice.voice_id.name: voice_id,
                    EnvioDecisaoB3Voice.decisao.name: decisao,
                    EnvioDecisaoB3Voice.sequencia_fix.name: sequencia_fix,
                    EnvioDecisaoB3Voice.enviado_em.name: agora,
                    EnvioDecisaoB3Voice.erro_em.name: None,
                    EnvioDecisaoB3Voice.detalhes_erro.name: None,
                    EnvioDecisaoB3Voice.usuario_id.name: usuario_id,
                }
            )
            .returning(EnvioDecisaoB3Voice.id)
        )
        return result.scalar()

    async def salvar_envio_alocacao_voice(
        self, usuario_id: int, id_msg: str, voice_id: int, conteudo: str
    ):
        agora = datetime.now()
        await self.db.execute(
            insert(EnvioAlocacaoB3Voice).values(
                {
                    EnvioAlocacaoB3Voice.id.name: id_msg,
                    EnvioAlocacaoB3Voice.voice_id.name: voice_id,
                    EnvioAlocacaoB3Voice.enviado_em.name: agora,
                    EnvioAlocacaoB3Voice.erro_em.name: None,
                    EnvioAlocacaoB3Voice.detalhes_erro.name: None,
                    EnvioAlocacaoB3Voice.sucesso_em.name: None,
                    EnvioAlocacaoB3Voice.usuario_id.name: usuario_id,
                    EnvioAlocacaoB3Voice.conteudo.name: conteudo,
                }
            )
        )

    async def envios_decisao_voice(
        self,
        data_negociacao: date,
        *,
        voice_id: int | None = None,
        sequencia_fix: int | None = None,
    ):
        condicoes = [cast(EnvioDecisaoB3Voice.enviado_em, DATE) == data_negociacao]
        if sequencia_fix:
            condicoes.append(EnvioDecisaoB3Voice.sequencia_fix == sequencia_fix)
        if voice_id:
            condicoes.append(EnvioDecisaoB3Voice.voice_id == voice_id)

        results = await self.db.execute(
            select(EnvioDecisaoB3Voice)
            .where(*condicoes)
            .order_by(EnvioDecisaoB3Voice.enviado_em.desc())
            .limit(1)
        )
        return results.scalar_one_or_none()

    async def envios_alocacao_do_voice(self, id_voice: int):
        results = await self.db.execute(
            select(EnvioAlocacaoB3Voice)
            .where(EnvioAlocacaoB3Voice.voice_id == id_voice)
            .order_by(EnvioAlocacaoB3Voice.enviado_em.desc())
            .limit(1)
        )
        return results.scalar_one_or_none()

    async def atualizar_decisao_voice(
        self,
        id_decisao: int,
        *,
        erro_em: datetime | None = None,
        detalhes_erro: str | None = None,
    ):
        update_info = {}
        if erro_em:
            update_info[EnvioDecisaoB3Voice.erro_em.name] = erro_em
        if detalhes_erro:
            update_info[EnvioDecisaoB3Voice.detalhes_erro.name] = detalhes_erro

        await self.db.execute(
            update(EnvioDecisaoB3Voice)
            .where(EnvioDecisaoB3Voice.id == id_decisao)
            .values(update_info)
        )

    async def atualizar_envio_alocacao_voice(
        self,
        id_envio_alocacao: str,
        *,
        erro_em: datetime | None = None,
        detalhes_erro: str | None = None,
        sucesso_em: datetime | None = None,
    ):
        update_info = {}
        if erro_em:
            update_info[EnvioAlocacaoB3Voice.erro_em.name] = erro_em
        if detalhes_erro:
            update_info[EnvioAlocacaoB3Voice.detalhes_erro.name] = detalhes_erro
        if sucesso_em:
            update_info[EnvioAlocacaoB3Voice.sucesso_em.name] = sucesso_em

        await self.db.execute(
            update(EnvioAlocacaoB3Voice)
            .where(EnvioAlocacaoB3Voice.id == id_envio_alocacao)
            .values(update_info)
        )

    async def atualizar_status_voice(
        self,
        id_voice: int,
        *,
        id_execucao: str,
        horario_recebimento_order_entry: datetime | None = None,
        horario_recebimento_post_trade: datetime | None = None,
        aprovado_em: datetime | None = None,
        cancelado_em: datetime | None = None,
    ):
        await self.db.execute(
            update(B3Voice)
            .where(B3Voice.id == id_voice)
            .values(
                {
                    B3Voice.id_execucao.name: id_execucao,
                    B3Voice.horario_recebimento_order_entry.name: horario_recebimento_order_entry,
                    B3Voice.horario_recebimento_post_trade.name: horario_recebimento_post_trade,
                    B3Voice.aprovado_em.name: aprovado_em,
                    B3Voice.cancelado_em.name: cancelado_em,
                }
            )
        )

    async def salvar_casamento_voice_alocacoes(
        self, usuario_id: int, voice_alocacoes: dict[int, list[int]]
    ):
        agora = datetime.now()
        async with self.db.begin_nested():
            infos_casamento = [
                {
                    CasamentoAlocacaoB3Voice.voice_id.name: voice_id,
                    CasamentoAlocacaoB3Voice.usuario_id.name: usuario_id,
                    CasamentoAlocacaoB3Voice.casado_em.name: agora,
                }
                for voice_id, alocacoes_ids in voice_alocacoes.items()
                if alocacoes_ids
            ]
            if not infos_casamento:
                return
            alocacoes_casamentos = [
                {
                    AlocacoesInternasCasamentos.casamento_id.name: voice_id,
                    AlocacoesInternasCasamentos.alocacao_id.name: alocacao_id,
                }
                for voice_id, alocacoes_ids in voice_alocacoes.items()
                for alocacao_id in alocacoes_ids
            ]
            if not alocacoes_casamentos:
                return
            await self.db.execute(
                insert(CasamentoAlocacaoB3Voice).values(infos_casamento)
            )
            await self.db.execute(
                insert(AlocacoesInternasCasamentos).values(alocacoes_casamentos)
            )

    async def preencher_e_salvar_informacoes_post_trade(
        self,
        voice: B3Voice,
        horario_recebimento_post_trade: datetime,
        id_instrumento: str,
        id_instrumento_subjacente: str | None,
    ):
        await self.db.execute(
            update(B3Voice)
            .values(
                {
                    B3Voice.horario_recebimento_post_trade.name: horario_recebimento_post_trade,
                    B3Voice.aprovado_em.name: (
                        voice.aprovado_em
                        if voice.aprovado_em
                        else horario_recebimento_post_trade
                    ),
                    B3Voice.id_instrumento.name: id_instrumento,
                    B3Voice.id_instrumento_subjacente.name: id_instrumento_subjacente,
                }
            )
            .where(B3Voice.id == voice.id)
        )
        voice.horario_recebimento_post_trade = horario_recebimento_post_trade
        voice.id_instrumento = id_instrumento
        voice.id_instrumento_subjacente

    async def criar_voice_a_partir_de_relatorio_post_trade(
        self, relatorio: RelatorioVoicePostTradeSchema
    ):
        agora = datetime.now()
        results = await self.db.execute(
            insert(B3Voice)
            .values(
                {
                    B3Voice.id_ordem.name: "",
                    B3Voice.id_ordem_secundario.name: "",
                    B3Voice.id_trader.name: relatorio.id_trader,
                    B3Voice.id_execucao.name: "",
                    B3Voice.codigo_ativo.name: relatorio.codigo_ativo,
                    B3Voice.id_instrumento.name: relatorio.id_instrumento,
                    B3Voice.id_instrumento_subjacente.name: relatorio.id_instrumento_subjacente,
                    B3Voice.vanguarda_compra.name: relatorio.vanguarda_compra,
                    B3Voice.preco_unitario.name: relatorio.preco_unitario,
                    B3Voice.quantidade.name: relatorio.quantidade,
                    B3Voice.data_negociacao.name: relatorio.data_negociacao,
                    B3Voice.data_liquidacao.name: relatorio.data_liquidacao,
                    B3Voice.contraparte_b3_corretora_nome.name: relatorio.contraparte_b3_corretora_nome,
                    B3Voice.horario_recebimento_order_entry.name: None,
                    B3Voice.horario_recebimento_post_trade.name: agora,
                    B3Voice.aprovado_em.name: agora,
                    B3Voice.cancelado_em.name: None,
                }
            )
            .returning(B3Voice.id)
        )
        return results.scalars().one()

    async def criar_registros_NoMe(self, registros: list[InfosMinimasRegistroNoMe]):
        hoje = date.today()
        agora = datetime.now()
        await self.db.execute(
            insert(B3RegistroNoMe).values(
                [
                    {
                        B3RegistroNoMe.alocacao_id.name: registro.alocacao_id,
                        B3RegistroNoMe.numero_controle.name: registro.numero_controle,
                        B3RegistroNoMe.data.name: hoje,
                        B3RegistroNoMe.recebido_em.name: agora,
                    }
                    for registro in registros
                ]
            )
        )

    async def registros_NoMe(self, numeros_controle: list[str]):
        self.db.expunge_all()
        results = await self.db.execute(
            select(B3RegistroNoMe).where(
                B3RegistroNoMe.numero_controle.in_(numeros_controle)
            )
        )
        return results.scalars().all()

    async def atualizar_registros_NoMe(
        self,
        data_negociacao: date,
        ids_alocacao_status: dict[int, AtualizarRegistroNoMe],
    ):
        agora = datetime.now()
        valores = [
            {
                B3RegistroNoMe.alocacao_id.name: id_alocacao,
                B3RegistroNoMe.data.name: data_negociacao,
                **(
                    {
                        B3RegistroNoMe.posicao_custodia.name: status.novo_valor_posicao_custodia,
                        B3RegistroNoMe.posicao_custodia_em.name: agora,
                    }
                    if status.deve_atualizar_posicao_custodia
                    else {}
                ),
                **(
                    {
                        B3RegistroNoMe.posicao_custodia_contraparte.name: status.novo_valor_posicao_custodia_contraparte,
                        B3RegistroNoMe.posicao_custodia_contraparte_em.name: agora,
                    }
                    if status.deve_atualizar_posicao_custodia_contraparte
                    else {}
                ),
            }
            for id_alocacao, status in ids_alocacao_status.items()
        ]
        await self.db.execute(update(B3RegistroNoMe), valores)
