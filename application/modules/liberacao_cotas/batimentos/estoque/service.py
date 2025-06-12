from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal
from pandas import DataFrame

from .schema import AtivoCarteiraSchema, ComparacaoEstoqueSchema, ResponseSchema
from modules.britech.estoque.types import (
    EstoqueBritechRendaFixa,
    EstoqueBritechRendaVariavel,
    EstoqueBritechFuturo,
    EstoqueBritechCota,
)

from modules.posicao.xml_anbima_401.service import XMLAnbima401Service
from modules.posicao.xml_anbima_401.types import XMLAnbima401Posicao, XMLAnbima401Fundo
from modules.posicao.xml_anbima_401.enums import Tags
from modules.posicao.xml_anbima_401.offshore.service import XMLAnbima401OffshoreService
from modules.posicao.xml_anbima_401.offshore.types import CodigosOpcao, CodigosFuturo
from modules.ativos.service import AtivosService
from modules.ativos.enums import SideOperacao
from modules.britech.estoque.service import BritechEstoqueService
from modules.calculos.service import CalculosService
from modules.caracteristicas_fundos.service import CaracteristicasFundosService
from modules.depara.cotas.service import DeparaCotasService
from modules.depara.cotas.types import LinhaDeparaCotaFundo
from modules.depara.offshore.ativo.service import DeParaOffshoreAtivoService
from modules.depara.offshore.ativo.types import DeParaLinhaOffshoreAtivo
from modules.util.temp_file import TempFileHelper
from modules.util.caracteristicas_fundos import CaractersticasFundosHelper
from modules.util.api_warning import APIWarning


class BatimentoEstoqueService:
    def get_batimento_estoque(
        self,
        usdbrl: float,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        nome_arq_xls_caracteristicas_fundos: str,
        nome_arq_xlsx_depara_cotas_fundos: str,
        nome_arq_xlsm_depara_derivativos: str,
        nome_arq_xlsx_estoque_renda_fixa: str,
        nome_arq_xlsx_estoque_renda_variavel: str,
        nome_arq_xlsx_estoque_futuro: str,
        nome_arq_xlsx_estoque_cota: str,
    ) -> ResponseSchema:
        buffer_caracteristicas_fundos: bytes = TempFileHelper.get_conteudo_e_deleta(
            nome_arq_xls_caracteristicas_fundos
        )
        buffer_depara_cotas_fundos: bytes = TempFileHelper.get_conteudo_e_deleta(
            nome_arq_xlsx_depara_cotas_fundos
        )
        buffer_depara_derivativos: bytes = TempFileHelper.get_conteudo_e_deleta(
            nome_arq_xlsm_depara_derivativos
        )
        buffer_estoque_renda_fixa: bytes = TempFileHelper.get_conteudo_e_deleta(
            nome_arq_xlsx_estoque_renda_fixa
        )
        buffer_estoque_renda_variavel: bytes = TempFileHelper.get_conteudo_e_deleta(
            nome_arq_xlsx_estoque_renda_variavel
        )
        buffer_estoque_futuro: bytes = TempFileHelper.get_conteudo_e_deleta(
            nome_arq_xlsx_estoque_futuro
        )
        buffer_estoque_cota: bytes = TempFileHelper.get_conteudo_e_deleta(
            nome_arq_xlsx_estoque_cota
        )

        dataframe_caracteristicas_fundos: DataFrame = (
            CaractersticasFundosHelper.get_dataframe_from_buffer(
                buffer_caracteristicas_fundos
            )
        )

        service_xml_anbima_401: XMLAnbima401Service = XMLAnbima401Service()
        service_xml_anbima_401_offshore: XMLAnbima401OffshoreService = (
            XMLAnbima401OffshoreService()
        )
        service_britech_estoque: BritechEstoqueService = BritechEstoqueService()
        service_caracteristicas_fundos: CaracteristicasFundosService = (
            CaracteristicasFundosService(
                dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos
            )
        )
        service_depara_cotas_fundos: DeparaCotasService = DeparaCotasService(
            buffer_xlsx_depara_cotas=buffer_depara_cotas_fundos
        )
        service_depara_offshore_ativo: DeParaOffshoreAtivoService = (
            DeParaOffshoreAtivoService(buffer_depara_derivativos)
        )

        estoque_renda_fixa: list[EstoqueBritechRendaFixa] = (
            service_britech_estoque.get_renda_fixa(buffer_estoque_renda_fixa)
        )
        estoque_renda_variavel: list[EstoqueBritechRendaVariavel] = (
            service_britech_estoque.get_renda_variavel(buffer_estoque_renda_variavel)
        )
        estoque_futuro: list[EstoqueBritechFuturo] = service_britech_estoque.get_futuro(
            buffer_estoque_futuro
        )
        estoque_cota: list[EstoqueBritechCota] = service_britech_estoque.get_cotas(
            buffer_estoque_cota
        )

        avisos: list[APIWarning] = []
        posicoes_anbima_401: list[XMLAnbima401Posicao] = []
        for i in range(0, len(nomes_arqs_xmls_anbima_401)):
            nome_arq: str = nomes_arqs_xmls_anbima_401[i][0]
            nome_arq_originial: str = nomes_arqs_xmls_anbima_401[i][1]

            buffer_xml: bytes = TempFileHelper.get_conteudo_e_deleta(nome_arq)
            try:
                posicao_anbima_401: XMLAnbima401Posicao = (
                    service_xml_anbima_401.get_posicao(buffer_xml)
                )
                posicoes_anbima_401.append(posicao_anbima_401)
            except Exception as e:
                aviso: APIWarning = APIWarning(
                    tipo_id="fundo_xml_nome", id=nome_arq_originial, mensagens=[str(e)]
                )
                avisos.append(aviso)

        estoque: list[ComparacaoEstoqueSchema] = []
        for posicao in posicoes_anbima_401:
            fundo: XMLAnbima401Fundo = posicao.fundo
            cnpj: str = fundo.header.cnpj
            data_posicao: date = datetime.strptime(
                fundo.header.dtposicao, "%Y%m%d"
            ).date()
            codigo_britech: str | None = (
                service_caracteristicas_fundos.get_fundo_codigo_britech_from_cnpj(
                    fundo_cnpj=cnpj,
                )
            )
            nome_fundo: str | None = (
                service_caracteristicas_fundos.get_fundo_nome_by_cnpj(
                    cnpj=cnpj,
                )
            )
            codigo_administrador: str | None = (
                service_caracteristicas_fundos.get_fundo_codigo_administrador_by_cnpj(
                    cnpj=cnpj,
                )
            )
            if (
                codigo_britech is None
                or nome_fundo is None
                or codigo_administrador is None
            ):
                aviso: APIWarning = APIWarning(
                    tipo_id="fundo_cnpj",
                    id=cnpj,
                    mensagens=[
                        CaracteristicasFundosService.get_fundo_cnpj_nao_encontrado(cnpj)
                    ],
                )
                avisos.append(aviso)
                continue

            aviso: APIWarning = APIWarning(
                tipo_id="fundo_codigo_britech", id=codigo_britech, mensagens=[]
            )
            fundo_estoque_xml: dict[str, AtivoCarteiraSchema] = {
                **self.__get_carteira_estoque_titulos_publicos_from_xml(
                    fundo=fundo,
                    forma_aviso=aviso,
                    avisos=avisos,
                ),
                **self.__get_carteira_estoque_titulos_privados_from_xml(
                    fundo=fundo,
                    forma_aviso=aviso,
                    avisos=avisos,
                ),
                **self.__get_carteira_estoque_debentures_from_xml(
                    fundo=fundo,
                    forma_aviso=aviso,
                    avisos=avisos,
                ),
                **self.__get_carteira_estoque_acoes_from_xml(
                    usdbrl=Decimal(usdbrl),
                    fundo=fundo,
                    forma_aviso=aviso,
                    avisos=avisos,
                ),
                **self.__get_carteira_estoque_futuros_from_xml(
                    usdbrl=Decimal(usdbrl),
                    fundo=fundo,
                    service_depara_offshore_ativo=service_depara_offshore_ativo,
                    forma_aviso=aviso,
                    avisos=avisos,
                ),
                **self.__get_carteira_estoque_opcoes_acoes_from_xml(
                    usdbrl=Decimal(usdbrl),
                    fundo=fundo,
                    service_xml_anbima_401_offshore=service_xml_anbima_401_offshore,
                    service_depara_offshore_ativo=service_depara_offshore_ativo,
                    forma_aviso=aviso,
                    avisos=avisos,
                ),
                **self.__get_carteira_estoque_opcoes_derivativos_from_xml(
                    usdbrl=Decimal(usdbrl),
                    fundo=fundo,
                    service_xml_anbima_401_offshore=service_xml_anbima_401_offshore,
                    service_depara_offshore_ativo=service_depara_offshore_ativo,
                    forma_aviso=aviso,
                    avisos=avisos,
                ),
                **self.__get_carteira_estoque_cotas_from_xml(
                    fundo=fundo,
                    service_depara_cotas_fundos=service_depara_cotas_fundos,
                    forma_aviso=aviso,
                    avisos=avisos,
                ),
            }

            fundo_estoque_britech: dict[str, AtivoCarteiraSchema] = {
                **self.__get_carteira_estoque_renda_fixa_from_estoque_britech(
                    fundo_codigo_britech=codigo_britech,
                    data_posicao=data_posicao,
                    estoque_renda_fixa_britech=estoque_renda_fixa,
                    avisos=avisos,
                ),
                **self.__get_carteira_estoque_renda_variavel_from_estoque_britech(
                    fundo_codigo_britech=codigo_britech,
                    data_posicao=data_posicao,
                    estoque_renda_variavel_britech=estoque_renda_variavel,
                ),
                **self.__get_carteira_estoque_futuro_from_estoque_britech(
                    fundo_codigo_britech=codigo_britech,
                    data_posicao=data_posicao,
                    estoque_futuro_britech=estoque_futuro,
                ),
                **self.__get_carteira_estoque_cotas_from_estoque_britech(
                    fundo_codigo_britech=codigo_britech,
                    data_posicao=data_posicao,
                    estoque_cotas_britech=estoque_cota,
                    avisos=avisos,
                ),
            }

            comparacoes_ativos: list[ComparacaoEstoqueSchema] = (
                self.__get_comparacoes_ativos(
                    fundo_codigo_britech=codigo_britech,
                    fundo_nome=nome_fundo,
                    fundo_codigo_administrador=codigo_administrador,
                    fundo_cnpj=cnpj,
                    data_referente=data_posicao,
                    fundo_estoque_xml=fundo_estoque_xml,
                    fundo_estoque_britech=fundo_estoque_britech,
                )
            )

            for comparacao in comparacoes_ativos:
                estoque.append(comparacao)

        return ResponseSchema(estoque=estoque, warnings=avisos)

    def __get_carteira_estoque_titulos_publicos_from_xml(
        self,
        fundo: XMLAnbima401Fundo,
        forma_aviso: APIWarning,
        avisos: list[APIWarning],
    ) -> dict[str, AtivoCarteiraSchema]:
        estoque: dict[str, AtivoCarteiraSchema] = {}

        for titulo_publico in fundo.titpublico:
            aviso = deepcopy(forma_aviso)
            ano_vencimento: str = (
                BritechEstoqueService.get_vencimento_ntnb_compromissada()
                if titulo_publico.compromisso
                else titulo_publico.dtvencimento[0:4]
            )
            codigo: str = (
                BritechEstoqueService.get_codigo_ntnb_compromissada() + ano_vencimento
                if titulo_publico.compromisso
                else titulo_publico.codativo + ano_vencimento
            )
            quantidade: Decimal = AtivosService.get_quantidade_tratada(
                quantidade=titulo_publico.qtdisponivel + titulo_publico.qtgarantia,
                side_operacao=SideOperacao(titulo_publico.classeoperacao),
            )

            if quantidade == 0:
                continue

            if codigo in estoque:
                pu_posicao_antigo: Decimal = estoque[codigo].preco_unitario_posicao
                quantidade_antiga: Decimal = estoque[codigo].quantidade

                pu_posicao_novo: Decimal = titulo_publico.puposicao
                quantidade_nova: Decimal = quantidade

                pu_posicao: Decimal = CalculosService.get_media_ponderada(
                    [
                        (pu_posicao_antigo, quantidade_antiga),
                        (pu_posicao_novo, quantidade_nova),
                    ]
                )

                estoque[codigo].preco_unitario_posicao = pu_posicao
                estoque[codigo].quantidade = quantidade_antiga + quantidade_nova
                continue

            isin: str = titulo_publico.isin
            aviso_isin: str | None = AtivosService.get_aviso_isin(
                isin=isin,
                identificador_ativo=codigo,
                tipo_ativo="Título Público",
            )
            if aviso_isin:
                aviso.mensagens.append(aviso_isin)

            preco_unitario_posicao: Decimal = titulo_publico.puposicao
            ativo_carteira: AtivoCarteiraSchema = AtivoCarteiraSchema(
                isin=isin,
                codigo=codigo,
                quantidade=quantidade,
                preco_unitario_posicao=preco_unitario_posicao,
                tipo="RendaFixa",
            )
            estoque[codigo] = ativo_carteira

            if len(aviso.mensagens) > 0:
                avisos.append(aviso)

        return estoque

    def __get_carteira_estoque_titulos_privados_from_xml(
        self,
        fundo: XMLAnbima401Fundo,
        forma_aviso: APIWarning,
        avisos: list[APIWarning],
    ) -> dict[str, AtivoCarteiraSchema]:
        estoque: dict[str, AtivoCarteiraSchema] = {}

        for titulo_privado in fundo.titprivado:
            aviso = deepcopy(forma_aviso)

            isin: str = titulo_privado.isin
            aviso_isin: str | None = AtivosService.get_aviso_isin(
                isin=isin,
                identificador_ativo=titulo_privado.codativo,
                tipo_ativo="Título Privado",
            )
            if aviso_isin:
                aviso.mensagens.append(aviso_isin)

            codigo: str = titulo_privado.codativo.replace(" ", "")
            quantidade: Decimal = AtivosService.get_quantidade_tratada(
                quantidade=titulo_privado.qtdisponivel + titulo_privado.qtgarantia,
                side_operacao=SideOperacao(titulo_privado.classeoperacao),
            )
            if quantidade == 0:
                continue

            if codigo in estoque:
                pu_posicao_antigo: Decimal = estoque[codigo].preco_unitario_posicao
                quantidade_antiga: Decimal = estoque[codigo].quantidade

                pu_posicao_novo: Decimal = titulo_privado.puposicao
                quantidade_nova: Decimal = quantidade

                pu_posicao: Decimal = CalculosService.get_media_ponderada(
                    [
                        (pu_posicao_antigo, quantidade_antiga),
                        (pu_posicao_novo, quantidade_nova),
                    ]
                )

                estoque[codigo].preco_unitario_posicao = pu_posicao
                estoque[codigo].quantidade = quantidade_antiga + quantidade_nova
                continue

            preco_unitario_posicao: Decimal = titulo_privado.puposicao
            ativo_carteira: AtivoCarteiraSchema = AtivoCarteiraSchema(
                isin=isin,
                codigo=codigo,
                quantidade=quantidade,
                preco_unitario_posicao=preco_unitario_posicao,
                tipo="RendaFixa",
            )
            estoque[codigo] = ativo_carteira

            if len(aviso.mensagens) > 0:
                avisos.append(aviso)

        return estoque

    def __get_carteira_estoque_debentures_from_xml(
        self,
        fundo: XMLAnbima401Fundo,
        forma_aviso: APIWarning,
        avisos: list[APIWarning],
    ) -> dict[str, AtivoCarteiraSchema]:
        estoque: dict[str, AtivoCarteiraSchema] = {}

        for debenture in fundo.debenture:
            aviso = deepcopy(forma_aviso)
            codigo: str = debenture.coddeb
            quantidade: Decimal = AtivosService.get_quantidade_tratada(
                quantidade=debenture.qtdisponivel + debenture.qtgarantia,
                side_operacao=SideOperacao(debenture.classeoperacao),
            )
            if quantidade == 0:
                continue

            if codigo in estoque:
                pu_posicao_antigo: Decimal = estoque[codigo].preco_unitario_posicao
                quantidade_antiga: Decimal = estoque[codigo].quantidade

                pu_posicao_novo: Decimal = debenture.puposicao
                quantidade_nova: Decimal = quantidade

                pu_posicao: Decimal = CalculosService.get_media_ponderada(
                    [
                        (pu_posicao_antigo, quantidade_antiga),
                        (pu_posicao_novo, quantidade_nova),
                    ]
                )

                estoque[codigo].preco_unitario_posicao = pu_posicao
                estoque[codigo].quantidade = quantidade_antiga + quantidade_nova
                continue

            isin: str = debenture.isin
            aviso_isin: str | None = AtivosService.get_aviso_isin(
                isin=isin,
                identificador_ativo=codigo,
                tipo_ativo="Debênture",
            )
            if aviso_isin:
                aviso.mensagens.append(aviso_isin)

            preco_unitario_posicao: Decimal = debenture.puposicao
            ativo_carteira: AtivoCarteiraSchema = AtivoCarteiraSchema(
                isin=isin,
                codigo=codigo,
                quantidade=quantidade,
                preco_unitario_posicao=preco_unitario_posicao,
                tipo="RendaFixa",
            )
            estoque[codigo] = ativo_carteira

            if len(aviso.mensagens) > 0:
                avisos.append(aviso)

        return estoque

    def __get_carteira_estoque_acoes_from_xml(
        self,
        usdbrl: Decimal,
        fundo: XMLAnbima401Fundo,
        forma_aviso: APIWarning,
        avisos: list[APIWarning],
    ) -> dict[str, AtivoCarteiraSchema]:
        estoque: dict[str, AtivoCarteiraSchema] = {}

        for acao in fundo.acoes:
            aviso = deepcopy(forma_aviso)
            codigo: str = acao.codativo
            quantidade: Decimal = AtivosService.get_quantidade_tratada(
                quantidade=acao.qtdisponivel + acao.qtgarantia,
                side_operacao=SideOperacao(acao.classeoperacao),
            )

            if quantidade == 0:
                continue

            if codigo in estoque:
                estoque[codigo].quantidade += quantidade
                continue

            isin: str = acao.isin
            aviso_isin: str | None = AtivosService.get_aviso_isin(
                isin=isin,
                identificador_ativo=codigo,
                tipo_ativo="Ação",
            )
            if aviso_isin:
                aviso.mensagens.append(aviso_isin)

            preco_unitario_posicao: Decimal = (
                (acao.puposicao / acao.lote) / usdbrl
                if AtivosService.is_ativo_offshore(isin)
                else acao.puposicao / acao.lote
            )

            ativo_carteira: AtivoCarteiraSchema = AtivoCarteiraSchema(
                isin=isin,
                codigo=codigo,
                quantidade=quantidade,
                preco_unitario_posicao=preco_unitario_posicao,
                tipo="RendaVariavel",
            )
            estoque[codigo] = ativo_carteira

            if len(aviso.mensagens) > 0:
                avisos.append(aviso)

        return estoque

    def __get_carteira_estoque_futuros_from_xml(
        self,
        usdbrl: Decimal,
        fundo: XMLAnbima401Fundo,
        service_depara_offshore_ativo: DeParaOffshoreAtivoService,
        forma_aviso: APIWarning,
        avisos: list[APIWarning],
    ) -> dict[str, AtivoCarteiraSchema]:
        estoque: dict[str, AtivoCarteiraSchema] = {}

        for futuro in fundo.futuros:
            aviso = deepcopy(forma_aviso)
            codigo_xml: str = futuro.ativo
            serie_xml: str = futuro.serie

            isin: str = futuro.isin
            aviso_isin: str | None = AtivosService.get_aviso_isin(
                isin=isin,
                identificador_ativo=f"cod: {codigo_xml}, série: {serie_xml}",
                tipo_ativo="Futuro",
            )
            if aviso_isin:
                aviso.mensagens.append(aviso_isin)

            quantidade_xml: Decimal = futuro.quantidade
            if quantidade_xml == 0:
                continue

            linha_depara: DeParaLinhaOffshoreAtivo | None = (
                service_depara_offshore_ativo.get_depara_linha_offshore_ativo(
                    codigo_ativo_objeto=codigo_xml, xml_tag=Tags.FUTUROS
                )
            )

            if AtivosService.is_ativo_offshore(isin):
                if linha_depara is None:
                    aviso.mensagens.append(
                        service_depara_offshore_ativo.get_mensagem_aviso_ativo_nao_encontrado(
                            tipo_ativo="Futuro",
                            identificador_ativo=f"cod: {codigo_xml}, série: {serie_xml}",
                        )
                    )
                    avisos.append(aviso)
                    continue
                if linha_depara.tamanho_lote is None:
                    aviso.mensagens.append(
                        service_depara_offshore_ativo.get_mensagem_aviso_ativo_sem_tamanho_lote(
                            tipo_ativo="Futuro",
                            identificador_ativo=f"cod: {codigo_xml}, série: {serie_xml}",
                        )
                    )
                    avisos.append(aviso)
                    continue

                codigo: str = linha_depara.bloomberg_codigo_ativo_objeto + futuro.serie
                quantidade: Decimal = AtivosService.get_quantidade_tratada(
                    quantidade=quantidade_xml,
                    side_operacao=SideOperacao(futuro.classeoperacao),
                )

                if codigo in estoque:
                    estoque[codigo].quantidade += quantidade
                    continue

                preco_unitario_posicao: Decimal = (
                    (futuro.vltotalpos / (abs(quantidade) * linha_depara.tamanho_lote))
                ) / Decimal(usdbrl)

                ativo_carteira: AtivoCarteiraSchema = AtivoCarteiraSchema(
                    isin=isin,
                    codigo=codigo,
                    quantidade=quantidade,
                    preco_unitario_posicao=preco_unitario_posicao,
                    tipo="Futuro",
                )
                estoque[codigo] = ativo_carteira
            else:
                codigo: str = futuro.ativo + futuro.serie
                quantidade: Decimal = AtivosService.get_quantidade_tratada(
                    quantidade=futuro.quantidade,
                    side_operacao=SideOperacao(futuro.classeoperacao),
                )

                if codigo in estoque:
                    estoque[codigo].quantidade += quantidade
                    continue
                tamanho_lote: Decimal = Decimal(1)

                if linha_depara is not None and linha_depara.tamanho_lote is not None:
                    tamanho_lote = Decimal(linha_depara.tamanho_lote)
                preco_unitario_posicao: Decimal = futuro.vltotalpos / (
                    abs(quantidade) * tamanho_lote
                )
                ativo_carteira: AtivoCarteiraSchema = AtivoCarteiraSchema(
                    isin=isin,
                    codigo=codigo,
                    quantidade=quantidade,
                    preco_unitario_posicao=preco_unitario_posicao,
                    tipo="Futuro",
                )
                estoque[codigo] = ativo_carteira

            if len(aviso.mensagens) > 0:
                avisos.append(aviso)

        return estoque

    def __get_carteira_estoque_opcoes_acoes_from_xml(
        self,
        usdbrl: Decimal,
        fundo: XMLAnbima401Fundo,
        service_xml_anbima_401_offshore: XMLAnbima401OffshoreService,
        service_depara_offshore_ativo: DeParaOffshoreAtivoService,
        forma_aviso: APIWarning,
        avisos: list[APIWarning],
    ) -> dict[str, AtivoCarteiraSchema]:
        estoque: dict[str, AtivoCarteiraSchema] = {}

        for opcao_acao in fundo.opcoesacoes:
            aviso = deepcopy(forma_aviso)
            codigo_xml: str = opcao_acao.codativo

            isin: str = opcao_acao.isin
            aviso_isin: str | None = AtivosService.get_aviso_isin(
                isin=isin,
                identificador_ativo=codigo_xml,
                tipo_ativo="Opção de Ação",
            )
            if aviso_isin:
                aviso.mensagens.append(aviso_isin)

            quantidade_xml: Decimal = opcao_acao.qtdisponivel
            if quantidade_xml == 0:
                continue

            if AtivosService.is_ativo_offshore(isin):
                xml_codigos_opcao: CodigosOpcao = (
                    service_xml_anbima_401_offshore.get_codigos_opcao_acao_offshore(
                        xml_codigo=codigo_xml
                    )
                )
                xml_codigo_ativo_objeto = xml_codigos_opcao.codigo_ativo_objeto
                codigo_serie = xml_codigos_opcao.codigo_serie
                tamanho_lote: Decimal = Decimal(100)

                linha_depara: DeParaLinhaOffshoreAtivo | None = (
                    service_depara_offshore_ativo.get_depara_linha_offshore_ativo(
                        codigo_ativo_objeto=xml_codigo_ativo_objeto,
                        xml_tag=Tags.OPCOESACOES,
                    )
                )
                if linha_depara:
                    aviso.mensagens.append(
                        service_depara_offshore_ativo.get_mensagem_aviso_ativo_encontrado(
                            tipo_ativo="Opção de Ação",
                            identificador_ativo=codigo_xml,
                        )
                    )

                    codigo: str = (
                        linha_depara.bloomberg_codigo_ativo_objeto + codigo_serie
                    )
                    if linha_depara.tamanho_lote is not None:
                        tamanho_lote = Decimal(linha_depara.tamanho_lote)
                else:
                    codigo: str = xml_codigo_ativo_objeto + codigo_serie

                quantidade: Decimal = AtivosService.get_quantidade_tratada(
                    quantidade=quantidade_xml,
                    side_operacao=SideOperacao(opcao_acao.classeoperacao),
                )

                if codigo in estoque:
                    estoque[codigo].quantidade += quantidade
                    continue

                preco_unitario_posicao: Decimal = (
                    opcao_acao.puposicao / (abs(quantidade) * tamanho_lote)
                ) / Decimal(usdbrl)

                ativo_carteira: AtivoCarteiraSchema = AtivoCarteiraSchema(
                    isin=isin,
                    codigo=codigo,
                    quantidade=quantidade,
                    preco_unitario_posicao=preco_unitario_posicao,
                    tipo="RendaVariavel",
                )
                estoque[codigo] = ativo_carteira
            else:
                codigo: str = codigo_xml
                quantidade: Decimal = AtivosService.get_quantidade_tratada(
                    quantidade=quantidade_xml,
                    side_operacao=SideOperacao(opcao_acao.classeoperacao),
                )

                if codigo in estoque:
                    estoque[codigo].quantidade += quantidade
                    continue

                preco_unitario_posicao: Decimal = opcao_acao.puposicao

                ativo_carteira: AtivoCarteiraSchema = AtivoCarteiraSchema(
                    isin=isin,
                    codigo=codigo,
                    quantidade=quantidade,
                    preco_unitario_posicao=preco_unitario_posicao,
                    tipo="RendaVariavel",
                )
                estoque[codigo] = ativo_carteira

            if len(aviso.mensagens) > 0:
                avisos.append(aviso)

        return estoque

    def __get_carteira_estoque_opcoes_derivativos_from_xml(
        self,
        usdbrl: Decimal,
        fundo: XMLAnbima401Fundo,
        service_xml_anbima_401_offshore: XMLAnbima401OffshoreService,
        service_depara_offshore_ativo: DeParaOffshoreAtivoService,
        forma_aviso: APIWarning,
        avisos: list[APIWarning],
    ) -> dict[str, AtivoCarteiraSchema]:
        estoque: dict[str, AtivoCarteiraSchema] = {}

        for opcao_derivativo in fundo.opcoesderiv:
            aviso = deepcopy(forma_aviso)
            codigo_xml: str = opcao_derivativo.ativo
            serie_xml: str = opcao_derivativo.serie

            isin: str = opcao_derivativo.isin
            aviso_isin: str | None = AtivosService.get_aviso_isin(
                isin=isin,
                identificador_ativo=codigo_xml,
                tipo_ativo="Opção de Derivativo",
            )
            if aviso_isin:
                aviso.mensagens.append(aviso_isin)

            quantidade_xml: Decimal = opcao_derivativo.quantidade
            if quantidade_xml == 0:
                continue

            if AtivosService.is_ativo_offshore(isin):
                xml_codigos_futuro: CodigosFuturo = (
                    service_xml_anbima_401_offshore.get_codigos_futuros(
                        xml_codigo=codigo_xml
                    )
                )
                xml_codigo_ativo_objeto_futuro = xml_codigos_futuro.codigo_ativo_objeto
                codigo_vencimento = xml_codigos_futuro.codigo_vencimento

                linha_depara: DeParaLinhaOffshoreAtivo | None = (
                    service_depara_offshore_ativo.get_depara_linha_offshore_ativo(
                        codigo_ativo_objeto=xml_codigo_ativo_objeto_futuro,
                        xml_tag=Tags.OPCOESDERIV,
                    )
                )
                if linha_depara is None:
                    aviso.mensagens.append(
                        service_depara_offshore_ativo.get_mensagem_aviso_ativo_nao_encontrado(
                            tipo_ativo="Opção de Derivativo",
                            identificador_ativo=codigo_xml,
                        )
                    )
                    avisos.append(aviso)
                    continue
                if linha_depara.tamanho_lote is None:
                    aviso.mensagens.append(
                        service_depara_offshore_ativo.get_mensagem_aviso_ativo_sem_tamanho_lote(
                            tipo_ativo="Opção de Derivativo",
                            identificador_ativo="Opção de Derivativo",
                        )
                    )
                    avisos.append(aviso)
                    continue

                codigo: str = (
                    linha_depara.bloomberg_codigo_ativo_objeto
                    + codigo_vencimento
                    + serie_xml[0]
                    + str(opcao_derivativo.precoexercicio).rstrip("0").replace(".", "")
                )
                quantidade: Decimal = AtivosService.get_quantidade_tratada(
                    quantidade=quantidade_xml,
                    side_operacao=SideOperacao(opcao_derivativo.classeoperacao),
                )

                if codigo in estoque:
                    estoque[codigo].quantidade += quantidade
                    continue

                preco_unitario_posicao: Decimal = (
                    opcao_derivativo.puposicao
                    / (abs(quantidade) * linha_depara.tamanho_lote)
                ) / Decimal(usdbrl)

                ativo_carteira: AtivoCarteiraSchema = AtivoCarteiraSchema(
                    isin=isin,
                    codigo=codigo,
                    quantidade=quantidade,
                    preco_unitario_posicao=preco_unitario_posicao,
                    tipo="Futuro",
                )
                estoque[codigo] = ativo_carteira
            else:
                codigo: str = codigo_xml + serie_xml
                quantidade: Decimal = AtivosService.get_quantidade_tratada(
                    quantidade=quantidade_xml,
                    side_operacao=SideOperacao(opcao_derivativo.classeoperacao),
                )

                if codigo in estoque:
                    estoque[codigo].quantidade += quantidade
                    continue

                preco_unitario_posicao: Decimal = opcao_derivativo.puposicao

                ativo_carteira: AtivoCarteiraSchema = AtivoCarteiraSchema(
                    isin=isin,
                    codigo=codigo,
                    quantidade=quantidade,
                    preco_unitario_posicao=preco_unitario_posicao,
                    tipo="Futuro",
                )
                estoque[codigo] = ativo_carteira

            if len(aviso.mensagens) > 0:
                avisos.append(aviso)

        return estoque

    def __get_carteira_estoque_cotas_from_xml(
        self,
        fundo: XMLAnbima401Fundo,
        service_depara_cotas_fundos: DeparaCotasService,
        forma_aviso: APIWarning,
        avisos: list[APIWarning],
    ) -> dict[str, AtivoCarteiraSchema]:
        estoque: dict[str, AtivoCarteiraSchema] = {}

        for cota in fundo.cotas:
            aviso = deepcopy(forma_aviso)

            linha_depara_cota_fundo: LinhaDeparaCotaFundo | None = (
                service_depara_cotas_fundos.get_linha_depara_cota_fundo_by_isin(
                    isin=cota.isin,
                )
            )
            if linha_depara_cota_fundo is None:
                aviso.mensagens.append(
                    DeparaCotasService.get_fundo_codigo_britech_nao_encontrado_depara_cotas(
                        isin
                    )
                )
                avisos.append(aviso)
                continue

            codigo: str = (
                linha_depara_cota_fundo.codigo_britech_fundo_espelho
                if linha_depara_cota_fundo.codigo_britech_fundo_espelho is not None
                else linha_depara_cota_fundo.id_carteira
            )
            quantidade: Decimal = cota.qtdisponivel + cota.qtgarantia
            if quantidade == 0:
                continue

            if codigo in estoque:
                estoque[codigo].quantidade += quantidade
                continue

            isin: str = cota.isin
            aviso_isin: str | None = AtivosService.get_aviso_isin(
                isin=isin,
                identificador_ativo=codigo,
                tipo_ativo="Cota",
            )
            if aviso_isin:
                aviso.mensagens.append(aviso_isin)
                avisos.append(aviso)
                continue

            preco_unitario_posicao: Decimal = cota.puposicao
            ativo_carteira: AtivoCarteiraSchema = AtivoCarteiraSchema(
                isin=isin,
                codigo=codigo,
                quantidade=quantidade,
                preco_unitario_posicao=preco_unitario_posicao,
                tipo="CotasFundos",
            )
            estoque[codigo] = ativo_carteira

        return estoque

    def __get_carteira_estoque_renda_fixa_from_estoque_britech(
        self,
        fundo_codigo_britech: str,
        data_posicao: date,
        estoque_renda_fixa_britech: list[EstoqueBritechRendaFixa],
        avisos: list[APIWarning],
    ) -> dict[str, AtivoCarteiraSchema]:
        estoque: dict[str, AtivoCarteiraSchema] = {}

        for estoque_ativo in estoque_renda_fixa_britech:
            if (
                estoque_ativo.data_historico != data_posicao
                or str(estoque_ativo.id_cliente) != fundo_codigo_britech
            ):
                continue

            if (
                estoque_ativo.codigo_cetip is None
                and estoque_ativo.codigo_custodia is None
            ):
                aviso: APIWarning = APIWarning(
                    tipo_id="estoque_britech_renda_fixa",
                    id=estoque_ativo.descricao_completa,
                    mensagens=[
                        'Ativo sem código (coluna "Código Cetip" e coluna "Código Custódia). P/ tit. pub. essa mesma coluna representa o código SELIC'
                    ],
                )
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            codigo_ativo: str

            if estoque_ativo.codigo_cetip is not None:
                codigo_ativo = estoque_ativo.codigo_cetip
            else:
                assert (
                    estoque_ativo.codigo_custodia is not None
                ), "Falha na lógica: codigo_custodia não deveria ser None aqui"
                codigo_ativo = estoque_ativo.codigo_custodia

            isin: str | None = estoque_ativo.codigo_isin
            codigo: str = BritechEstoqueService.get_codigo_ativo_renda_fixa(
                codigo_ativo=codigo_ativo,
                data_vencimento=estoque_ativo.data_vencimento,
                tipo_ativo=estoque_ativo.descricao,
            )
            quantidade = estoque_ativo.quantidade
            if quantidade == 0:
                continue

            if codigo in estoque:
                pu_posicao_antigo: Decimal = estoque[codigo].preco_unitario_posicao
                quantidade_antiga: Decimal = estoque[codigo].quantidade

                pu_posicao_novo: Decimal = estoque_ativo.pu_mercado
                quantidade_nova: Decimal = estoque_ativo.quantidade

                pu_posicao: Decimal = CalculosService.get_media_ponderada(
                    [
                        (pu_posicao_antigo, quantidade_antiga),
                        (pu_posicao_novo, quantidade_nova),
                    ]
                )

                estoque[codigo].preco_unitario_posicao = pu_posicao
                estoque[codigo].quantidade = quantidade_antiga + quantidade_nova
                continue

            preco_unitario_posicao = estoque_ativo.pu_mercado

            ativo: AtivoCarteiraSchema = AtivoCarteiraSchema(
                isin=isin,
                codigo=codigo,
                quantidade=quantidade,
                preco_unitario_posicao=preco_unitario_posicao,
                tipo="RendaFixa",
            )
            estoque[codigo] = ativo

        return estoque

    def __get_carteira_estoque_renda_variavel_from_estoque_britech(
        self,
        fundo_codigo_britech: str,
        data_posicao: date,
        estoque_renda_variavel_britech: list[EstoqueBritechRendaVariavel],
    ) -> dict[str, AtivoCarteiraSchema]:
        estoque: dict[str, AtivoCarteiraSchema] = {}

        for estoque_ativo in estoque_renda_variavel_britech:
            if (
                estoque_ativo.data_historico != data_posicao
                or str(estoque_ativo.id_cliente) != fundo_codigo_britech
            ):
                continue

            codigo: str = estoque_ativo.cd_ativo_bolsa
            quantidade = estoque_ativo.quantidade

            if quantidade == 0:
                continue

            if codigo in estoque:
                estoque[codigo].quantidade += quantidade
                continue

            preco_unitario_posicao = estoque_ativo.pu_mercado
            isin: str | None = None

            ativo: AtivoCarteiraSchema = AtivoCarteiraSchema(
                isin=isin,
                codigo=codigo,
                quantidade=quantidade,
                preco_unitario_posicao=preco_unitario_posicao,
                tipo="RendaVariavel",
            )
            estoque[codigo] = ativo

        return estoque

    def __get_carteira_estoque_futuro_from_estoque_britech(
        self,
        fundo_codigo_britech: str,
        data_posicao: date,
        estoque_futuro_britech: list[EstoqueBritechFuturo],
    ) -> dict[str, AtivoCarteiraSchema]:
        estoque: dict[str, AtivoCarteiraSchema] = {}

        for estoque_ativo in estoque_futuro_britech:
            if (
                estoque_ativo.data_historico != data_posicao
                or str(estoque_ativo.id_cliente) != fundo_codigo_britech
            ):
                continue

            codigo: str = estoque_ativo.cd_ativo_bmf + estoque_ativo.serie
            quantidade = estoque_ativo.quantidade
            if quantidade == 0:
                continue

            if codigo in estoque:
                estoque[codigo].quantidade += estoque_ativo.quantidade
                continue

            isin: str | None = None
            preco_unitario_posicao = estoque_ativo.pu_mercado

            ativo: AtivoCarteiraSchema = AtivoCarteiraSchema(
                isin=isin,
                codigo=codigo,
                quantidade=quantidade,
                preco_unitario_posicao=preco_unitario_posicao,
                tipo="Futuro",
            )
            estoque[codigo] = ativo

        return estoque

    def __get_carteira_estoque_cotas_from_estoque_britech(
        self,
        fundo_codigo_britech: str,
        data_posicao: date,
        estoque_cotas_britech: list[EstoqueBritechCota],
        avisos: list[APIWarning],
    ) -> dict[str, AtivoCarteiraSchema]:
        estoque: dict[str, AtivoCarteiraSchema] = {}

        for estoque_ativo in estoque_cotas_britech:
            if (
                estoque_ativo.data_historico != data_posicao
                or str(estoque_ativo.id_cliente) != fundo_codigo_britech
            ):
                continue

            isin: str | None = estoque_ativo.isin_cota
            if isin is None:
                aviso: APIWarning = APIWarning(
                    tipo_id="ativo_estoque_britech_cotas_codigo_isin",
                    id=str(estoque_ativo.id_carteira),
                    mensagens=[
                        f'Cota de idcarteira "{estoque_ativo.id_carteira}" sem isin no estoque de cotas da britech'
                    ],
                )
                if aviso not in avisos:
                    avisos.append(aviso)

            codigo: str = str(estoque_ativo.id_carteira)
            quantidade = estoque_ativo.quantidade
            if quantidade == 0:
                continue

            if codigo in estoque:
                estoque[codigo].quantidade += estoque_ativo.quantidade
                continue

            preco_unitario_posicao = estoque_ativo.pu_mercado
            ativo: AtivoCarteiraSchema = AtivoCarteiraSchema(
                isin=isin,
                codigo=codigo,
                quantidade=quantidade,
                preco_unitario_posicao=preco_unitario_posicao,
                tipo="CotasFundos",
            )
            estoque[codigo] = ativo

        return estoque

    def __get_comparacoes_ativos(
        self,
        fundo_codigo_britech: str,
        fundo_codigo_administrador: str,
        fundo_cnpj: str,
        fundo_nome: str,
        data_referente: date,
        fundo_estoque_xml: dict[str, AtivoCarteiraSchema],
        fundo_estoque_britech: dict[str, AtivoCarteiraSchema],
    ) -> list[ComparacaoEstoqueSchema]:
        comparacoes: list[ComparacaoEstoqueSchema] = []
        for codigo_ativo_xml, ativo_xml in fundo_estoque_xml.items():
            if codigo_ativo_xml not in fundo_estoque_britech:
                comparacao: ComparacaoEstoqueSchema = ComparacaoEstoqueSchema(
                    fundo_codigo_britech=fundo_codigo_britech,
                    fundo_codigo_administrador=fundo_codigo_administrador,
                    fundo_cnpj=fundo_cnpj,
                    fundo_nome=fundo_nome,
                    data_referente=data_referente,
                    ativo_xml=ativo_xml,
                    tipo_ativo=ativo_xml.tipo,
                    ativo_britech=None,
                    diferenca_pu=None,
                    diferenca_quantidade=None,
                    diferenca_financeiro=None,
                )
                comparacoes.append(comparacao)
                continue

            ativo_britech: AtivoCarteiraSchema = fundo_estoque_britech[codigo_ativo_xml]
            diferenca_preco: Decimal = Decimal(
                abs(
                    ativo_xml.preco_unitario_posicao
                    - ativo_britech.preco_unitario_posicao
                )
            )
            diferenca_quantidade: Decimal = Decimal(
                abs(ativo_xml.quantidade - ativo_britech.quantidade)
            )
            diferenca_financeiro = Decimal(
                abs(ativo_xml.financeiro - ativo_britech.financeiro)
            )

            comparacao: ComparacaoEstoqueSchema = ComparacaoEstoqueSchema(
                fundo_codigo_britech=fundo_codigo_britech,
                fundo_codigo_administrador=fundo_codigo_administrador,
                fundo_cnpj=fundo_cnpj,
                fundo_nome=fundo_nome,
                data_referente=data_referente,
                ativo_xml=ativo_xml,
                ativo_britech=ativo_britech,
                tipo_ativo=ativo_xml.tipo,
                diferenca_pu=diferenca_preco,
                diferenca_quantidade=diferenca_quantidade,
                diferenca_financeiro=diferenca_financeiro,
            )
            comparacoes.append(comparacao)

        for codigo_ativo_britech, ativo_britech in fundo_estoque_britech.items():
            if codigo_ativo_britech not in fundo_estoque_xml:
                comparacao: ComparacaoEstoqueSchema = ComparacaoEstoqueSchema(
                    fundo_codigo_britech=fundo_codigo_britech,
                    fundo_codigo_administrador=fundo_codigo_administrador,
                    fundo_nome=fundo_nome,
                    fundo_cnpj=fundo_cnpj,
                    data_referente=data_referente,
                    ativo_xml=None,
                    ativo_britech=ativo_britech,
                    tipo_ativo=ativo_britech.tipo,
                    diferenca_pu=None,
                    diferenca_quantidade=None,
                    diferenca_financeiro=None,
                )
                comparacoes.append(comparacao)
                continue

            ativo_xml: AtivoCarteiraSchema = fundo_estoque_xml[codigo_ativo_britech]
            diferenca_preco: Decimal = Decimal(
                abs(
                    ativo_xml.preco_unitario_posicao
                    - ativo_britech.preco_unitario_posicao
                )
            )
            diferenca_quantidade: Decimal = Decimal(
                abs(ativo_xml.quantidade - ativo_britech.quantidade)
            )
            diferenca_financeiro: Decimal = Decimal(
                abs(ativo_xml.financeiro - ativo_britech.financeiro)
            )

            comparacao: ComparacaoEstoqueSchema = ComparacaoEstoqueSchema(
                fundo_codigo_britech=fundo_codigo_britech,
                fundo_codigo_administrador=fundo_codigo_administrador,
                fundo_nome=fundo_nome,
                fundo_cnpj=fundo_cnpj,
                data_referente=data_referente,
                ativo_xml=ativo_xml,
                ativo_britech=ativo_britech,
                tipo_ativo=ativo_britech.tipo,
                diferenca_pu=diferenca_preco,
                diferenca_quantidade=diferenca_quantidade,
                diferenca_financeiro=diferenca_financeiro,
            )
            if comparacao not in comparacoes:
                comparacoes.append(comparacao)

        return comparacoes
