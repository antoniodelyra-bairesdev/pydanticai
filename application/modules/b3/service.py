import asyncio
from calendar import timegm
from decimal import Decimal
import json
import logging

from datetime import date, datetime

from dataclasses import dataclass

from pandas import read_excel
from sqlalchemy.ext.asyncio import AsyncSession
from subprocess import run, PIPE
from typing import BinaryIO, Coroutine, Literal, Sequence

from config.environment import SessaoFIXType, fix_config

from modules.auth.model import Usuario
from modules.email.schema import EmailTemplateSchema
from modules.email.service import EmailService, EmailServiceFactory
from modules.operacoes.repository import OperacoesRepository
from modules.operacoes.schema import EmailAlocacoesSchema, IdentificadorCorretora
from modules.operacoes.model import AlocacaoInterna
from modules.websockets.service import WebSocketService

from .repository import AtualizarRegistroNoMe, B3Repository, IDVoiceTrade
from .schema import (
    AlocacaoPostTradeSchema,
    CasamentoAlocacaoB3VoiceSchema,
    EmailVoiceSchema,
    EnvioAlocacaoSchema,
    EnvioAlocacoesPostTrade,
    EstadoVoiceEnum,
    RejeicaoVoicePostTradeSchema,
    RelatorioVoicePostTradeSchema,
    RelatorioVoicePreTradeSchema,
    StatusRegistroNoMeEnum,
    StatusVoicePostTradeEnum,
    VoiceDetalhesSchema,
    VoiceSchema,
    VoiceSimulacaoCasamento,
    AlocacaoSimulacaoCasamento,
    InfosMinimasRegistroNoMe,
    InfosMinimasAlocacao,
)
from .model import B3RegistroNoMe, B3Voice


class B3ServiceFactory:
    @staticmethod
    def criarService(db: AsyncSession):
        return B3Service(
            b3_repository=B3Repository(db=db),
            operacoes_repository=OperacoesRepository(db=db),
            email_service=EmailServiceFactory.criarService(db=db),
        )


@dataclass
class B3Service:
    b3_repository: B3Repository
    operacoes_repository: OperacoesRepository
    email_service: EmailService

    @staticmethod
    def is_messaging_reachable(application: SessaoFIXType) -> tuple[bool, str]:
        try:
            config = fix_config(application)
            result = run(
                ["nc", "-z", "-v", "-w", "5", config.address, config.port],
                text=True,
                stdout=PIPE,
                stderr=PIPE,
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception:
            return False, "Erro interno."
    
    async def converter_exportacoes(self, arquivo_voices: BinaryIO, arquivo_boleta: BinaryIO):
        limpar = lambda txt: txt.replace('.', '').replace('/', '').replace('-','')
        _str = lambda x: str(x).strip()
        sem_pontuacao = lambda txt: limpar(_str(txt))
        alocacoes = (
            read_excel(
                arquivo_boleta,
                converters={
                    "Código": _str,
                    "Ativo": _str,
                    "Dt. Operac.": _str,
                    "Side": _str,
                    "CETIP": sem_pontuacao,
                    "CNPJ": sem_pontuacao,
                    "Cliente": _str,
                    "Contraparte": _str,
                    "Quant.": lambda x: float(_str(x)),
                    "P.U.": lambda x: float(_str(x)),
                },
            )
            .fillna("")
            .to_dict("records")
        )
        cnpj_para_cetip: dict[str, str] = {
            alocacao['CNPJ']: alocacao['CETIP']
            for alocacao in alocacoes
        }
        voices = (
            read_excel(
                arquivo_voices,
                converters={
                    "Código Negociação": _str,
                    "Data e hora da execução do negócio": _str,
                    "Natureza da operação": _str,
                    "Cód. Família de Front Contraparte": _str,
                    "Quantidade do Negócio": lambda x: float(_str(x)),
                    "Valor Unitário do Título": lambda x: float(_str(x)),
                },
            )
            .fillna("")
            .to_dict("records")
        )

        apelidos_corretora = {
            alocacao['Contraparte']
            for alocacao in alocacoes
        }
        nomes_corretoras = {
            alocacao['Cód. Família de Front Contraparte']
            for alocacao in voices
        }
        corretora_nome_b3_para_apelido_vanguarda = {
            corretora.b3_corretora.nome: corretora.nome
            for corretora in await self.operacoes_repository.buscar_corretoras([
                *[
                    IdentificadorCorretora(
                        tipo='APELIDO_VANGUARDA',
                        valor=apelido
                    )
                    for apelido in apelidos_corretora
                ],
                *[
                    IdentificadorCorretora(
                        tipo='NOME_INSTITUICAO',
                        valor=nome
                    )
                    for nome in nomes_corretoras
                ]
            ])
            if corretora.b3_corretora
        }
        
        @dataclass
        class _ReturnType:
            boleta: list[AlocacaoSimulacaoCasamento]
            voices: list[VoiceSimulacaoCasamento]
            cnpj_para_cetip: dict[str, str]

        return _ReturnType(
            boleta=[
                AlocacaoSimulacaoCasamento(
                    id=linha,
                    ativo=alocacao["Código"],
                    corretora=alocacao["Contraparte"],
                    data_liquidacao=datetime.fromisoformat(alocacao['Dt. Operac.']).date(),
                    data_negociacao=datetime.fromisoformat(alocacao['Dt. Operac.']).date(),
                    fundo_cnpj=alocacao['CNPJ'],
                    horario=datetime.now(),
                    lado_operacao=alocacao['Side'],
                    preco=round(alocacao['P.U.'], 8),
                    quantidade=round(alocacao['Quant.'], 8),
                    boleta_id=0,
                    voice_id=None,
                )
                for linha, alocacao in enumerate(alocacoes, 2)
                if type(alocacao['Nº YMF']) == int and alocacao['Nº YMF'] > 0
            ],
            voices=[
                VoiceSimulacaoCasamento(
                    id=voice['Número do negócio'],
                    ativo=voice['Código Negociação'],
                    lado_operacao="C" if voice['Natureza da operação'] == 'Compra' else "V",
                    preco=round(voice['Valor Unitário do Título'], 8),
                    quantidade=round(voice['Quantidade do Negócio'], 8),
                    horario=datetime.fromisoformat(voice['Data e hora da execução do negócio']),
                    data_negociacao=datetime.fromisoformat(voice['Data do Negócio']).date(),
                    data_liquidacao=datetime.fromisoformat(voice['Data de liquidação']).date(),
                    corretora=(
                        corretora_nome_b3_para_apelido_vanguarda[voice['Cód. Família de Front Contraparte']]
                        if voice['Cód. Família de Front Contraparte'] in corretora_nome_b3_para_apelido_vanguarda
                        else 'Não registrada'
                    ),
                )
                for voice in voices
            ],
            cnpj_para_cetip=cnpj_para_cetip
        )

    async def listar_voices(self, data: date):
        voices = await self.b3_repository.detalhes_voices(data)
        return [VoiceDetalhesSchema.from_model(voice) for voice in voices]

    async def enviar_decisoes_nao_transmitidas(self, usuario: Usuario):
        hoje = date.today()
        voices = await self.b3_repository.voices_casados_candidatos_a_envio_de_decisao(
            hoje
        )
        for voice in voices:
            await self.enviar_decisao_voice(usuario, "ACATO", hoje, voice.id_trader)

    async def enviar_alocacoes_nao_transmitidas(self, usuario: Usuario):
        hoje = date.today()
        voices = await self.b3_repository.voices_casados_candidatos_a_envio_de_alocacao(
            hoje
        )
        for voice in voices:
            await self.enviar_casamentos_pendentes_para_b3_caso_existam(
                usuario, voice.id
            )
        return voices

    async def enviar_decisao_voice(
        self,
        usuario: Usuario,
        decisao: Literal["ACATO", "REJEIÇÃO"],
        data_negociacao: date,
        id_trader: str,
        motivo_rejeicao="Rejeitado via sistema.",
    ):
        from .fix.order_entry_application import OrderEntryApplicationSingleton

        async with self.b3_repository.db.begin_nested():
            voices = await self.b3_repository.voices(
                [IDVoiceTrade(data_negociacao=data_negociacao, id_trader=id_trader)]
            )
            if len(voices) != 1:
                return
            [voice] = voices

            application = OrderEntryApplicationSingleton.get_application()
            dados_msg = application.envio_decisao_voice(decisao, voice, motivo_rejeicao)
            if not dados_msg:
                return
            id = await self.b3_repository.salvar_envio_decisao_voice(
                usuario.id, decisao, voice.id, dados_msg.numero_sequencia
            )
            if not id:
                return
            await WebSocketService.send_json(
                {
                    "canal": "operacoes.alocacao",
                    "tipo": "voice.orderentry.envio",
                    "dados": {
                        "id_trader": voice.id_trader,
                        "id_envio": id,
                        "enviado_em": datetime.now().isoformat(),
                    },
                }
            )

    async def erro_envio_decisao_voice(
        self,
        data_negociacao: date,
        codigo: str,
        detalhes: str,
        *,
        voice_id: int | None = None,
        sequencia_fix: int | None = None,
    ):
        async with self.b3_repository.db.begin_nested():
            if voice_id == None and sequencia_fix == None:
                return logging.error(
                    "Pelo menos um dos dois campos precisa ser informado: sequencia_fix, voice_id."
                )
            envio = await self.b3_repository.envios_decisao_voice(
                data_negociacao, sequencia_fix=sequencia_fix
            )
            if not envio or envio.erro_em:
                return
            agora = datetime.now()
            detalhes_erro = f"Erro{(' ' + codigo) if codigo else ''}: {detalhes}"
            await self.b3_repository.atualizar_decisao_voice(
                envio.id,
                erro_em=agora,
                detalhes_erro=detalhes_erro,
            )
            voices = [*await self.b3_repository.voices([envio.voice_id])]
            if not voices:
                return
            [voice] = voices
            await WebSocketService.send_json(
                {
                    "canal": "operacoes.alocacao",
                    "tipo": "voice.orderentry.erro",
                    "dados": {
                        "id_trader": voice.id_trader,
                        "id_envio": envio.id,
                        "erro": detalhes_erro,
                    },
                }
            )

    async def erro_envio_alocacao_voice(self, rejeicao: RejeicaoVoicePostTradeSchema):
        async with self.b3_repository.db.begin_nested():
            agora = datetime.now()
            await self.b3_repository.atualizar_envio_alocacao_voice(
                rejeicao.id_msg,
                erro_em=agora,
                detalhes_erro=rejeicao.detalhes_erro,
            )
            await WebSocketService.send_json(
                {
                    "canal": "operacoes.alocacao",
                    "tipo": "voice.posttrade.erro",
                    "dados": {
                        "id_trader": rejeicao.id_trader,
                        "id_envio": rejeicao.id_msg,
                        "erro": rejeicao.detalhes_erro,
                    },
                }
            )

    async def atualizar_informacoes_voice_pre_trade(
        self,
        usuario: Usuario,
        relatorio_voice: RelatorioVoicePreTradeSchema,
        erro: str | None = None,
    ):
        async with self.b3_repository.db.begin_nested():
            voices = await self.b3_repository.voices(
                [
                    IDVoiceTrade(
                        id_trader=relatorio_voice.id_trader,
                        data_negociacao=relatorio_voice.data_negociacao,
                    )
                ]
            )
            if not voices:
                voice_id = await self.b3_repository.criar_voice_a_partir_de_relatorio_pre_trade(
                    relatorio_voice
                )
                await self.casar_voices_e_alocacoes(
                    usuario, "ORDER_ENTRY", voice_id=voice_id
                )
                return
            [voice] = voices
            agora = datetime.now()
            await self.b3_repository.atualizar_status_voice(
                voice.id,
                id_execucao=relatorio_voice.id_execucao,
                aprovado_em=(
                    agora
                    if not voice.aprovado_em
                    and relatorio_voice.status == EstadoVoiceEnum.ACATADO
                    else voice.aprovado_em
                ),
                cancelado_em=(
                    agora
                    if not voice.cancelado_em
                    and relatorio_voice.status == EstadoVoiceEnum.CANCELADO
                    else voice.cancelado_em
                ),
                horario_recebimento_order_entry=(
                    voice.horario_recebimento_order_entry or agora
                ),
                horario_recebimento_post_trade=voice.horario_recebimento_post_trade,
            )
            if relatorio_voice.status != EstadoVoiceEnum.REJEITADO:
                return
            await self.erro_envio_decisao_voice(
                date.today(),
                "",
                erro if erro else "Dados não informados",
                voice_id=voice.id,
            )

    async def casar_voices_e_alocacoes(
        self,
        usuario: Usuario,
        etapa: SessaoFIXType | None = None,
        *,
        voice_id: int | None = None,
        ids_boletas: list[int] | None = None,
    ) -> dict[int, list[int]]:
        async with self.b3_repository.db.begin_nested():
            hoje = date.today()
            voices = {
                voice.id: voice
                for voice in await self.b3_repository.voices_disponiveis_para_casamento(
                    hoje, voice_id
                )
            }
            if not voices:
                return {}
            alocacoes = (
                await self.operacoes_repository.alocacoes_disponiveis_para_casamento(
                    hoje, ids_boletas
                )
            )
            voices_sim, alocacoes_sim = self._gerar_formato_simulacao_casamento(
                [*voices.values()], alocacoes
            )
            boletas: dict[int, list[AlocacaoSimulacaoCasamento]] = {}
            for alocacao in alocacoes_sim:
                b_id = alocacao.boleta_id
                if b_id not in boletas:
                    boletas[b_id] = []
                boletas[b_id].append(alocacao)
            resultados: list[AlocacaoSimulacaoCasamento] = []
            for voice in voices_sim:
                for alocacoes in boletas.values():
                    resultado = self._casar_voice_com_alocacoes(voice, alocacoes)
                    for alocacao in resultado:
                        alocacao.voice_id = voice.id
                    resultados += resultado

            voice_alocacoes: dict[int, list[int]] = {}
            for alocacao in resultados:
                vid = alocacao.voice_id
                if not vid:
                    continue
                if vid not in voice_alocacoes:
                    voice_alocacoes[vid] = []
                voice_alocacoes[vid].append(alocacao.id)

            await self.b3_repository.salvar_casamento_voice_alocacoes(
                usuario.id, voice_alocacoes
            )

            alocacao_para_boleta = {
                alocacao.id: boleta
                for boleta in await self.operacoes_repository.buscar_boletas(
                    data_liquidacao=date.today(),
                    ids_boletas=[id_boleta for id_boleta in boletas],
                )
                for alocacao in boleta.alocacoes
            }

            agora = datetime.now()
            if not voice_alocacoes:
                return voice_alocacoes

            from modules.operacoes.service import OperacoesService

            for vid in voice_alocacoes:
                voice = voices[vid]
                alocacoes = voice_alocacoes[vid]
                if not alocacoes:
                    continue
                boleta = alocacao_para_boleta[alocacoes[0]]
                boleta.alocacoes = [
                    alocacao
                    for alocacao in boleta.alocacoes
                    if alocacao.id in alocacoes
                ]
                await WebSocketService.send_json(
                    {
                        "canal": "operacoes.alocacao",
                        "tipo": "voice.casamento",
                        "dados": {
                            "casamento": CasamentoAlocacaoB3VoiceSchema(
                                casado_em=agora,
                                voice=VoiceSchema(
                                    id_trader=voice.id_trader,
                                    horario_recebimento_post_trade=(
                                        agora if etapa == "POST_TRADE" else None
                                    ),
                                ),
                            ).model_dump(mode="json"),
                            "alocacoes_ids": alocacoes,
                        },
                    }
                )
                # await self.email_service.enviar(
                #     [usuario.email],
                #     "[SISTEMA] Casamento de alocações com voice",
                #     EmailTemplateSchema(
                #         titulo=f"Casamento de alocações com voice",
                #         conteudo_html=f"""{
                #             EmailAlocacoesSchema(
                #                 fluxoII=OperacoesService.eh_fluxoII(
                #                     boleta.tipo_ativo_id,
                #                     boleta.mercado_negociado_id,
                #                 ),
                #                 boleta=boleta,
                #                 usuario='Sistema Vanguarda',
                #                 acao="casou as seguintes alocações com o voice abaixo.",
                #             ).html()
                #         }<br><br>{
                #             EmailVoiceSchema(
                #                 id_trader=voice.id_trader,
                #                 codigo_ativo=voice.codigo_ativo,
                #                 side='C' if voice.vanguarda_compra else 'V',
                #                 preco_unitario=voice.preco_unitario,
                #                 quantidade=voice.quantidade,
                #                 nome_contraparte=(
                #                     voice.b3_mesa_order_entry.b3_corretora.corretora.nome if voice.b3_mesa_order_entry else
                #                     voice.b3_corretora_post_trade.corretora.nome if voice.b3_corretora_post_trade else
                #                     'Nome da corretora não encontrado'
                #                 )
                #             ).html()
                #         }""",
                #     ).html(),
                #     [
                #         "backoffice@icatuvanguarda.com.br",
                #         "grupomesacp@icatuvanguarda.com.br",
                #     ],
                # )
            for voice_id in voice_alocacoes.keys():
                voice = voices[voice_id]
                if not voice.horario_recebimento_post_trade:
                    await self.enviar_decisao_voice(
                        usuario, "ACATO", voice.data_negociacao, voice.id_trader
                    )
            return voice_alocacoes

    def _gerar_formato_simulacao_casamento(
        self, voices: Sequence[B3Voice], alocacoes: Sequence[AlocacaoInterna]
    ):
        return (
            [
                VoiceSimulacaoCasamento(
                    id=voice.id,
                    ativo=voice.codigo_ativo,
                    lado_operacao="C" if voice.vanguarda_compra else "V",
                    preco=round(voice.preco_unitario, 8),
                    quantidade=round(voice.quantidade, 8),
                    horario=voice.horario_recebimento_order_entry
                    or voice.horario_recebimento_post_trade
                    or datetime.now(),
                    data_negociacao=voice.data_negociacao,
                    data_liquidacao=voice.data_liquidacao,
                    corretora=(
                        voice.b3_mesa_order_entry.b3_corretora.corretora.nome
                        if voice.b3_mesa_order_entry
                        else (
                            voice.b3_corretora_post_trade.corretora.nome
                            if voice.b3_corretora_post_trade
                            else ""
                        )
                    ),
                )
                for voice in voices
            ],
            [
                AlocacaoSimulacaoCasamento(
                    id=alocacao.id,
                    ativo=alocacao.codigo_ativo,
                    corretora=alocacao.corretora.b3_corretora.corretora.nome,
                    data_liquidacao=alocacao.data_liquidacao,
                    data_negociacao=alocacao.data_negociacao,
                    fundo_cnpj=alocacao.fundo.cnpj,
                    horario=alocacao.alocado_em,
                    lado_operacao="C" if alocacao.vanguarda_compra else "V",
                    preco=round(alocacao.preco_unitario, 8),
                    quantidade=round(alocacao.quantidade, 8),
                    boleta_id=alocacao.boleta_id,
                    voice_id=None,
                )
                for alocacao in alocacoes
            ],
        )

    def _encontrar_combinacao(self, valor_total: Decimal, valores: list[Decimal]):
        pos_atual: int = 0
        pos_candidatas: list[int] = []
        soma = 0
        while pos_atual < len(valores):
            soma_candidata = soma + valores[pos_atual]
            if soma_candidata <= valor_total:
                pos_candidatas.append(pos_atual)
                soma = soma_candidata
            if soma == valor_total:
                return pos_candidatas
            while pos_atual == len(valores) - 1:
                if len(pos_candidatas) > 0:
                    ultima_posicao = pos_candidatas.pop()
                    soma -= valores[ultima_posicao]
                    pos_atual = ultima_posicao
                else:
                    return []
            pos_atual += 1
        return []

    def _casar_voice_com_alocacoes(
        self,
        voice: VoiceSimulacaoCasamento,
        alocacoes: list[AlocacaoSimulacaoCasamento],
    ):
        alocacoes_ord = sorted(
            sorted(
                [
                    alocacao
                    for alocacao in alocacoes
                    if (
                        alocacao.ativo == voice.ativo
                        and alocacao.preco == voice.preco
                        and alocacao.lado_operacao == voice.lado_operacao
                        and alocacao.data_liquidacao == voice.data_liquidacao
                        and alocacao.data_negociacao == voice.data_negociacao
                        and alocacao.corretora == voice.corretora
                        and alocacao.voice_id is None
                    )
                ],
                key=lambda a: f"{timegm(a.horario.timetuple())}-{a.id}",
            ),
            key=lambda a: a.quantidade,
            reverse=True,
        )
        combinacao = self._encontrar_combinacao(
            voice.quantidade, [alocacao.quantidade for alocacao in alocacoes_ord]
        )
        return [alocacoes_ord[pos] for pos in combinacao]

    def relatorio_possui_alocacoes(self, relatorio: RelatorioVoicePostTradeSchema):
        return len(relatorio.alocacoes) > 0

    def registros_NoMe_foram_emitidos(self, relatorio: RelatorioVoicePostTradeSchema):
        return self.relatorio_possui_alocacoes(relatorio) and all(
            [
                detalhe_alocacao.registro_nome != None
                for detalhe_alocacao in relatorio.alocacoes
            ]
        )

    def alocacoes_estao_sincronizadas(
        self, alocacoes: list[AlocacaoInterna], relatorio: RelatorioVoicePostTradeSchema
    ):
        if len(alocacoes) != len(relatorio.alocacoes):
            return False
        quantidades_alocacoes_internas = sorted(
            [alocacao.quantidade for alocacao in alocacoes]
        )
        quantidades_alocacoes_b3 = sorted(
            [detalhe_alocacao.quantidade for detalhe_alocacao in relatorio.alocacoes]
        )
        for i in range(0, len(alocacoes)):
            qtd_int = quantidades_alocacoes_internas[i]
            qtd_ext = quantidades_alocacoes_b3[i]
            if qtd_int != qtd_ext:
                return False
        return True

    def alocacoes_ja_foram_quebradas(self, voice: B3Voice):
        logging.info("=" * 80)
        if voice.casamento:
            logging.info(f"{voice.casamento.casado_em}")
            for pivot in voice.casamento.pivot_alocacoes:
                logging.info(f"\t{pivot.alocacao.id} ({pivot.alocacao.quantidade})")
                for quebra in pivot.alocacao.quebras:
                    logging.info(
                        f"\t|----> {quebra.id} ({quebra.quantidade}) {quebra.registro_NoMe.numero_controle if quebra.registro_NoMe else '---'}"
                    )
        logging.info("=" * 80)
        return (
            False
            if not voice.casamento
            else any(
                [
                    pivot.alocacao.registro_NoMe or pivot.alocacao.quebras
                    for pivot in voice.casamento.pivot_alocacoes
                ]
            )
        )

    def detectar_quebras(
        self,
        alocacoes: list[InfosMinimasAlocacao],
        registros: list[InfosMinimasRegistroNoMe],
    ) -> dict[int, list[str]]:
        # Quantidade de alocações precisa ser menor ou igual à quantidade de registros
        if len(alocacoes) > len(registros):
            return {}

        soma_fundos_alocacoes: dict[str, Decimal] = {}
        for alocacao in alocacoes:
            cetip = alocacao.cetip.replace("-", "").replace(".", "")
            alocacao.cetip = cetip
            if cetip not in soma_fundos_alocacoes:
                soma_fundos_alocacoes[cetip] = Decimal(0)
            soma_fundos_alocacoes[cetip] += alocacao.quantidade

        soma_fundos_registros: dict[str, Decimal] = {}
        for registro in registros:
            cetip = registro.cetip.replace("-", "").replace(".", "")
            registro.cetip = cetip
            if cetip not in soma_fundos_registros:
                soma_fundos_registros[cetip] = Decimal(0)
            soma_fundos_registros[cetip] += registro.quantidade

        # Soma total precisa ser igual
        if sum(soma_fundos_alocacoes.values()) != sum(soma_fundos_registros.values()):
            return {}

        # Soma por fundo precisa ser igual
        for fundo in soma_fundos_alocacoes:
            if fundo not in soma_fundos_registros:
                return {}
            if soma_fundos_alocacoes[fundo] != soma_fundos_registros[fundo]:
                return {}

        # Segregando os registros por fundo
        registros_por_fundo: dict[str, list[InfosMinimasRegistroNoMe]] = {}
        for registro in registros:
            if registro.cetip not in registros_por_fundo:
                registros_por_fundo[registro.cetip] = []
            registros_por_fundo[registro.cetip].append(registro)

        _alocacoes = [*alocacoes]

        alocacao_id_para_registros_numero_controle: dict[int, list[str]] = {}

        # Primeira leitura: encontrar iguais
        for alocacao in _alocacoes:
            _registros = registros_por_fundo[alocacao.cetip]
            pos_igual = -1
            for i, registro in enumerate(_registros):
                if (
                    alocacao.quantidade == registro.quantidade
                    and alocacao.cetip == registro.cetip
                ):
                    alocacao_id_para_registros_numero_controle[alocacao.id] = [
                        registro.numero_controle
                    ]
                    pos_igual = i
                    break
            if pos_igual != -1:
                _registros.pop(pos_igual)

        # Segunda leitura: encontrar quebras
        _alocacoes = [
            alocacao
            for alocacao in _alocacoes
            if alocacao.id not in alocacao_id_para_registros_numero_controle
        ]
        for alocacao in _alocacoes:
            _registros = registros_por_fundo[alocacao.cetip]
            combinacao = sorted(
                self._encontrar_combinacao(
                    alocacao.quantidade,
                    [registro.quantidade for registro in _registros],
                ),
                reverse=True,
            )
            if not combinacao:
                continue
            for pos in combinacao:
                if alocacao.id not in alocacao_id_para_registros_numero_controle:
                    alocacao_id_para_registros_numero_controle[alocacao.id] = []
                alocacao_id_para_registros_numero_controle[alocacao.id].append(
                    _registros[pos].numero_controle
                )
            for pos in combinacao:
                _registros.pop(pos)

        return (
            {}
            if len(alocacoes) != len(alocacao_id_para_registros_numero_controle)
            else alocacao_id_para_registros_numero_controle
        )

    async def atualizar_informacoes_voice_post_trade(
        self, usuario: Usuario, relatorio: RelatorioVoicePostTradeSchema
    ):
        async with self.b3_repository.db.begin_nested():
            voices = [
                *await self.b3_repository.voices(
                    [
                        IDVoiceTrade(
                            data_negociacao=relatorio.data_negociacao,
                            id_trader=relatorio.id_trader,
                        )
                    ]
                )
            ]

            # Mensageria de Order Entry pode não estar funcionando (voice foi detectado pela primeira vez somente via Post Trade)
            if not voices:
                logging.info("Criando novo voice...")
                voice_id = await self.b3_repository.criar_voice_a_partir_de_relatorio_post_trade(
                    relatorio
                )
                voices = [*await self.b3_repository.voices([voice_id])]

            [voice] = voices

            # Mensageria de Order Entry provavelmente estava funcionando mas é a primeira vez que recebemos as informações de Post Trade
            if not voice.horario_recebimento_post_trade:
                logging.info("Preenchendo informações faltantes")
                agora = datetime.now()
                await self.b3_repository.preencher_e_salvar_informacoes_post_trade(
                    voice,
                    agora,
                    relatorio.id_instrumento,
                    relatorio.id_instrumento_subjacente,
                )
                await WebSocketService.send_json(
                    {
                        "canal": "operacoes.alocacao",
                        "tipo": "voice.posttrade.recebido",
                        "dados": {
                            "id_trader": voice.id_trader,
                            "horario_recebimento_post_trade": agora.isoformat(),
                        },
                    }
                )

            # Voice ainda não foi alocado na [B]³
            if not self.relatorio_possui_alocacoes(relatorio):
                if not voice.casamento:
                    # Precisamos realizar o casamento das alocações antes da transmissão, caso já não tenha ocorrido.
                    voices_alocacoes = await self.casar_voices_e_alocacoes(
                        usuario, "POST_TRADE", voice_id=voice.id
                    )
                    if not voices_alocacoes:
                        return logging.info("Não há alocações para transmitir.")
                if relatorio.status in {
                    StatusVoicePostTradeEnum.Novo,
                    StatusVoicePostTradeEnum.Pendente_Alocação,
                    StatusVoicePostTradeEnum.Pendente_Confirmação,
                }:
                    return await self.enviar_casamentos_pendentes_para_b3_caso_existam(
                        usuario, voice.id
                    )

            # Voice já foi alocado na [B]³

            # Relatório veio com as alocações mas não temos estas informações no nosso banco de dados: as alocações foram feitas por outro sistema.
            if not voice.casamento:
                return logging.info(
                    "Alocações recebidas, mas voice não foi casado com nenhuma alocação."
                )

            # Não há registros na depositária NoMe: Contraparte não alocou.
            if not self.registros_NoMe_foram_emitidos(relatorio):
                alocacoes_internas = [
                    pivot.alocacao for pivot in voice.casamento.pivot_alocacoes
                ]
                # Por algum motivo as alocações não são as mesmas que as armazenadas. O casamento foi realizado, porém antes de ser transmitido ou processado, as alocações foram realizadas externamente.
                if not self.alocacoes_estao_sincronizadas(
                    alocacoes_internas, relatorio
                ):
                    return logging.info(
                        "Alocações recebidas, mas as alocações do voice não coincidem."
                    )
                # As alocações são as mesmas que temos armazenadas no sistema. Notificar sucesso na alocação. Ficamos no aguardo da alocação da contraparte.
                logging.info(
                    "Alocações transmitidas com sucesso. Falta alocação da contraparte."
                )
                envio = await self.b3_repository.envios_alocacao_do_voice(voice.id)
                if not envio:
                    return
                agora = datetime.now()
                await self.b3_repository.atualizar_envio_alocacao_voice(
                    envio.id, sucesso_em=agora
                )
                await WebSocketService.send_json(
                    {
                        "canal": "operacoes.alocacao",
                        "tipo": "voice.posttrade.alocado",
                        "dados": {
                            "id_trader": voice.id_trader,
                            "id_envio": envio.id,
                            "sucesso_em": agora.isoformat(),
                        },
                    }
                )
                return

            # Há registros na depositária NoMe: Contraparte alocou e quebras de alocações podem ter ocorrido.

            # Busca os Registros NoMe existentes para esse voice

            # Detectar quebras de alocações caso não tenham sido realizadas
            if not self.alocacoes_ja_foram_quebradas(voice):
                ids_para_alocacoes_internas = {
                    pivot.alocacao.id: InfosMinimasAlocacao(
                        id=pivot.alocacao.id,
                        quantidade=pivot.alocacao.quantidade,
                        cetip=pivot.alocacao.fundo.conta_cetip or "",
                    )
                    for pivot in voice.casamento.pivot_alocacoes
                }
                ids_para_registros_recebidos = {
                    alocacao.registro_nome.numero_controle: InfosMinimasRegistroNoMe(
                        numero_controle=alocacao.registro_nome.numero_controle,
                        quantidade=alocacao.quantidade,
                        cetip=alocacao.cetip,
                        alocacao_id=None,
                    )
                    for alocacao in relatorio.alocacoes
                    if alocacao.registro_nome != None
                }
                casamento_alocacoes_registros_NoMe = self.detectar_quebras(
                    [*ids_para_alocacoes_internas.values()],
                    [*ids_para_registros_recebidos.values()],
                )
                if casamento_alocacoes_registros_NoMe:
                    iguais = {
                        k: v
                        for k, v in casamento_alocacoes_registros_NoMe.items()
                        if len(v) == 1
                    }
                    if iguais:
                        infos_registros_NoMe_iguais = [
                            InfosMinimasRegistroNoMe(
                                numero_controle=rid,
                                alocacao_id=aid,
                                quantidade=ids_para_registros_recebidos[rid].quantidade,
                                cetip=ids_para_registros_recebidos[rid].cetip,
                            )
                            for aid, [rid] in iguais.items()
                        ]
                        await self.b3_repository.criar_registros_NoMe(
                            infos_registros_NoMe_iguais
                        )
                        await WebSocketService.send_json(
                            {
                                "canal": "operacoes.alocacao",
                                "tipo": "voice.registro_nome.novos",
                                "dados": infos_registros_NoMe_iguais,
                            }
                        )
                        logging.info(
                            f"Registros casados com as alocações: {json.dumps(iguais, indent=2)}"
                        )
                    quebras = {
                        k: v
                        for k, v in casamento_alocacoes_registros_NoMe.items()
                        if len(v) > 1
                    }
                    if not quebras:
                        return
                    logging.info(f"Quebras detectadas: {json.dumps(quebras, indent=2)}")
                    await self.armazenar_quebras_de_alocacao(
                        {
                            aid: [ids_para_registros_recebidos[rid] for rid in rids]
                            for aid, rids in quebras.items()
                        }
                    )
                else:
                    return logging.info(
                        f"Não foi possível associar os registros NoMe com as alocações informadas."
                    )

            registros_NoMe = {
                registro.numero_controle: registro
                for registro in await self.b3_repository.registros_NoMe(
                    [
                        alocacao.registro_nome.numero_controle
                        for alocacao in relatorio.alocacoes
                        if alocacao.registro_nome
                    ]
                )
            }

            infos_atualizacao = {
                registros_NoMe[
                    alocacao.registro_nome.numero_controle
                ].alocacao_id: self.infos_atualizacao_registro_NoMe(
                    registros_NoMe, alocacao
                )
                for alocacao in relatorio.alocacoes
                if alocacao.registro_nome
                and alocacao.registro_nome.numero_controle in registros_NoMe
            }

            await self.b3_repository.atualizar_registros_NoMe(
                relatorio.data_negociacao, infos_atualizacao
            )

            messages: list[Coroutine] = []
            for alocacao_id, atualizacao in infos_atualizacao.items():
                if (
                    not atualizacao.deve_atualizar_posicao_custodia
                    and not atualizacao.deve_atualizar_posicao_custodia_contraparte
                ):
                    continue
                agora = datetime.now()
                messages.append(
                    WebSocketService.send_json(
                        {
                            "canal": "operacoes.alocacao",
                            "tipo": "voice.registro_nome.atualizacao",
                            "dados": {
                                "alocacao_id": alocacao_id,
                                **(
                                    {
                                        "posicao_custodia": atualizacao.novo_valor_posicao_custodia,
                                        "posicao_custodia_em": agora,
                                    }
                                    if atualizacao.deve_atualizar_posicao_custodia
                                    else {}
                                ),
                                **(
                                    {
                                        "posicao_custodia_contraparte": atualizacao.novo_valor_posicao_custodia_contraparte,
                                        "posicao_custodia_contraparte_em": agora,
                                    }
                                    if atualizacao.deve_atualizar_posicao_custodia_contraparte
                                    else {}
                                ),
                            },
                        }
                    )
                )

            if messages:
                await asyncio.gather(*messages)

    def infos_atualizacao_registro_NoMe(
        self,
        registros_existentes: dict[str, B3RegistroNoMe],
        alocacao: AlocacaoPostTradeSchema,
    ):
        rn = alocacao.registro_nome
        if not rn:
            return AtualizarRegistroNoMe(
                deve_atualizar_posicao_custodia=False,
                novo_valor_posicao_custodia=None,
                deve_atualizar_posicao_custodia_contraparte=False,
                novo_valor_posicao_custodia_contraparte=None,
            )

        status_com_aprovacao_custodia = {
            StatusRegistroNoMeEnum.Pendente_Confirmação_Contraparte_Custodiante,
            StatusRegistroNoMeEnum.Confirmado_pelo_Custodiante,
            StatusRegistroNoMeEnum.Disponível_para_Registro,
        }
        status_com_rejeicao_custodia = {
            StatusRegistroNoMeEnum.Rejeitado_pelo_Custodiante
        }
        deve_atualizar_posicao_custodia = registros_existentes[
            rn.numero_controle
        ].posicao_custodia == None and rn.status in {
            *status_com_aprovacao_custodia,
            *status_com_rejeicao_custodia,
        }

        status_com_aprovacao_custodia_contraparte = {
            StatusRegistroNoMeEnum.Disponível_para_Registro
        }
        status_com_rejeicao_custodia_contraparte = {
            StatusRegistroNoMeEnum.Rejeitado_pela_Contraparte_Custodiante
        }
        deve_atualizar_posicao_custodia_contraparte = registros_existentes[
            rn.numero_controle
        ].posicao_custodia_contraparte == None and rn.status in {
            *status_com_aprovacao_custodia_contraparte,
            *status_com_rejeicao_custodia_contraparte,
        }

        return AtualizarRegistroNoMe(
            deve_atualizar_posicao_custodia=deve_atualizar_posicao_custodia,
            novo_valor_posicao_custodia=(
                True
                if rn.status in status_com_aprovacao_custodia
                else False if rn.status in status_com_rejeicao_custodia else None
            ),
            deve_atualizar_posicao_custodia_contraparte=deve_atualizar_posicao_custodia_contraparte,
            novo_valor_posicao_custodia_contraparte=(
                True
                if rn.status in status_com_aprovacao_custodia_contraparte
                else (
                    False
                    if rn.status in status_com_rejeicao_custodia_contraparte
                    else None
                )
            ),
        )

    async def armazenar_quebras_de_alocacao(
        self,
        alocacao_id_para_registros: dict[int, list[InfosMinimasRegistroNoMe]],
    ):
        async with self.operacoes_repository.db.begin_nested():
            infos_quebras = {
                id_alocacao: [registro.quantidade for registro in registros]
                for id_alocacao, registros in alocacao_id_para_registros.items()
            }
            resultados = await self.operacoes_repository.criar_quebras(infos_quebras)
            await WebSocketService.send_json(
                {
                    "canal": "operacoes.alocacao",
                    "tipo": "alocacoes.quebras",
                    "dados": [
                        {
                            "alocacao_anterior_id": alocacao_anterior_id,
                            "quebras": [
                                {"alocacao_id": alocacao_id, "quantidade": quantidade}
                                for alocacao_id, quantidade in pares_novo_id_quantidade
                            ],
                        }
                        for alocacao_anterior_id, pares_novo_id_quantidade in resultados.items()
                    ],
                }
            )
            infos_registros_novos: list[InfosMinimasRegistroNoMe] = []
            for id_alocacao_anterior in resultados:
                novos_ids_e_quantidades = sorted(
                    resultados[id_alocacao_anterior],
                    key=lambda par: par[1],
                    reverse=True,
                )
                registros = sorted(
                    alocacao_id_para_registros[id_alocacao_anterior],
                    key=lambda r: r.quantidade,
                    reverse=True,
                )
                for i, (novo_id, _) in enumerate(novos_ids_e_quantidades):
                    registros[i].alocacao_id = novo_id
                    infos_registros_novos.append(registros[i])
            await self.b3_repository.criar_registros_NoMe(infos_registros_novos)
            await WebSocketService.send_json(
                {
                    "canal": "operacoes.alocacao",
                    "tipo": "voice.registro_nome.novos",
                    "dados": infos_registros_novos,
                }
            )

    async def enviar_casamentos_pendentes_para_b3_caso_existam(
        self, usuario: Usuario, voice_id: int
    ):
        voices = [*await self.b3_repository.voices([voice_id])]
        if not voices:
            return logging.info("Voice inexistente")
        [voice] = voices
        if not voice.casamento:
            return logging.info("Voice não possui casamento a ser transmitido.")
        if not voice.horario_recebimento_post_trade:
            return logging.info(
                "Voice ainda não possui informações para transmissão no Post Trade"
            )

        if not voice.id_instrumento or any(
            [
                not pivot.alocacao.fundo.conta_cetip
                for pivot in voice.casamento.pivot_alocacoes
            ]
        ):
            return

        infos_envio = EnvioAlocacoesPostTrade(
            id_trade=voice.id_trader,
            id_instrumento=voice.id_instrumento,
            vanguarda_compra=voice.vanguarda_compra,
            data_negociacao=voice.data_negociacao,
            horario=datetime.now(),
            alocacoes=[
                EnvioAlocacaoSchema(
                    cetip=pivot.alocacao.fundo.conta_cetip or "",
                    quantidade=pivot.alocacao.quantidade,
                )
                for pivot in voice.casamento.pivot_alocacoes
            ],
        )

        from .fix.post_trade_application import PostTradeApplicationSingleton

        application = PostTradeApplicationSingleton.get_application()
        infos = application.enviar_alocacoes(infos_envio)
        if not infos:
            return
        id_msg, mensagem_xml = infos
        await self.b3_repository.salvar_envio_alocacao_voice(
            usuario.id, id_msg, voice.id, mensagem_xml
        )
        await WebSocketService.send_json(
            {
                "canal": "operacoes.alocacao",
                "tipo": "voice.posttrade.envio",
                "dados": {
                    "id_trader": voice.id_trader,
                    "id_envio": id_msg,
                    "enviado_em": datetime.now().isoformat(),
                },
            }
        )
