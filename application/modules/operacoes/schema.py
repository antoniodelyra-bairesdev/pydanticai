from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel as Schema

from typing import Literal

from modules.fundos.model import Fundo, FundoAdministrador
from modules.fundos.schema import IdentificadorFundo

from modules.b3.schema import DetalhesRegistroNoMeSchema, CasamentoAlocacaoB3VoiceSchema
from modules.ativos.model import TipoAtivo
from modules.util.string import __ENTER__

from .model import (
    AlocacaoAdministrador,
    AlocacaoInterna,
    Boleta as ModelBoleta,
    CancelamentoAlocacaoAdministrador,
    CancelamentoAlocacaoInterna,
    Corretora,
    LiquidacaoAlocacaoAdministrador,
)

Mercado = Literal["PRIMARIO", "SECUNDARIO"]
TipoOperacao = Literal["EXTERNA", "INTERNA"]
TipoTitulo = Literal[
    "BOND",
    "CDB",
    "CRA",
    "CRI",
    "Debênture",
    "DPGE",
    "FIDC",
    "FII",
    "LF",
    "LFS",
    "LFSC",
    "LFSN",
    "NC",
    "RDB",
]


class IdentificadorAtivo(Schema):
    tipo_ativo: TipoTitulo
    tipo_codigo: Literal["ISIN", "TICKER"]
    codigo: str


TipoIdentificadorCorretora = Literal[
    "APELIDO_VANGUARDA",
    "NOME_INSTITUICAO",
    "NOME_DESK",
    "NOME_USUARIO",
    "ID_INSTITUICAO",
    "ID_DESK",
    "ID_USUARIO",
]


class IdentificadorCorretora(Schema):
    tipo: TipoIdentificadorCorretora
    valor: str


class AlocacaoSchema(Schema):
    id: int
    id_fundo: IdentificadorFundo
    id_ativo: IdentificadorAtivo
    id_corretora: IdentificadorCorretora
    lado_operacao: Literal["C", "V"]
    data_liquidacao: date
    preco: float
    quantidade: float
    horario: datetime


class SugestaoBoleta(Schema):
    client_id: int | float | None = None
    id: int
    mercado: Mercado | None
    tipo: TipoOperacao
    horario: datetime
    tipo_ativo: TipoTitulo
    corretora: str
    alocacoes: list[AlocacaoSchema]
    data_liquidacao: date


class BoletaSchema(SugestaoBoleta):
    mercado: Mercado


class Interna(Schema):
    compra: AlocacaoSchema
    venda: AlocacaoSchema


class ResultadoBuscaBoleta_Corretora(Schema):
    id: int
    nome: str

    @staticmethod
    def from_model(corretora: Corretora):
        return ResultadoBuscaBoleta_Corretora(id=corretora.id, nome=corretora.nome)


class ResultadoBuscaBoleta_Administrador(Schema):
    id: int
    nome: str

    @staticmethod
    def from_model(administrador: FundoAdministrador):
        return ResultadoBuscaBoleta_Administrador(
            id=administrador.id, nome=administrador.nome
        )


class ResultadoBuscaBoleta_Fundo(Schema):
    id: int
    nome: str
    cnpj: str
    conta_cetip: str
    administrador: ResultadoBuscaBoleta_Administrador | None

    @staticmethod
    def from_model(fundo: Fundo):
        return ResultadoBuscaBoleta_Fundo(
            id=fundo.id,
            nome=fundo.nome,
            cnpj=fundo.cnpj,
            conta_cetip=fundo.conta_cetip or "",
            administrador=(
                ResultadoBuscaBoleta_Administrador.from_model(fundo.administrador)
                if fundo.administrador
                else None
            ),
        )


class ResultadoBuscaBoleta_CancelamentoAdministrador(Schema):
    alocacao_administrador_id: int
    cancelado_em: datetime
    motivo: str | None = None
    usuario_id: int

    @staticmethod
    def from_model(cancelamento: CancelamentoAlocacaoAdministrador):
        return ResultadoBuscaBoleta_CancelamentoAdministrador(
            alocacao_administrador_id=cancelamento.alocacao_administrador_id,
            cancelado_em=cancelamento.cancelado_em,
            motivo=cancelamento.motivo,
            usuario_id=cancelamento.usuario_id,
        )


class ResultadoBuscaBoleta_Liquidacao(Schema):
    alocacao_administrador_id: int
    liquidado_em: datetime
    usuario_id: int

    @staticmethod
    def from_model(liquidacao: LiquidacaoAlocacaoAdministrador):
        return ResultadoBuscaBoleta_Liquidacao(
            alocacao_administrador_id=liquidacao.alocacao_administrador_id,
            liquidado_em=liquidacao.liquidado_em,
            usuario_id=liquidacao.usuario_id,
        )


class ResultadoBuscaBoleta_AlocacaoAdministrador(Schema):
    alocacao_id: int
    alocacao_usuario_id: int
    alocado_em: datetime
    codigo_administrador: str | None
    cancelamento: ResultadoBuscaBoleta_CancelamentoAdministrador | None
    liquidacao: ResultadoBuscaBoleta_Liquidacao | None

    @staticmethod
    def from_model(al_adm: AlocacaoAdministrador):
        return ResultadoBuscaBoleta_AlocacaoAdministrador(
            alocacao_id=al_adm.alocacao_id,
            alocado_em=al_adm.alocado_em,
            alocacao_usuario_id=al_adm.alocacao_usuario_id,
            codigo_administrador=al_adm.codigo_administrador,
            cancelamento=(
                ResultadoBuscaBoleta_CancelamentoAdministrador.from_model(
                    al_adm.cancelamento
                )
                if al_adm.cancelamento
                else None
            ),
            liquidacao=(
                ResultadoBuscaBoleta_Liquidacao.from_model(al_adm.liquidacao)
                if al_adm.liquidacao
                else None
            ),
        )


class ResultadoBuscaBoleta_Cancelamento(Schema):
    alocacao_id: int
    cancelado_em: datetime
    motivo: str | None = None
    usuario_id: int

    @staticmethod
    def from_model(cancelamento: CancelamentoAlocacaoInterna):
        return ResultadoBuscaBoleta_Cancelamento(
            alocacao_id=cancelamento.alocacao_id,
            cancelado_em=cancelamento.cancelado_em,
            motivo=cancelamento.motivo,
            usuario_id=cancelamento.usuario_id,
        )


class ResultadoBuscaBoleta_Alocacao(Schema):
    id: int
    codigo_ativo: str
    vanguarda_compra: bool
    preco_unitario: Decimal
    quantidade: Decimal
    data_liquidacao: date
    data_negociacao: date
    alocado_em: datetime
    aprovado_em: datetime | None
    corretora_id: int
    alocacao_usuario: str
    aprovacao_usuario: str | None
    alocacao_anterior_id: int | None
    fundo: ResultadoBuscaBoleta_Fundo
    cancelamento: ResultadoBuscaBoleta_Cancelamento | None
    alocacao_administrador: ResultadoBuscaBoleta_AlocacaoAdministrador | None

    quebras: list["ResultadoBuscaBoleta_Alocacao"] = []
    registro_NoMe: DetalhesRegistroNoMeSchema | None = None
    casamento: CasamentoAlocacaoB3VoiceSchema | None = None

    @staticmethod
    def from_model(alocacao: AlocacaoInterna, quebra=False):
        return ResultadoBuscaBoleta_Alocacao(
            id=alocacao.id,
            codigo_ativo=alocacao.codigo_ativo,
            vanguarda_compra=alocacao.vanguarda_compra,
            preco_unitario=alocacao.preco_unitario,
            quantidade=alocacao.quantidade,
            data_negociacao=alocacao.data_negociacao,
            data_liquidacao=alocacao.data_negociacao,
            alocado_em=alocacao.alocado_em,
            aprovado_em=alocacao.aprovado_em,
            corretora_id=alocacao.corretora_id,
            alocacao_usuario=alocacao.alocacao_usuario.nome,
            aprovacao_usuario=(
                alocacao.aprovacao_usuario.nome if alocacao.aprovacao_usuario else None
            ),
            alocacao_anterior_id=alocacao.alocacao_anterior_id,
            cancelamento=(
                ResultadoBuscaBoleta_Cancelamento.from_model(alocacao.cancelamento)
                if alocacao.cancelamento
                else None
            ),
            alocacao_administrador=(
                ResultadoBuscaBoleta_AlocacaoAdministrador.from_model(
                    alocacao.alocacao_administrador
                )
                if alocacao.alocacao_administrador
                else None
            ),
            fundo=ResultadoBuscaBoleta_Fundo.from_model(alocacao.fundo),
            quebras=(
                []
                if quebra
                else [
                    ResultadoBuscaBoleta_Alocacao.from_model(quebra, True)
                    for quebra in alocacao.quebras
                ]
            ),
            registro_NoMe=(
                DetalhesRegistroNoMeSchema.from_model(alocacao.registro_NoMe)
                if alocacao.registro_NoMe
                else None
            ),
            casamento=(
                None
                if quebra
                else (
                    CasamentoAlocacaoB3VoiceSchema.from_model(
                        alocacao.pivot_casamento_voice.casamento
                    )
                    if alocacao.pivot_casamento_voice
                    and alocacao.pivot_casamento_voice.casamento
                    else None
                )
            ),
        )


class ResultadoBuscaBoleta(Schema):
    id: int
    data_liquidacao: date
    tipo_ativo_id: int
    natureza_operacao_id: int
    mercado_negociado_id: int
    corretora: ResultadoBuscaBoleta_Corretora
    alocacoes: list[ResultadoBuscaBoleta_Alocacao]

    @staticmethod
    def from_model(boleta: ModelBoleta):
        return ResultadoBuscaBoleta(
            id=boleta.id,
            data_liquidacao=boleta.data_liquidacao,
            tipo_ativo_id=boleta.tipo_ativo_id,
            natureza_operacao_id=boleta.natureza_operacao_id,
            mercado_negociado_id=boleta.mercado_negociado_id,
            corretora=ResultadoBuscaBoleta_Corretora.from_model(boleta.corretora),
            alocacoes=[
                ResultadoBuscaBoleta_Alocacao.from_model(alocacao)
                for alocacao in boleta.alocacoes
                if not alocacao.alocacao_anterior_id
            ],
        )


class EmailAlocacoesSchema(Schema):
    boleta: ResultadoBuscaBoleta
    usuario: str
    acao: str
    fluxoII: bool

    def html(self):
        return f"""
                <p>
                    <span style="color: #5ebb47"><b>{self.usuario}</b></span> {self.acao}.
                </p>
                <hr>
                <p>
                    <strong>
                        {'<span style="padding: 4px; border-radius: 4px; background-color: #0D6696; color: white; font-size: 11px; margin-right: 4px">[B]³ Fluxo II</span>' if self.fluxoII else ''} Boleta {self.boleta.id} - {TipoAtivo.ID(self.boleta.tipo_ativo_id).name} {self.boleta.corretora.nome} {date.today().strftime("%d/%m/%Y")}
                    </strong>
                </p>
                <table style="border-spacing: 8px; border-collapse: separate">
                    <thead style="background-color: #1B3157; color: white">
                        <tr>
                            <th>Fundo</th>
                            <th>Lado</th>
                            <th>Ativo</th>
                            <th>Quantidade</th>
                            <th>P.U.</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {__ENTER__.join([
                            f'''
                            <tr>
                                <td>{alocacao.fundo.nome}</td>
                                <td style="color: {'blue' if alocacao.vanguarda_compra else 'red'}">{'C' if alocacao.vanguarda_compra else 'V'}</td>
                                <td><b>{alocacao.codigo_ativo}</b></td>
                                <td>{'%.6f' % alocacao.quantidade}</td>
                                <td>R$ {'%.8f' % alocacao.preco_unitario}</td>
                                <td>R$ {'%.2f' % (alocacao.preco_unitario * alocacao.quantidade)}</td>
                            </tr>
                            '''
                            for alocacao in sorted(self.boleta.alocacoes, key=lambda x: x.id)
                        ])}
                    </tbody>
                </table>
                <hr>
                <p>
                    Para visualizar as alocações, acesse o painel de operações.
                    <a href="https://sistema.icatuvanguarda.com.br/operacoes">
                        Acessar
                    </a>
                </p>
                """
