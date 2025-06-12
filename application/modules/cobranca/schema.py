from datetime import date, datetime
from decimal import Decimal
from enum import IntEnum
from re import sub
from unidecode import unidecode
from uuid import uuid4

from pydantic import BaseModel as Schema

from .model import ContratoLocacao, DadosExecucaoDaycoval, ExecucaoDaycoval, Inquilino, PassoExecucaoDaycoval


class SolicitacaoBoletoSchema(Schema):
    contrato_id: int
    valor: Decimal
    vencimento: date
    percentual_juros_mora_ao_mes: Decimal
    percentual_sobre_valor_multa_mora: Decimal


class ArquivoRemessa(Schema):
    solicitacao: SolicitacaoBoletoSchema
    id_titulo: str
    id_cobranca: str
    conteudo: str


class TipoMultaDaycovalEnum(IntEnum):
    ISENTO = 0
    FIXA = 1
    PERCENTUAL = 2


class ExecucaoStatus(IntEnum):
    AGUARDANDO = 0
    EM_ANDAMENTO = 1
    CONCLUIDO = 2
    ERRO = 3

ID_GRUL11_DAYCOVAL = "00881738300011937994"
NOME_GRUL11_DAYCOVAL = "ICATU VAN GRU LOG FII RL"
CNPJ_GRUL11_DAYCOVAL = "54.483.412/0001-59"

class CNAB400Remessa(Schema):
    id_empresa_no_banco: str = ID_GRUL11_DAYCOVAL
    nome_empresa_no_banco: str = NOME_GRUL11_DAYCOVAL
    cnpj_empresa_cobradora: str = CNPJ_GRUL11_DAYCOVAL
    data_emissao: date
    vencimento: date
    tipo_multa: TipoMultaDaycovalEnum
    valor_ou_taxa_multa: Decimal
    valor_mora_por_dia_de_atraso: Decimal
    dias_apos_vencimento_para_aplicar_multa: int
    valor: Decimal
    cnpj_empresa_cobrada: str
    nome_empresa_cobrada: str
    logradouro_empresa_cobrada: str
    bairro_empresa_cobrada: str
    cep_empresa_cobrada: str
    cidade_empresa_cobrada: str
    uf_empresa_cobrada: str

    def gerar(self, id_titulo_vanguarda: str, numero_doc_cobranca: str):
        """
        Gera arquivo de remessa no formato CNAB400.

        Wiki: Serviços Externos > Boletos Daycoval > Layout arquivo de remessa Daycoval
        """
        header = [
            "0",
            "1",
            "REMESSA",
            "01",
            "COBRANCA".ljust(15),
            self.id_empresa_no_banco[:20].ljust(20),
            unidecode(self.nome_empresa_no_banco[:30].ljust(30)),
            "707",
            "BANCO DAYCOVAL".ljust(15),
            self.data_emissao.strftime("%d%m%y"),
            " " * 294,
            "000001",
        ]
        registro = [
            "1",
            "02",
            sub("[^0-9]", "", self.cnpj_empresa_cobradora)[:14],
            self.id_empresa_no_banco[:20].ljust(20),
            id_titulo_vanguarda,
            "0" * 11,
            " " * 13,
            "   ",
            str(self.tipo_multa),
            sub(
                "[^0-9]",
                "",
                str(
                    Decimal(0)
                    if self.tipo_multa == "ISENTO"
                    else self.valor_ou_taxa_multa.quantize(
                        Decimal(".01")
                        if self.tipo_multa == "FIXA"
                        else Decimal(".0001")
                    )
                ),
            ).rjust(13, "0"),
            str(self.dias_apos_vencimento_para_aplicar_multa).rjust(2, "0"),
            "  ",
            "5",
            "01",
            numero_doc_cobranca,
            self.vencimento.strftime("%d%m%y"),
            sub("[^0-9]", "", str(self.valor.quantize(Decimal(".01")))).rjust(13, "0"),
            "707",
            "0000",
            "0",
            "99",
            "A",
            self.data_emissao.strftime("%d%m%y"),
            "10",
            "10",
            sub(
                "[^0-9]",
                "",
                str(self.valor_mora_por_dia_de_atraso.quantize(Decimal(".01"))),
            ).rjust(13, "0"),
            "0" * 6,
            "0" * 13,
            "0" * 13,
            "0" * 13,
            "02",
            sub("[^0-9]", "", self.cnpj_empresa_cobrada)[:14].ljust(14),
            unidecode(self.nome_empresa_cobrada[:30].ljust(30)),
            " " * 10,
            unidecode(self.logradouro_empresa_cobrada[:40].ljust(40)),
            unidecode(self.bairro_empresa_cobrada[:12].ljust(12)),
            sub("[^0-9]", "", self.cep_empresa_cobrada)[:8].ljust(8),
            unidecode(self.cidade_empresa_cobrada[:15].ljust(15)),
            unidecode(self.uf_empresa_cobrada[:2].ljust(2)),
            unidecode(self.nome_empresa_no_banco[:30].ljust(30)),
            " " * 4,
            " " * 6,
            "00",
            "0",
            "000002",
        ]
        trailer = ["9", " " * 393, "000003"]
        cnab400 = "\n".join(["".join(secao) for secao in [header, registro, trailer]])
        return cnab400


class ExecucaoSchema(Schema):
    id: int
    id_usuario: int
    nome_usuario: str
    solicitado_em: datetime


class TipoExecucaoDaycovalSchema(Schema):
    id: int
    nome: str


class DadosExecucaoDaycovalSchema(Schema):
    id: int
    identificador_titulo: str
    identificador_documento_cobranca: str
    vencimento: date
    valor: float
    percentual_juros_mora_ao_mes: float
    percentual_sobre_valor_multa_mora: float
    conteudo_arquivo_remessa: str | None = None
    nome_arquivo_remessa: str | None = None
    nome_arquivo_retorno: str | None = None
    arquivo_id_boleto_parcial_pdf: str | None = None
    conteudo_arquivo_retorno: str | None = None
    arquivo_id_boleto_completo_pdf: str | None = None
    contrato_id: int
    execucao_daycoval_id: int

    @staticmethod
    def from_model(dado: DadosExecucaoDaycoval):
        return DadosExecucaoDaycovalSchema(
            id=dado.id,
            identificador_titulo=dado.identificador_titulo,
            identificador_documento_cobranca=dado.identificador_documento_cobranca,
            vencimento=dado.vencimento,
            valor=dado.valor,
            percentual_juros_mora_ao_mes=dado.percentual_juros_mora_ao_mes,
            percentual_sobre_valor_multa_mora=dado.percentual_sobre_valor_multa_mora,
            conteudo_arquivo_remessa=dado.conteudo_arquivo_remessa,
            nome_arquivo_remessa=dado.nome_arquivo_remessa,
            nome_arquivo_retorno=dado.nome_arquivo_retorno,
            arquivo_id_boleto_parcial_pdf=dado.arquivo_id_boleto_parcial_pdf,
            conteudo_arquivo_retorno=dado.conteudo_arquivo_retorno,
            arquivo_id_boleto_completo_pdf=dado.arquivo_id_boleto_completo_pdf,
            contrato_id=dado.contrato_id,
            execucao_daycoval_id=dado.execucao_daycoval_id
        )
    
    def html_cobranca(self):
        def fmt(n: float):
            return f'{n:,.2f}'.replace(',','_').replace('.',',').replace('_','.')
        
        return f"""
            <b>Em caso de pagamento após a data de vencimento, haverá um acréscimo no valor de acordo com as seguintes regras (cumulativo):</b>
            <ul>
                <li>
                    - Multa única de <b>R$ {fmt(round(self.percentual_sobre_valor_multa_mora*self.valor/100, 2))}</b> ({fmt(self.percentual_sobre_valor_multa_mora)}% do valor total)
                </li>
                <li>
                    - Juros de <b>R$ {fmt(round(self.percentual_juros_mora_ao_mes*self.valor/100/30, 2))}</b> por dia de atraso (equivalente a {fmt(self.percentual_juros_mora_ao_mes)}% do valor total ao mês)
                </li>
            </ul>
        """


class PassoExecucaoDaycovalSchema(Schema):
    id: int
    nome: str
    inicio: datetime
    fim: datetime | None = None
    erro: str | None = None
    execucao_daycoval_id: int

    @staticmethod
    def from_model(passo: PassoExecucaoDaycoval):
        return PassoExecucaoDaycovalSchema(
            id=passo.id,
            nome=passo.nome,
            inicio=passo.inicio,
            fim=passo.fim,
            erro=passo.erro,
            execucao_daycoval_id=passo.execucao_daycoval_id
        )


class ExecucaoDaycovalSchema(Schema):
    class Usuario(Schema):
        id: int
        email: str
        nome: str
    id: int
    tipo_execucao: TipoExecucaoDaycovalSchema
    inicio: datetime
    fim: datetime | None = None
    erro: str | None = None
    passos: list[PassoExecucaoDaycovalSchema]
    dados: list[DadosExecucaoDaycovalSchema]
    usuario: Usuario

    @staticmethod
    def from_model(execucao: ExecucaoDaycoval):
        return ExecucaoDaycovalSchema(
            id=execucao.id,
            tipo_execucao=TipoExecucaoDaycovalSchema(
                id=execucao.tipo_execucao.id,
                nome=execucao.tipo_execucao.nome
            ),
            inicio=execucao.inicio,
            fim=execucao.fim,
            erro=execucao.erro,
            passos=[
                PassoExecucaoDaycovalSchema.from_model(passo)
                for passo in execucao.passos
            ],
            dados=[
                DadosExecucaoDaycovalSchema.from_model(dado)
                for dado in execucao.dados
            ],
            usuario=ExecucaoDaycovalSchema.Usuario(
                id=execucao.usuario.id,
                nome=execucao.usuario.nome,
                email=execucao.usuario.email
            ),
        )
    
class BodyCriacaoDadosExecucaoDaycovalSchema(Schema):
    vencimento: date
    valor: float
    percentual_juros_mora_ao_mes: float
    percentual_sobre_valor_multa_mora: float
    contrato_id: int

class CriacaoDadosExecucaoDaycovalSchema(BodyCriacaoDadosExecucaoDaycovalSchema):
    identificador_titulo: str
    identificador_documento_cobranca: str

class FaixaMultaMoraSchema(Schema):
    contrato_locacao_id: int
    dias_a_partir_vencimento: int
    percentual_sobre_valor: float


class ContratoLocacaoSchema(Schema):
    id: int
    fundo_id: int
    inquilino_id: int
    dia_vencimento: int
    percentual_juros_mora_ao_mes: float
    faixas_cobranca_multa_mora: list[FaixaMultaMoraSchema]

    @staticmethod
    def from_model(contrato: ContratoLocacao):
        return ContratoLocacaoSchema(
            id=contrato.id,
            fundo_id=contrato.fundo_id,
            inquilino_id=contrato.inquilino_id,
            dia_vencimento=contrato.dia_vencimento,
            percentual_juros_mora_ao_mes=contrato.percentual_juros_mora_ao_mes,
            faixas_cobranca_multa_mora=[
                FaixaMultaMoraSchema(
                    contrato_locacao_id=faixa.contrato_locacao_id,
                    dias_a_partir_vencimento=faixa.dias_a_partir_vencimento,
                    percentual_sobre_valor=faixa.percentual_sobre_valor,
                )
                for faixa in contrato.faixas_cobranca_multa_mora
            ],
        )


class FundoInquilinoSchema(Schema):
    id: int
    razao_social: str
    cnpj: str
    cep: str
    logradouro: str
    bairro: str
    cidade: str
    estado: str
    contrato: ContratoLocacaoSchema

    @staticmethod
    def from_model(inquilino: Inquilino, fundo_id: int):
        contratos = [
            ContratoLocacaoSchema.from_model(contrato)
            for contrato in inquilino.contratos
            if contrato.fundo_id == fundo_id
        ]
        contrato: ContratoLocacaoSchema
        if not contratos:
            return None
        [contrato] = contratos
        return FundoInquilinoSchema(
            id=inquilino.id,
            razao_social=inquilino.razao_social,
            cnpj=inquilino.cnpj,
            cep=inquilino.cep,
            logradouro=inquilino.logradouro,
            bairro=inquilino.bairro,
            cidade=inquilino.cidade,
            estado=inquilino.estado,
            contrato=contrato,
        )
