from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_EVEN
from pandas import DataFrame

from .schema import ResponseSchema, AtivoPrecoFundo as FlatAtivoPrecoFundo
from .types import AtivoPrecosFundos, FundoInfo
from modules.ativos.service import AtivosService
from modules.caracteristicas_fundos.service import CaracteristicasFundosService
from modules.util.api_warning import APIWarning
from modules.util.caracteristicas_fundos import CaractersticasFundosHelper
from modules.util.temp_file import TempFileHelper
from modules.posicao.xml_anbima_401.service import XMLAnbima401Service
from modules.posicao.xml_anbima_401.types import (
    XMLAnbima401Posicao,
    XMLAnbima401Fundo,
    XMLAnbima401Titprivado,
    XMLAnbima401Debenture,
)


class BatimentoPrecosCreditoPrivado:
    ativos_precos_fundos_por_custodiante: dict[str, dict[str, AtivoPrecosFundos]]
    __DIFERENCA_MINIMA: Decimal = Decimal(0.05)

    def __init__(self):
        self.ativos_precos_fundos_por_custodiante = {}

    def get_batimento_precos_credito_privado(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        nome_arq_xls_caracteristicas_fundos: str,
    ) -> ResponseSchema:
        buffer_caracteristicas_fundos: bytes = TempFileHelper.get_conteudo_e_deleta(
            nome_arq_xls_caracteristicas_fundos
        )

        dataframe_caracteristicas_fundos: DataFrame = (
            CaractersticasFundosHelper.get_dataframe_from_buffer(
                buffer_caracteristicas_fundos
            )
        )

        service_xml_anbima_401: XMLAnbima401Service = XMLAnbima401Service()
        service_caracteristicas_fundos: CaracteristicasFundosService = (
            CaracteristicasFundosService(
                dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos
            )
        )

        avisos: list[APIWarning] = []
        for i in range(0, len(nomes_arqs_xmls_anbima_401)):
            nome_arq: str = nomes_arqs_xmls_anbima_401[i][0]
            nome_arq_original: str = nomes_arqs_xmls_anbima_401[i][1]

            buffer_xml: bytes = TempFileHelper.get_conteudo_e_deleta(nome_arq)
            try:
                posicao_anbima_401: XMLAnbima401Posicao = (
                    service_xml_anbima_401.get_posicao(buffer_xml)
                )
            except Exception as e:
                aviso: APIWarning = APIWarning(
                    tipo_id="fundo_xml_nome", id=nome_arq_original, mensagens=[str(e)]
                )
                avisos.append(aviso)
                continue

            fundo: XMLAnbima401Fundo = posicao_anbima_401.fundo
            cnpj: str = fundo.header.cnpj
            try:
                data_posicao: date = datetime.strptime(
                    fundo.header.dtposicao, "%Y%m%d"
                ).date()
            except ValueError:
                aviso: APIWarning = APIWarning(
                    tipo_id="fundo_xml_nome",
                    id=nome_arq_original,
                    mensagens=[
                        f"Data de posição inválida no XML: {fundo.header.dtposicao}"
                    ],
                )
                avisos.append(aviso)
                continue

            fundo_codigo_britech: str | None = (
                service_caracteristicas_fundos.get_fundo_codigo_britech_from_cnpj(
                    fundo_cnpj=cnpj
                )
            )
            fundo_nome: str | None = (
                service_caracteristicas_fundos.get_fundo_nome_by_cnpj(
                    cnpj=cnpj,
                )
            )
            fundo_custodiante: str | None = (
                service_caracteristicas_fundos.get_fundo_custodiante_by_cnpj(cnpj)
            )
            fundo_codigo_administrador: str | None = (
                service_caracteristicas_fundos.get_fundo_codigo_administrador_by_cnpj(
                    cnpj=cnpj
                )
            )
            fundo_tipo_cota: str | None = (
                service_caracteristicas_fundos.get_fundo_tipo_cota_by_cnpj(cnpj=cnpj)
            )

            if (
                fundo_codigo_britech is None
                or fundo_nome is None
                or fundo_custodiante is None
                or fundo_codigo_administrador is None
                or fundo_tipo_cota is None
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

            fundo_info: FundoInfo = FundoInfo(
                codigo_britech=fundo_codigo_britech,
                codigo_administrador=fundo_codigo_administrador,
                cnpj=cnpj,
                nome=fundo_nome,
                custodiante=fundo_custodiante,
                tipo_cota=fundo_tipo_cota,
                nome_arq_xml_anbima_401=nome_arq_original,
            )

            forma_aviso: APIWarning = APIWarning(
                tipo_id="fundo_codigo_britech", id=fundo_codigo_britech, mensagens=[]
            )
            self.__inplace_insere_titulos_privados_precos_fundos(
                posicao_fundo=posicao_anbima_401,
                data_posicao=data_posicao,
                fundo_info=fundo_info,
                forma_aviso=forma_aviso,
                avisos=avisos,
            )
            self.__inplace_insere_debentures_precos_fundos(
                posicao_fundo=posicao_anbima_401,
                data_posicao=data_posicao,
                fundo_info=fundo_info,
                forma_aviso=forma_aviso,
                avisos=avisos,
            )

        flat_ativos_precos_fundos: list[FlatAtivoPrecoFundo] = (
            self.get_flat_ativos_precos_fundos_por_custodiante()
        )

        return ResponseSchema(ativos=flat_ativos_precos_fundos, warnings=avisos)

    def __inplace_insere_titulos_privados_precos_fundos(
        self,
        posicao_fundo: XMLAnbima401Posicao,
        data_posicao: date,
        fundo_info: FundoInfo,
        forma_aviso: APIWarning,
        avisos: list[APIWarning],
    ) -> None:
        titulos_privados: list[XMLAnbima401Titprivado] = posicao_fundo.fundo.titprivado
        custodiante: str = fundo_info.custodiante

        if custodiante not in self.ativos_precos_fundos_por_custodiante:
            self.ativos_precos_fundos_por_custodiante[custodiante] = {}

        for ativo in titulos_privados:
            aviso: APIWarning = deepcopy(forma_aviso)

            isin: str = ativo.isin
            aviso_isin: str | None = AtivosService.get_aviso_isin(
                isin=isin,
                identificador_ativo=ativo.codativo,
                tipo_ativo="Título Privado",
            )
            if aviso_isin:
                aviso.mensagens.append(aviso_isin)
                if aviso.mensagens:
                    avisos.append(aviso)

            if AtivosService.is_ativo_offshore(isin):
                continue

            codigo: str = ativo.codativo
            chave_ativo_preco_fundo: str = (
                BatimentoPrecosCreditoPrivado.__get_identificador_ativo_preco_fundo(
                    codigo=codigo, data_referente=data_posicao
                )
            )

            preco_unitario_posicao: Decimal = Decimal(
                ativo.puposicao.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
            )

            ativos_precos_fundos_do_custodiante = (
                self.ativos_precos_fundos_por_custodiante[custodiante]
            )

            if ativos_precos_fundos_do_custodiante.get(chave_ativo_preco_fundo) is None:
                preco_fundos: dict[Decimal, list[FundoInfo]] = {
                    preco_unitario_posicao: [fundo_info]
                }
                ativos_precos_fundos_do_custodiante[chave_ativo_preco_fundo] = (
                    AtivoPrecosFundos(
                        codigo=codigo,
                        isin=isin,
                        data=data_posicao,
                        precos_fundos=preco_fundos,
                    )
                )
            else:
                ativos_precos_fundos_do_custodiante[
                    chave_ativo_preco_fundo
                ].append_fundo_precos_fundos(
                    preco_unitario_posicao=preco_unitario_posicao, fundo_info=fundo_info
                )

    def __inplace_insere_debentures_precos_fundos(
        self,
        posicao_fundo: XMLAnbima401Posicao,
        data_posicao: date,
        fundo_info: FundoInfo,
        forma_aviso: APIWarning,
        avisos: list[APIWarning],
    ) -> None:
        debentures: list[XMLAnbima401Debenture] = posicao_fundo.fundo.debenture
        custodiante: str = fundo_info.custodiante

        if custodiante not in self.ativos_precos_fundos_por_custodiante:
            self.ativos_precos_fundos_por_custodiante[custodiante] = {}

        for ativo in debentures:
            aviso: APIWarning = deepcopy(forma_aviso)

            isin: str = ativo.isin
            aviso_isin: str | None = AtivosService.get_aviso_isin(
                isin=isin, identificador_ativo=ativo.coddeb, tipo_ativo="Debênture"
            )
            if aviso_isin:
                aviso.mensagens.append(aviso_isin)
                if aviso.mensagens:
                    avisos.append(aviso)

            codigo: str = ativo.coddeb
            chave_ativo_fundo: str = (
                BatimentoPrecosCreditoPrivado.__get_identificador_ativo_preco_fundo(
                    codigo=codigo, data_referente=data_posicao
                )
            )

            preco_unitario_posicao: Decimal = Decimal(
                ativo.puposicao.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
            )

            ativos_precos_fundos_do_custodiante = (
                self.ativos_precos_fundos_por_custodiante[custodiante]
            )

            if ativos_precos_fundos_do_custodiante.get(chave_ativo_fundo) is None:
                preco_fundos: dict[Decimal, list[FundoInfo]] = {
                    preco_unitario_posicao: [fundo_info]
                }
                ativos_precos_fundos_do_custodiante[chave_ativo_fundo] = (
                    AtivoPrecosFundos(
                        codigo=codigo,
                        isin=isin,
                        data=data_posicao,
                        precos_fundos=preco_fundos,
                    )
                )
            else:
                ativos_precos_fundos_do_custodiante[
                    chave_ativo_fundo
                ].append_fundo_precos_fundos(
                    preco_unitario_posicao=preco_unitario_posicao, fundo_info=fundo_info
                )

    def get_flat_ativos_precos_fundos_por_custodiante(
        self,
    ) -> list[FlatAtivoPrecoFundo]:
        flat_ativos_precos_fundos: list[FlatAtivoPrecoFundo] = []
        for (
            _,
            ativos_do_custodiante,
        ) in self.ativos_precos_fundos_por_custodiante.items():
            for __, ativo_preco_fundo in ativos_do_custodiante.items():
                if len(ativo_preco_fundo.precos_fundos) > 1:
                    precos_registrados = list(ativo_preco_fundo.precos_fundos.keys())

                    max_preco = max(precos_registrados)
                    min_preco = min(precos_registrados)
                    diferenca_preco = max_preco - min_preco

                    if diferenca_preco > self.__DIFERENCA_MINIMA:
                        for (
                            preco,
                            fundos_infos,
                        ) in ativo_preco_fundo.precos_fundos.items():
                            for fundo_info in fundos_infos:
                                flat_ativo_preco_fundo: FlatAtivoPrecoFundo = (
                                    FlatAtivoPrecoFundo(
                                        codigo=ativo_preco_fundo.codigo,
                                        isin=ativo_preco_fundo.isin,
                                        preco_unitario_posicao=preco,
                                        data_referente=ativo_preco_fundo.data,
                                        fundo_info=fundo_info,
                                    )
                                )
                                flat_ativos_precos_fundos.append(flat_ativo_preco_fundo)

        return flat_ativos_precos_fundos

    @staticmethod
    def __get_identificador_ativo_preco_fundo(codigo: str, data_referente: date) -> str:
        return f"{codigo}|{data_referente.strftime('%Y%m%d')}"
