import asyncio

from datetime import date, datetime
from decimal import Decimal
from http import HTTPStatus

from dataclasses import dataclass
from pandas import read_excel
from typing import BinaryIO, Coroutine, Literal, Hashable, Any

from fastapi.exceptions import HTTPException

from modules.ativos.model import TipoAtivo
from modules.ativos.repository import AtivosRepository
from modules.auth.model import Usuario
from modules.b3.service import B3Service, B3ServiceFactory
from modules.email.service import EmailService, EmailServiceFactory
from modules.email.schema import EmailTemplateSchema
from modules.fundos.repository import FundosRepository
from modules.websockets.service import WebSocketService

from sqlalchemy.ext.asyncio import AsyncSession

from .model import MercadoNegociado, NaturezaOperacao
from .repository import CriarAlocacao, CriarBoleta, OperacoesRepository
from .schema import (
    AlocacaoSchema,
    BoletaSchema,
    EmailAlocacoesSchema,
    ResultadoBuscaBoleta,
    ResultadoBuscaBoleta_Alocacao,
    ResultadoBuscaBoleta_Corretora,
    ResultadoBuscaBoleta_Fundo,
    SugestaoBoleta,
    Interna,
    IdentificadorAtivo,
    IdentificadorCorretora,
    IdentificadorFundo,
    TipoOperacao,
    Mercado,
)


class OperacoesServiceFactory:
    @staticmethod
    def criarService(db: AsyncSession):
        return OperacoesService(
            operacoes_repository=OperacoesRepository(db),
            fundos_repository=FundosRepository(db),
            ativos_repository=AtivosRepository(db),
            b3_service=B3ServiceFactory.criarService(db),
            email_service=EmailServiceFactory.criarService(db),
        )


@dataclass
class OperacoesService:
    operacoes_repository: OperacoesRepository
    fundos_repository: FundosRepository
    ativos_repository: AtivosRepository
    b3_service: B3Service
    email_service: EmailService

    def processar_boleta_v2(
        self,
        file: BinaryIO,
        formato: Literal["titpriv"],
    ):
        match formato:
            case "titpriv":
                return self.processar_boleta_v2_titulos_privados(file)

    async def processar_boleta_v2_titulos_privados(self, file: BinaryIO):
        dados = self._processar_arquivo_boleta_v2_titulos_privados(file)
        fundos = await self.fundos_repository.buscar_fundos(
            [IdentificadorFundo(tipo="CETIP", valor=dado["CETIP"]) for dado in dados]
        )
        contas_cetip_registradas = {
            fundo.conta_cetip.strip().replace(".", "").replace("-", "")
            for fundo in fundos
            if fundo.conta_cetip
        }
        corretoras = await self.operacoes_repository.buscar_corretoras(
            [
                IdentificadorCorretora(
                    tipo="APELIDO_VANGUARDA", valor=dado["Contraparte"]
                )
                for dado in dados
            ]
        )
        nomes_corretoras_registradas = {corretora.nome for corretora in corretoras}
        tickers_registrados = {*await self.ativos_repository.lista_codigos()}
        resultados: list[OperacoesService.ResultadoProcessamentoLinhaTitPriv] = []
        for linha, dado in enumerate(dados):
            resultado = self._processar_linha_boleta_titulos_privados_v2(
                dado,
                linha + 2,
                contas_cetip_registradas,
                nomes_corretoras_registradas,
                tickers_registrados,
            )
            resultados.append(resultado)
        return resultados

    def _processar_arquivo_boleta_v2_titulos_privados(self, file: BinaryIO):
        _str = lambda x: str(x).strip()
        return (
            read_excel(
                file,
                converters={
                    "Código": _str,
                    "Ativo": _str,
                    "Dt. Operac.": _str,
                    "Side": _str,
                    "CETIP": _str,
                    "Cliente": _str,
                    "Contraparte": _str,
                    "Quant.": lambda x: float(_str(x)),
                    "P.U.": lambda x: float(_str(x)),
                },
            )
            .fillna("")
            .to_dict("records")
        )

    @dataclass
    class ResultadoProcessamentoLinhaTitPriv:
        linha: int
        status: Literal["ERRO", "VAZIA", "AVISO", "OK"]
        dados: AlocacaoSchema | None
        detalhes: str | None

    def _processar_linha_boleta_titulos_privados_v2(
        self,
        dado: dict[Hashable, Any],
        linha: int,
        contas_cetip_registradas: set[str],
        nomes_corretoras_registradas: set[str],
        tickers_registrados: set[str],
    ):
        tipo_ativo = dado["Ativo"]
        cod = dado["Código"]
        side = dado["Side"]
        cetip = dado["CETIP"].strip().replace(".", "").replace("-", "")
        dt_liq = dado["Dt. Operac."]
        try:
            dt_liq = datetime.fromisoformat(dt_liq)
        except:
            dt_liq = ""
        if not dt_liq:
            try:
                dt_liq = datetime.strptime(dt_liq, "%d/%m/%Y")
            except:
                dt_liq = ""
        corretora = dado["Contraparte"]
        qtd = dado["Quant."]
        pu = dado["P.U."]

        avisos = []

        if (
            not cod
            and (side not in {"C", "V"})
            and not dt_liq
            and not qtd
            and not pu
            and not cetip
            and not corretora
        ):
            return OperacoesService.ResultadoProcessamentoLinhaTitPriv(
                status="VAZIA", dados=None, linha=linha, detalhes=None
            )
        elif (
            not cod
            or (side not in {"C", "V"})
            or not dt_liq
            or not qtd
            or not pu
            or not cetip
            or not corretora
        ):
            return OperacoesService.ResultadoProcessamentoLinhaTitPriv(
                status="ERRO",
                dados=None,
                linha=linha,
                detalhes="Linha parcialmente preenchida.",
            )

        if cetip not in contas_cetip_registradas:
            return OperacoesService.ResultadoProcessamentoLinhaTitPriv(
                status="ERRO",
                dados=None,
                linha=linha,
                detalhes=f'Conta CETIP "{cetip}" não registrada em nenhum fundo no sistema.',
            )
        if corretora not in nomes_corretoras_registradas:
            return OperacoesService.ResultadoProcessamentoLinhaTitPriv(
                status="ERRO",
                dados=None,
                linha=linha,
                detalhes=f'Corretora "{corretora}" não registrada no sistema.',
            )
        if cod not in tickers_registrados:
            avisos.append(f'Ativo "{cod}" não registrado no sistema.')

        try:
            alocacao = AlocacaoSchema(
                id=linha,
                id_ativo=IdentificadorAtivo(
                    tipo_ativo=tipo_ativo, tipo_codigo="TICKER", codigo=cod
                ),
                lado_operacao="C" if side == "C" else "V",
                preco=pu,
                quantidade=qtd,
                id_corretora=IdentificadorCorretora(
                    tipo="APELIDO_VANGUARDA", valor=corretora
                ),
                id_fundo=IdentificadorFundo(tipo="CETIP", valor=cetip),
                data_liquidacao=dt_liq,
                horario=datetime.now(),
            )
            return OperacoesService.ResultadoProcessamentoLinhaTitPriv(
                status="AVISO" if avisos else "OK",
                dados=alocacao,
                linha=linha,
                detalhes="\n".join(avisos) if avisos else None,
            )
        except:
            return OperacoesService.ResultadoProcessamentoLinhaTitPriv(
                status="ERRO",
                dados=None,
                linha=linha,
                detalhes="Dados inválidos. Verificar linha.",
            )

    async def separacao_alocacoes(
        self,
        alocacoes: list[AlocacaoSchema],
        formato: Literal["titpriv"],
        estrategia_duplicadas: Literal[
            "ignorar-alterar", "ignorar-criar", "manter-alterar", "manter-criar"
        ],
    ):
        if estrategia_duplicadas != "manter-criar":
            raise HTTPException(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                'Atualmente só há suporte para o método "manter-criar"',
            )
        sugestoes = self._sugestao_boletas(alocacoes)
        return await self._preencher_informacoes_sugestoes_boletas(sugestoes)

    async def _preencher_informacoes_sugestoes_boletas(
        self, sugestoes: list[SugestaoBoleta]
    ):
        corretoras = await self.operacoes_repository.buscar_corretoras(
            [
                IdentificadorCorretora(tipo="APELIDO_VANGUARDA", valor=boleta.corretora)
                for boleta in sugestoes
            ]
        )
        apelido_para_corretora = {corretora.nome: corretora for corretora in corretoras}

        fundos = await self.fundos_repository.buscar_fundos(
            [alocacao.id_fundo for boleta in sugestoes for alocacao in boleta.alocacoes]
        )
        cetip_para_fundo = {
            fundo.conta_cetip.strip().replace(".", "").replace("-", ""): fundo
            for fundo in fundos
            if fundo.conta_cetip
        }
        boletas: list[ResultadoBuscaBoleta] = []
        for boleta in sugestoes:
            corretora = apelido_para_corretora[boleta.corretora]
            alocacoes: list[ResultadoBuscaBoleta_Alocacao] = []
            for alocacao in boleta.alocacoes:
                fundo = cetip_para_fundo[alocacao.id_fundo.valor]
                f = ResultadoBuscaBoleta_Fundo.from_model(fundo)
                alocacoes.append(
                    ResultadoBuscaBoleta_Alocacao(
                        id=-1,
                        alocacao_anterior_id=None,
                        alocacao_usuario="",
                        data_negociacao=date.today(),
                        data_liquidacao=alocacao.data_liquidacao,
                        alocado_em=datetime.now(),
                        aprovacao_usuario=None,
                        aprovado_em=None,
                        codigo_ativo=alocacao.id_ativo.codigo,
                        corretora_id=corretora.id,
                        fundo=f,
                        preco_unitario=Decimal(alocacao.preco),
                        quantidade=Decimal(alocacao.quantidade),
                        vanguarda_compra=alocacao.lado_operacao == "C",
                        cancelamento=None,
                        alocacao_administrador=None,
                    )
                )
            boletas.append(
                ResultadoBuscaBoleta(
                    id=-1,
                    data_liquidacao=boleta.horario.date(),
                    mercado_negociado_id=(
                        MercadoNegociado.ID[boleta.mercado] if boleta.mercado else 0
                    ),
                    natureza_operacao_id=NaturezaOperacao.ID[boleta.tipo],
                    tipo_ativo_id=TipoAtivo.ID[boleta.tipo_ativo],
                    corretora=ResultadoBuscaBoleta_Corretora(
                        id=corretora.id, nome=corretora.nome
                    ),
                    alocacoes=alocacoes,
                )
            )
        return boletas

    def _identificar_internas(self, alocacoes: list[AlocacaoSchema]):
        @dataclass
        class Resultado:
            compras_em_aberto: list[AlocacaoSchema]
            vendas_em_aberto: list[AlocacaoSchema]
            internas: list[Interna]

        resultado = Resultado(compras_em_aberto=[], vendas_em_aberto=[], internas=[])
        for alocacao in alocacoes:
            lado_op = alocacao.lado_operacao
            outro_lado_abertas = (
                resultado.vendas_em_aberto
                if lado_op == "C"
                else resultado.compras_em_aberto
            )
            mesmo_lado_abertas = (
                resultado.vendas_em_aberto
                if lado_op == "V"
                else resultado.compras_em_aberto
            )

            indice_da_operacao_compativel = -1
            # Para todas as operações da ponta contrária
            for i, alocacao_candidata_a_outra_ponta in enumerate(outro_lado_abertas):
                if (
                    # Mesmo ativo, quantidade, data de liquidação e corretora
                    alocacao.id_ativo.codigo
                    == alocacao_candidata_a_outra_ponta.id_ativo.codigo
                    and alocacao.quantidade
                    == alocacao_candidata_a_outra_ponta.quantidade
                    and alocacao.data_liquidacao
                    == alocacao_candidata_a_outra_ponta.data_liquidacao
                    and alocacao.id_corretora.valor
                    == alocacao_candidata_a_outra_ponta.id_corretora.valor
                    # Preço de compra precisa ser maior que o de venda (pagamento de corretagem)
                    and {
                        "C": (alocacao.preco > alocacao_candidata_a_outra_ponta.preco),
                        "V": (alocacao.preco < alocacao_candidata_a_outra_ponta.preco),
                    }[lado_op]
                    # Não pode ser para o mesmo fundo
                    and alocacao.id_fundo.valor
                    != alocacao_candidata_a_outra_ponta.id_fundo.valor
                ):
                    indice_da_operacao_compativel = i
                    break

            if indice_da_operacao_compativel != -1:
                operacao_compativel = outro_lado_abertas.pop(
                    indice_da_operacao_compativel
                )
                compra = alocacao if lado_op == "C" else operacao_compativel
                venda = alocacao if lado_op == "V" else operacao_compativel
                resultado.internas.append(Interna(compra=compra, venda=venda))
            else:
                mesmo_lado_abertas.append(alocacao)

        return resultado

    def _hash_tipo_boleta(
        self, a: AlocacaoSchema, tipo: TipoOperacao, mercado: Mercado | None
    ):
        return f"{a.id_ativo.tipo_ativo}-{a.id_corretora.valor}-{tipo}-{mercado}"

    def _criar_boleta_a_partir_de_caracteristicas(
        self,
        id: int,
        alocacao: AlocacaoSchema,
        tipo: TipoOperacao,
        mercado: Mercado | None,
    ):
        return SugestaoBoleta(
            id=id,
            alocacoes=[],
            horario=datetime.now(),
            tipo=tipo,
            mercado=mercado,
            corretora=alocacao.id_corretora.valor,
            tipo_ativo=alocacao.id_ativo.tipo_ativo,
            data_liquidacao=alocacao.data_liquidacao,
        )

    def _sugestao_boletas(
        self, alocacoes: list[AlocacaoSchema]
    ) -> list[SugestaoBoleta]:
        internas_e_sem_pontas = self._identificar_internas(alocacoes)
        boletas: dict[str, SugestaoBoleta] = {}
        id = -1
        tipo = "INTERNA"
        mercado = "SECUNDARIO"
        for interna in internas_e_sem_pontas.internas:
            hash = self._hash_tipo_boleta(interna.compra, tipo, mercado)
            if hash not in boletas:
                boletas[hash] = self._criar_boleta_a_partir_de_caracteristicas(
                    id, interna.compra, tipo, mercado
                )
            boletas[hash].alocacoes.append(interna.compra)
            boletas[hash].alocacoes.append(interna.venda)
        tipo = "EXTERNA"
        mercado = "SECUNDARIO"
        for venda in internas_e_sem_pontas.vendas_em_aberto:
            hash = self._hash_tipo_boleta(venda, tipo, mercado)
            if hash not in boletas:
                boletas[hash] = self._criar_boleta_a_partir_de_caracteristicas(
                    id, venda, tipo, mercado
                )
            boletas[hash].alocacoes.append(venda)
        tipo = "EXTERNA"
        mercado = None
        for compra in internas_e_sem_pontas.compras_em_aberto:
            hash = self._hash_tipo_boleta(compra, tipo, mercado)
            if hash not in boletas:
                boletas[hash] = self._criar_boleta_a_partir_de_caracteristicas(
                    id, compra, tipo, mercado
                )
            boletas[hash].alocacoes.append(compra)
        return [*boletas.values()]

    async def buscar_corretoras(self, corretoras: list[IdentificadorCorretora]):
        return await self.operacoes_repository.buscar_corretoras(corretoras)

    @staticmethod
    def eh_fluxoII(tipo_ativo_id: int, mercado_id: int):
        try:
            return (
                TipoAtivo.ID(tipo_ativo_id)
                in {
                    TipoAtivo.ID.Debênture,
                    TipoAtivo.ID.CRI,
                    TipoAtivo.ID.CRA,
                    TipoAtivo.ID.FIDC,
                }
                and MercadoNegociado.ID(mercado_id) == MercadoNegociado.ID.SECUNDARIO
            )
        except:
            return False

    async def criar_alocacoes(self, boleta: BoletaSchema, usuario: Usuario):
        for alocacao in boleta.alocacoes:
            if alocacao.id_ativo.tipo_codigo != "TICKER":
                raise HTTPException(
                    HTTPStatus.UNPROCESSABLE_ENTITY,
                    "Criação de alocações só suporta identificação de ativos por ticker.",
                )
            if alocacao.id_fundo.tipo != "CETIP":
                raise HTTPException(
                    HTTPStatus.UNPROCESSABLE_ENTITY,
                    "Criação de alocações só suporta identificação de fundos por conta CETIP.",
                )
        async with self.operacoes_repository.db.begin_nested():
            corretoras = await self.operacoes_repository.buscar_corretoras(
                [
                    IdentificadorCorretora(
                        tipo="APELIDO_VANGUARDA", valor=boleta.corretora
                    )
                ]
            )
            if len(corretoras) != 1:
                raise HTTPException(HTTPStatus.NOT_FOUND, "Corretora não encontrada")
            [corretora] = corretoras

            fundos = await self.fundos_repository.buscar_fundos(
                [alocacao.id_fundo for alocacao in boleta.alocacoes]
            )
            cetip_para_id_fundo = {
                fundo.conta_cetip.strip().replace(".", "").replace("-", ""): fundo.id
                for fundo in fundos
                if fundo.conta_cetip
            }

            if boleta.id <= 0:
                try:
                    m_id = MercadoNegociado.ID[boleta.mercado]
                except:
                    raise HTTPException(HTTPStatus.NOT_FOUND, "Mercado não encontrado")
                try:
                    n_id = NaturezaOperacao.ID[boleta.tipo]
                except:
                    raise HTTPException(
                        HTTPStatus.NOT_FOUND, "Natureza da operação não encontrada"
                    )
                try:
                    t_id = TipoAtivo.ID[boleta.tipo_ativo]
                except:
                    raise HTTPException(
                        HTTPStatus.NOT_FOUND, "Tipo de ativo não encontrado"
                    )
                [id_boleta] = await self.operacoes_repository.criar_boletas(
                    [
                        CriarBoleta(
                            data_negociacao=date.today(),
                            data_liquidacao=date.today(),
                            corretora_id=corretora.id,
                            mercado_negociado_id=m_id.value,
                            natureza_operacao_id=n_id.value,
                            tipo_ativo_id=t_id.value,
                        )
                    ]
                )
            else:
                id_boleta = boleta.id

            ids_alocacoes = await self.operacoes_repository.criar_alocacoes(
                [
                    CriarAlocacao(
                        codigo_ativo=alocacao.id_ativo.codigo,
                        alocacao_anterior_id=None,
                        alocacao_usuario_id=usuario.id,
                        alocado_em=datetime.now(),
                        aprovacao_usuario_id=None,
                        aprovado_em=None,
                        boleta_id=id_boleta,
                        fundo_id=cetip_para_id_fundo[
                            alocacao.id_fundo.valor.strip()
                            .replace(".", "")
                            .replace("-", "")
                        ],
                        preco_unitario=Decimal(alocacao.preco),
                        quantidade=Decimal(alocacao.quantidade),
                        tipo_ativo_id=t_id.value,
                        vanguarda_compra=alocacao.lado_operacao == "C",
                        corretora_id=corretora.id,
                        data_liquidacao=alocacao.data_liquidacao,
                        data_negociacao=date.today(),
                    )
                    for alocacao in boleta.alocacoes
                ]
            )
            for i, id in enumerate(ids_alocacoes):
                boleta.alocacoes[i].id = id

        [nova_boleta] = await self.operacoes_repository.buscar_boletas(
            ids_boletas=[id_boleta]
        )

        await WebSocketService.send_json(
            {
                "canal": "operacoes.alocacao",
                "tipo": "alocacao.nova",
                "dados": nova_boleta,
                "client_request_id": boleta.client_id,
            }
        )
        await self.email_service.enviar(
            [usuario.email],
            "[SISTEMA] Novas alocações",
            EmailTemplateSchema(
                titulo=f"Novas alocações",
                conteudo_html=EmailAlocacoesSchema(
                    fluxoII=OperacoesService.eh_fluxoII(
                        nova_boleta.tipo_ativo_id, nova_boleta.mercado_negociado_id
                    ),
                    boleta=nova_boleta,
                    usuario=usuario.nome,
                    acao="enviou novas alocações para aprovação no sistema",
                ).html(),
            ).html(),
            ["backoffice@icatuvanguarda.com.br", "grupomesacp@icatuvanguarda.com.br"],
        )

    async def transmitir_boletas_ws(self, usuario: Usuario):
        boletas = await self.operacoes_repository.buscar_boletas(
            data_liquidacao=date.today()
        )
        await WebSocketService.send_json(
            {
                "canal": "operacoes.alocacao",
                "tipo": "alocacao.todas",
                "dados": boletas,
            },
            user_ids=[usuario.id],
        )

    async def aprovar_alocacoes(self, usuario: Usuario, ids_alocacoes: list[int]):
        def falha(motivo: str):
            return WebSocketService.notify(
                [usuario.id], text=f"Nenhuma alocação foi aprovada. Motivo: {motivo}"
            )

        async with self.operacoes_repository.db.begin_nested():
            alocacoes = await self.operacoes_repository.alocacoes(ids_alocacoes)
            alocacoes_canceladas = [
                alocacao for alocacao in alocacoes if alocacao.cancelamento != None
            ]
            if alocacoes_canceladas:
                return await falha(
                    f"{len(alocacoes_canceladas)} das {len(ids_alocacoes)} alocações selecionadas foram canceladas."
                )
            alocacoes_ja_aprovadas = [
                alocacao for alocacao in alocacoes if alocacao.aprovado_em
            ]
            if alocacoes_ja_aprovadas:
                return await falha(
                    f"{len(alocacoes_ja_aprovadas)} das {len(ids_alocacoes)} alocações selecionadas já foram aprovadas."
                )
            await self.operacoes_repository.aprovar_alocacoes(usuario.id, ids_alocacoes)

            messages: list[Coroutine] = []
            ids_boletas: set[int] = set()
            ids_alocacoes_aprovadas: set[int] = set()
            for alocacao in alocacoes:
                messages.append(
                    WebSocketService.send_json(
                        {
                            "canal": "operacoes.alocacao",
                            "tipo": "alocacao.aprovacao",
                            "dados": {
                                "alocacao_id": alocacao.id,
                                "aprovado_em": datetime.now().isoformat(),
                                "aprovado_por": usuario.nome,
                            },
                        }
                    )
                )
                ids_alocacoes_aprovadas.add(alocacao.id)
                ids_boletas.add(alocacao.boleta.id)

            boletas = await self.operacoes_repository.buscar_boletas(
                data_liquidacao=date.today(), ids_boletas=[*ids_boletas]
            )

            for boleta in boletas:
                boleta.alocacoes = [
                    alocacao
                    for alocacao in boleta.alocacoes
                    if alocacao.id in ids_alocacoes_aprovadas
                ]
                messages.append(
                    self.email_service.enviar(
                        [usuario.email],
                        "[SISTEMA] Alocações aprovadas",
                        EmailTemplateSchema(
                            titulo=f"Alocações aprovadas",
                            conteudo_html=EmailAlocacoesSchema(
                                fluxoII=OperacoesService.eh_fluxoII(
                                    boleta.tipo_ativo_id,
                                    boleta.mercado_negociado_id,
                                ),
                                boleta=boleta,
                                usuario=usuario.nome,
                                acao="aprovou as seguintes alocações no sistema",
                            ).html(),
                        ).html(),
                        [
                            "backoffice@icatuvanguarda.com.br",
                            "grupomesacp@icatuvanguarda.com.br",
                        ],
                    )
                )
            if messages:
                await asyncio.gather(*messages)
            casamentos = await self.b3_service.casar_voices_e_alocacoes(
                usuario, ids_boletas=[*ids_boletas]
            )
            for voice_id in casamentos:
                await self.b3_service.enviar_casamentos_pendentes_para_b3_caso_existam(
                    usuario, voice_id
                )

    async def alocar_administrador(self, usuario: Usuario, ids_alocacoes: list[int]):
        def falha(motivo: str):
            return WebSocketService.notify(
                [usuario.id],
                text=f"Nenhuma alocação foi enviada para o administrador. Motivo: {motivo}",
            )

        async with self.operacoes_repository.db.begin_nested():
            alocacoes = await self.operacoes_repository.alocacoes(ids_alocacoes)
            alocacoes_ja_canceladas = [
                alocacao for alocacao in alocacoes if alocacao.cancelamento != None
            ]
            if alocacoes_ja_canceladas:
                return await falha(
                    f"{len(alocacoes_ja_canceladas)} das {len(ids_alocacoes)} alocações selecionadas foram canceladas."
                )
            alocacoes_nao_aprovadas = [
                alocacao for alocacao in alocacoes if alocacao.aprovado_em == None
            ]
            if alocacoes_nao_aprovadas:
                return await falha(
                    f"{len(alocacoes_nao_aprovadas)} das {len(ids_alocacoes)} alocações selecionadas ainda estão em triagem."
                )
            alocacoes_ja_enviadas_para_administrador = [
                alocacao
                for alocacao in alocacoes
                if alocacao.alocacao_administrador != None
            ]
            if alocacoes_ja_enviadas_para_administrador:
                return await falha(
                    f"{len(alocacoes_ja_enviadas_para_administrador)} das {len(ids_alocacoes)} alocações selecionadas já foram enviadas para o administrador."
                )
            alocacoes_com_fundos_sem_administrador = [
                alocacao
                for alocacao in alocacoes
                if alocacao.fundo.fundo_administrador_id == None
            ]
            if alocacoes_com_fundos_sem_administrador:
                return await falha(
                    f"{len(alocacoes_com_fundos_sem_administrador)} das {len(ids_alocacoes)} alocações selecionadas não possuem um fundo com um administrador registrado no sistema."
                )
            await self.operacoes_repository.alocar_administrador(
                usuario.id, ids_alocacoes
            )

        messages: list[Coroutine] = []
        for id in ids_alocacoes:
            messages.append(
                WebSocketService.send_json(
                    {
                        "canal": "operacoes.alocacao",
                        "tipo": "alocacao.nova.administrador",
                        "dados": {
                            "alocacao_id": id,
                            "alocado_em": datetime.now().isoformat(),
                            "codigo_administrador": None,
                            "alocacao_usuario_id": usuario.id,
                        },
                    }
                )
            )
        if messages:
            await asyncio.gather(*messages)

    async def cancelar_alocacoes(
        self, usuario: Usuario, ids_alocacoes: list[int], motivo: str | None = None
    ):
        def falha(motivo: str):
            return WebSocketService.notify(
                [usuario.id], text=f"Nenhuma alocação foi cancelada. Motivo: {motivo}"
            )

        async with self.operacoes_repository.db.begin_nested():
            alocacoes = await self.operacoes_repository.alocacoes(ids_alocacoes)
            alocacoes_ja_canceladas = [
                alocacao for alocacao in alocacoes if alocacao.cancelamento != None
            ]
            if alocacoes_ja_canceladas:
                return await falha(
                    f"{len(alocacoes_ja_canceladas)} das {len(ids_alocacoes)} alocações selecionadas já se encontram canceladas."
                )

            await self.operacoes_repository.cancelar_alocacoes(
                usuario.id, ids_alocacoes, motivo
            )

            ids_alocacoes_aprovadas = {alocacao.id for alocacao in alocacoes}
            ids_boletas = {alocacao.boleta.id for alocacao in alocacoes}

            messages: list[Coroutine] = []
            for id in ids_alocacoes:
                messages.append(
                    WebSocketService.send_json(
                        {
                            "canal": "operacoes.alocacao",
                            "tipo": "alocacao.cancelamento",
                            "dados": {
                                "alocacao_id": id,
                                "motivo": motivo,
                                "cancelado_em": datetime.now().isoformat(),
                                "usuario_id": usuario.id,
                            },
                        }
                    )
                )

            boletas = await self.operacoes_repository.buscar_boletas(
                data_liquidacao=date.today(), ids_boletas=[*ids_boletas]
            )
            for boleta in boletas:
                boleta.alocacoes = [
                    alocacao
                    for alocacao in boleta.alocacoes
                    if alocacao.id in ids_alocacoes_aprovadas
                ]
                messages.append(
                    self.email_service.enviar(
                        [usuario.email],
                        "[SISTEMA] Solicitação de cancelamento",
                        EmailTemplateSchema(
                            titulo=f"Solicitação de cancelamento",
                            conteudo_html=EmailAlocacoesSchema(
                                fluxoII=OperacoesService.eh_fluxoII(
                                    boleta.tipo_ativo_id,
                                    boleta.mercado_negociado_id,
                                ),
                                boleta=boleta,
                                usuario=usuario.nome,
                                acao=f"solicitou o <b style='color: red'>cancelamento</b> das seguintes alocações. <b style='color: red'>Motivo: {motivo or 'não informado'}</b>",
                            ).html(),
                        ).html(),
                        [
                            "backoffice@icatuvanguarda.com.br",
                            "grupomesacp@icatuvanguarda.com.br",
                        ],
                    )
                )
            if messages:
                await asyncio.gather(*messages)

    async def cancelar_alocacoes_administrador(
        self, usuario: Usuario, ids_alocacoes: list[int], motivo: str | None = None
    ):
        def falha(motivo: str):
            return WebSocketService.notify(
                [usuario.id],
                text=f"Nenhuma alocação foi cancelada no administrador. Motivo: {motivo}",
            )

        async with self.operacoes_repository.db.begin_nested():
            alocacoes = await self.operacoes_repository.alocacoes(ids_alocacoes)
            alocacoes_nao_alocadas_no_administrador = [
                alocacao
                for alocacao in alocacoes
                if alocacao.alocacao_administrador == None
            ]
            if alocacoes_nao_alocadas_no_administrador:
                return await falha(
                    f"{len(alocacoes_nao_alocadas_no_administrador)} das {len(ids_alocacoes)} alocações selecionadas não foram alocadas no administrador."
                )
            alocacoes_ja_canceladas_no_administrador = [
                alocacao
                for alocacao in alocacoes
                if alocacao.alocacao_administrador
                and alocacao.alocacao_administrador.cancelamento != None
            ]
            if alocacoes_ja_canceladas_no_administrador:
                return await falha(
                    f"{len(alocacoes_ja_canceladas_no_administrador)} das {len(ids_alocacoes)} alocações selecionadas já se encontram canceladas no administrador."
                )

            await self.operacoes_repository.cancelar_alocacoes_administrador(
                usuario.id, ids_alocacoes, motivo
            )

        messages: list[Coroutine] = []
        for id in ids_alocacoes:
            messages.append(
                WebSocketService.send_json(
                    {
                        "canal": "operacoes.alocacao",
                        "tipo": "alocacao.cancelamento.administrador",
                        "dados": {
                            "alocacao_administrador_id": id,
                            "motivo": motivo,
                            "cancelado_em": datetime.now().isoformat(),
                            "usuario_id": usuario.id,
                        },
                    }
                )
            )
        if messages:
            await asyncio.gather(*messages)

    async def sinalizar_liquidacao(self, usuario: Usuario, ids_alocacoes: list[int]):
        def falha(motivo: str):
            return WebSocketService.notify(
                [usuario.id],
                text=f"Nenhuma alocação foi marcada como liquidada. Motivo: {motivo}",
            )

        async with self.operacoes_repository.db.begin_nested():
            alocacoes = await self.operacoes_repository.alocacoes(ids_alocacoes)
            alocacoes_nao_aprovadas = [
                alocacao for alocacao in alocacoes if alocacao.aprovado_em == None
            ]
            if alocacoes_nao_aprovadas:
                return await falha(
                    f"{len(alocacoes_nao_aprovadas)} das {len(ids_alocacoes)} alocações selecionadas ainda não foram aprovadas."
                )
            alocacoes_nao_enviadas_para_adm = [
                alocacao
                for alocacao in alocacoes
                if alocacao.alocacao_administrador == None
            ]
            if alocacoes_nao_enviadas_para_adm:
                return await falha(
                    f"{len(alocacoes_nao_enviadas_para_adm)} das {len(ids_alocacoes)} alocações selecionadas ainda não foram enviadas para o administrador."
                )
            alocacoes_ja_liquidadas = [
                alocacao
                for alocacao in alocacoes
                if alocacao.alocacao_administrador
                and alocacao.alocacao_administrador.liquidacao
            ]
            if alocacoes_ja_liquidadas:
                return await falha(
                    f"{len(alocacoes_ja_liquidadas)} das {len(ids_alocacoes)} alocações selecionadas já se encontram liquidadas."
                )

            await self.operacoes_repository.sinalizar_liquidacao(
                usuario.id, ids_alocacoes
            )

        messages: list[Coroutine] = []
        for id in ids_alocacoes:
            messages.append(
                WebSocketService.send_json(
                    {
                        "canal": "operacoes.alocacao",
                        "tipo": "alocacao.liquidacao",
                        "dados": {
                            "alocacao_administrador_id": id,
                            "liquidado_em": datetime.now().isoformat(),
                            "usuario_id": usuario.id,
                        },
                    }
                )
            )
        if messages:
            await asyncio.gather(*messages)
