from datetime import date, datetime
from io import BytesIO
from json import dumps
from pandas import DataFrame
from xml.etree.ElementTree import fromstring, Element, ParseError
from zipfile import ZipFile

from modules.posicao.xml_anbima_401.enums import Tags
from modules.calculos.service import CalculosService
from modules.util.string import get_cnpj_com_formatacao
from modules.util.temp_file import TempFileHelper
from modules.util.feriados_financeiros_numpy import feriados
from modules.depara.cotas.service import DeparaCotasService
from modules.depara.cotas.types import LinhaDeparaCotaFundo
from .types import CotaFundo
from ..types import Log, LogMensagem
from ..service import LiberacaoCotasService


class CotasService(LiberacaoCotasService):
    def get_zip_buffer_cotas_fundos(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        nome_arq_xlsx_depara_cotas_fundos: str,
        nome_arq_xls_caracteristicas_fundos: str,
    ) -> tuple[BytesIO, str]:
        buffer_depara_cotas_fundos: bytes = TempFileHelper.get_conteudo_e_deleta(
            nome_arq_xlsx_depara_cotas_fundos
        )
        service_depara_cotas: DeparaCotasService = DeparaCotasService(
            buffer_xlsx_depara_cotas=buffer_depara_cotas_fundos
        )

        linhas_depara_cotas_fundos: list[LinhaDeparaCotaFundo] = (
            service_depara_cotas.get_linhas_depara_cotas_fundos()
        )

        dataframe_caracteristicas_fundos: DataFrame = (
            self._get_dataframe_caracteristicas_fundos(
                nome_arq_xls_caracteristicas_fundos
            )
        )
        dataframe_cotas_fundos, avisos = self.__get_cotas_fundos_e_avisos(
            service_depara_cotas=service_depara_cotas,
            nomes_arqs_xmls_anbima_401=nomes_arqs_xmls_anbima_401,
            linhas_depara_cotas_fundos=linhas_depara_cotas_fundos,
            dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
        )

        SHEET_NAME: str = "HISTORICO_COTA"
        buffer_excel_cotas: BytesIO = self._get_excel_buffer(
            dataframe=dataframe_cotas_fundos, sheet_name=SHEET_NAME
        )

        zip_buffer: BytesIO = BytesIO()
        nome_arq_xlsx_cotas: str = "ImportacaoHistoricoCota.xlsx"

        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr(nome_arq_xlsx_cotas, buffer_excel_cotas.read())

        avisos_dicts = [aviso.__dict__ for aviso in avisos]

        return (zip_buffer, dumps(avisos_dicts))

    def __get_cotas_fundos_e_avisos(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        service_depara_cotas: DeparaCotasService,
        linhas_depara_cotas_fundos: list[LinhaDeparaCotaFundo],
        dataframe_caracteristicas_fundos: DataFrame,
    ) -> tuple[DataFrame, list[Log]]:
        cotas_fundos, avisos = self.__get_cotas_fundos_e_avisos_from_xmls(
            nomes_arqs_xmls_anbima_401=nomes_arqs_xmls_anbima_401,
            service_depara_cotas=service_depara_cotas,
            linhas_depara_cotas_fundos=linhas_depara_cotas_fundos,
            dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
        )

        cotas_fundos_com_datas_ate_d0 = self.__get_fundos_cotas_com_datas_ate_d0(
            cotas_fundos
        )

        linhas_cotas_fundos_com_datas_ate_d0: list[dict] = []
        for cota_fundo in cotas_fundos_com_datas_ate_d0:
            linha_cota_fundo: dict = {
                "IdCarteira": int(cota_fundo.codigo_britech),
                "Data": date.strftime(cota_fundo.data_referente, "%d/%m/%Y"),
                "CotaLiquida": cota_fundo.preco_unitario,
                "PL": (
                    cota_fundo.patrimonio_liquido
                    if cota_fundo.is_externo is False
                    else ""
                ),
                "QuantidadeFechamento": (
                    cota_fundo.quantidade if cota_fundo.is_externo is False else ""
                ),
                "CotaBruta": (
                    cota_fundo.preco_unitario if cota_fundo.is_externo is False else ""
                ),
                "IdSerie": "",
            }
            linhas_cotas_fundos_com_datas_ate_d0.append(linha_cota_fundo)

        dataframe_cotas_fundos: DataFrame = DataFrame(
            linhas_cotas_fundos_com_datas_ate_d0
        )

        return (dataframe_cotas_fundos, avisos)

    def __get_cotas_fundos_e_avisos_from_xmls(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        service_depara_cotas: DeparaCotasService,
        linhas_depara_cotas_fundos: list[LinhaDeparaCotaFundo],
        dataframe_caracteristicas_fundos: DataFrame,
    ) -> tuple[list[CotaFundo], list[Log]]:
        avisos: list[Log] = []
        cotas_fundos: list[CotaFundo] = []

        for i in range(0, len(nomes_arqs_xmls_anbima_401)):
            nome_arq = nomes_arqs_xmls_anbima_401[i][0]
            nome_arq_original = nomes_arqs_xmls_anbima_401[i][1]
            aviso: Log = Log(
                tipo_id="fundo_xml_nome", id=nome_arq_original, mensagens=[]
            )

            buffer_xml: bytes = TempFileHelper.get_conteudo_e_deleta(nome_arq)
            try:
                root: Element | None = fromstring(buffer_xml).find(Tags.FUNDO.value)
            except ParseError:
                aviso.mensagens.append(LogMensagem.ESTRUTURA_XML_CORROMPIDA)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            if root is None:
                aviso.mensagens.append(LogMensagem.FUNDO_CORROMPIDO)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            node_header: Element | None = root.find(Tags.HEADER.value)
            if node_header is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_CORROMPIDO)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            node_data_posicao: Element | None = node_header.find(Tags.DTPOSICAO.value)
            if node_data_posicao is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_DATA_POSICAO_CORROMPIDA)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue
            data_posicao: date | None = (
                datetime.strptime(node_data_posicao.text, "%Y%m%d").date()
                if node_data_posicao.text is not None
                else None
            )
            if data_posicao is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_DATA_POSICAO_CORROMPIDA)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            cota_fundo: CotaFundo | None = self.__get_cota_fundo_e_appenda_avisos(
                node_header=node_header,
                dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
                data_posicao=data_posicao,
                aviso=aviso,
                avisos=avisos,
            )

            if (
                cota_fundo is not None
                and cota_fundo.is_externo is False
                and cota_fundo not in cotas_fundos
            ):
                cotas_fundos.append(cota_fundo)

                codigo_britech_fundo_espelho: str | None = (
                    self.__get_codigo_britech_fundo_espelho_by_id_carteira(
                        id_carteira=cota_fundo.codigo_britech,
                        linhas_depara_cotas=linhas_depara_cotas_fundos,
                    )
                )

                if codigo_britech_fundo_espelho:
                    cota_fundo_espelho: CotaFundo = CotasService.get_fundo_cota_espelho(
                        id_carteira_fundo_espelho=codigo_britech_fundo_espelho,
                        cota_fundo=cota_fundo,
                    )
                    if (
                        cota_fundo_espelho not in cotas_fundos
                        and cota_fundo.is_externo is False
                    ):
                        cotas_fundos.append(cota_fundo_espelho)

            node_cotas_fundos: list[Element] | None = root.findall(Tags.COTAS.value)
            if node_cotas_fundos is None:
                aviso.mensagens.append(LogMensagem.FUNDO_COTAS_CORROMPIDA)
                if aviso not in avisos:
                    avisos.append(aviso)
                continue

            for node in node_cotas_fundos:
                ativo_cota_fundo: CotaFundo | None = (
                    self.__get_ativo_cota_fundo_e_appenda_avisos(
                        node_cotas=node,
                        service_depara_cotas=service_depara_cotas,
                        data_referente=data_posicao,
                        dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
                        aviso=aviso,
                        avisos=avisos,
                    )
                )

                if (
                    ativo_cota_fundo is not None
                    and ativo_cota_fundo.is_externo
                    and ativo_cota_fundo not in cotas_fundos
                ):
                    cotas_fundos.append(ativo_cota_fundo)

        return (cotas_fundos, avisos)

    def __get_cota_fundo_e_appenda_avisos(
        self,
        node_header: Element,
        dataframe_caracteristicas_fundos: DataFrame,
        data_posicao: date,
        aviso: Log,
        avisos: list[Log],
    ) -> CotaFundo | None:
        node_isin: Element | None = node_header.find(Tags.ISIN.value)
        if node_isin is None:
            aviso.mensagens.append(LogMensagem.FUNDO_HEADER_ISIN_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        isin: str | None = node_isin.text
        if isin is None:
            aviso.mensagens.append(LogMensagem.FUNDO_HEADER_ISIN_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        node_cnpj: Element | None = node_header.find(Tags.CNPJ.value)
        if node_cnpj is None:
            aviso.mensagens.append(LogMensagem.FUNDO_HEADER_CNPJ_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        cnpj: str | None = node_cnpj.text
        if cnpj is None:
            aviso.mensagens.append(LogMensagem.FUNDO_HEADER_CNPJ_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        node_quantidade: Element | None = node_header.find(Tags.QUANTIDADE.value)
        if node_quantidade is None:
            aviso.mensagens.append(LogMensagem.FUNDO_HEADER_QUANTIDADE_CORROMPIDA)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        quantidade: float | None = (
            float(node_quantidade.text) if node_quantidade.text is not None else None
        )
        if quantidade is None:
            aviso.mensagens.append(LogMensagem.FUNDO_HEADER_QUANTIDADE_CORROMPIDA)
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        node_valor_cota: Element | None = node_header.find(Tags.VALORCOTA.value)
        if node_valor_cota is None:
            aviso.mensagens.append(LogMensagem.FUNDO_HEADER_VALOR_COTA_CORROMPIDA)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        valor_cota: float | None = (
            float(node_valor_cota.text) if node_valor_cota.text is not None else None
        )
        if valor_cota is None:
            aviso.mensagens.append(LogMensagem.FUNDO_HEADER_VALOR_COTA_CORROMPIDA)
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        node_patrimonio_liquido: Element | None = node_header.find(Tags.PATLIQ.value)
        if node_patrimonio_liquido is None:
            aviso.mensagens.append(
                LogMensagem.FUNDO_HEADER_PATRIMONIO_LIQUIDO_CORROMPIDO
            )
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        patrimonio_liquido: float | None = (
            float(node_patrimonio_liquido.text)
            if node_patrimonio_liquido.text is not None
            else None
        )
        if patrimonio_liquido is None:
            aviso.mensagens.append(
                LogMensagem.FUNDO_HEADER_PATRIMONIO_LIQUIDO_CORROMPIDO
            )
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        codigo_britech: str | None = self._get_fundo_codigo_britech_by_cnpj(
            cnpj=cnpj,
            dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
        )
        if codigo_britech is None:
            aviso.mensagens.append(
                LogMensagem.get_fundo_codigo_britech_nao_encontrado_caracteristicas(
                    "cnpj", get_cnpj_com_formatacao(cnpj)
                )
            )
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        cota_fundo: CotaFundo = CotaFundo(
            isin=isin,
            codigo_britech=codigo_britech,
            cnpj=cnpj,
            quantidade=quantidade,
            preco_unitario=valor_cota,
            patrimonio_liquido=patrimonio_liquido,
            is_externo=self.__is_fundo_externo(
                cnpj=cnpj,
                dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
            ),
            nivel_risco=None,
            data_referente=data_posicao,
        )

        return cota_fundo

    def __get_ativo_cota_fundo_e_appenda_avisos(
        self,
        node_cotas: Element,
        service_depara_cotas: DeparaCotasService,
        data_referente: date,
        dataframe_caracteristicas_fundos: DataFrame,
        aviso: Log,
        avisos: list[Log],
    ) -> CotaFundo | None:
        node_isin: Element | None = node_cotas.find(Tags.ISIN.value)
        if node_isin is None:
            aviso.mensagens.append(LogMensagem.FUNDO_HEADER_ISIN_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        isin: str | None = node_isin.text
        if isin is None:
            aviso.mensagens.append(LogMensagem.FUNDO_HEADER_ISIN_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        node_cnpj: Element | None = node_cotas.find(Tags.CNPJFUNDO.value)
        if node_cnpj is None:
            aviso.mensagens.append(LogMensagem.FUNDO_HEADER_CNPJ_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        cnpj: str | None = node_cnpj.text
        if cnpj is None:
            aviso.mensagens.append(LogMensagem.FUNDO_HEADER_CNPJ_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        pass

        depara_fundo_cota: LinhaDeparaCotaFundo | None = (
            service_depara_cotas.get_linha_depara_cota_fundo_by_isin(isin=isin)
        )
        if depara_fundo_cota is None:
            aviso.mensagens.append(
                DeparaCotasService.get_fundo_codigo_britech_nao_encontrado_depara_cotas(
                    isin
                )
            )
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        node_preco_unitario_posicao: Element | None = node_cotas.find(
            Tags.PUPOSICAO.value
        )
        if node_preco_unitario_posicao is None:
            aviso.mensagens.append(LogMensagem.FUNDO_COTAS_PU_POSICAO_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        preco_unitario: float | None = (
            float(node_preco_unitario_posicao.text)
            if node_preco_unitario_posicao.text is not None
            else None
        )
        if preco_unitario is None:
            aviso.mensagens.append(LogMensagem.FUNDO_COTAS_PU_POSICAO_CORROMPIDO)
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        node_quantidade_disponivel: Element | None = node_cotas.find(
            Tags.QTDISPONIVEL.value
        )
        if node_quantidade_disponivel is None:
            aviso.mensagens.append(
                LogMensagem.FUNDO_COTAS_QUANTIDADE_DISPONIVEL_CORROMPIDA
            )
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        quantidade_disponivel: float | None = (
            float(node_quantidade_disponivel.text)
            if node_quantidade_disponivel.text is not None
            else None
        )
        if quantidade_disponivel is None:
            aviso.mensagens.append(
                LogMensagem.FUNDO_COTAS_QUANTIDADE_DISPONIVEL_CORROMPIDA
            )
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        node_quantidade_garantia: Element | None = node_cotas.find(
            Tags.QTGARANTIA.value
        )
        if node_quantidade_garantia is None:
            aviso.mensagens.append(
                LogMensagem.FUNDO_COTAS_QUANTIDADE_GARANTIDA_CORROMPIDA
            )
            if aviso not in avisos:
                avisos.append(aviso)
            return None
        quantidade_garantia: float | None = (
            float(node_quantidade_garantia.text)
            if node_quantidade_garantia.text is not None
            else None
        )
        if quantidade_garantia is None:
            aviso.mensagens.append(
                LogMensagem.FUNDO_COTAS_QUANTIDADE_GARANTIDA_CORROMPIDA
            )
            if aviso not in avisos:
                avisos.append(aviso)
            return None

        quantidade = quantidade_disponivel + quantidade_garantia

        cota_fundo: CotaFundo = CotaFundo(
            isin=isin,
            codigo_britech=depara_fundo_cota.id_carteira,
            cnpj=cnpj,
            quantidade=quantidade,
            preco_unitario=preco_unitario,
            patrimonio_liquido=None,
            is_externo=self.__is_fundo_externo(
                cnpj=cnpj,
                dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos,
            ),
            nivel_risco=None,
            data_referente=data_referente,
        )

        return cota_fundo

    @staticmethod
    def get_fundo_cota_espelho(
        id_carteira_fundo_espelho: str, cota_fundo: CotaFundo
    ) -> CotaFundo:
        cota_fundo_espelho: CotaFundo = CotaFundo(
            isin=cota_fundo.isin,
            codigo_britech=id_carteira_fundo_espelho,
            cnpj=cota_fundo.cnpj,
            quantidade=cota_fundo.quantidade,
            preco_unitario=cota_fundo.preco_unitario,
            patrimonio_liquido=cota_fundo.patrimonio_liquido,
            is_externo=False,
            nivel_risco=cota_fundo.nivel_risco,
            data_referente=cota_fundo.data_referente,
        )

        return cota_fundo_espelho

    def __is_fundo_externo(
        self, cnpj: str, dataframe_caracteristicas_fundos: DataFrame
    ) -> bool:
        codigo_britech: str | None = self._get_fundo_codigo_britech_by_cnpj(
            cnpj=cnpj, dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos
        )
        return True if codigo_britech is None else False

    def __get_fundos_cotas_com_datas_ate_d0(
        self, fundos_cotas: list[CotaFundo]
    ) -> list[CotaFundo]:
        fundos_cotas_com_datas_ate_d0: list[CotaFundo] = []

        for cota_fundo in fundos_cotas:
            fundos_cotas_com_datas_ate_d0.append(cota_fundo)

            d0_util: date = CalculosService.get_data_d_util_menos_x_dias(
                x_dias=0,
                data_input=date.today(),
                feriados=feriados,
            )
            data_referente: date = cota_fundo.data_referente
            data_atual: date = data_referente

            contador: int = 0

            while data_atual != d0_util and contador < 2:
                data_atual = CalculosService.get_data_d_util_mais_x_dias(
                    x_dias=1,
                    data_input=data_atual,
                    feriados=feriados,
                )

                cota_fundo_com_data_avancada: CotaFundo = CotaFundo(
                    isin=cota_fundo.isin,
                    codigo_britech=cota_fundo.codigo_britech,
                    cnpj=cota_fundo.cnpj,
                    quantidade=cota_fundo.quantidade,
                    preco_unitario=cota_fundo.preco_unitario,
                    patrimonio_liquido=cota_fundo.patrimonio_liquido,
                    is_externo=cota_fundo.is_externo,
                    nivel_risco=cota_fundo.nivel_risco,
                    data_referente=data_atual,
                )
                if (
                    cota_fundo_com_data_avancada not in fundos_cotas_com_datas_ate_d0
                    and cota_fundo_com_data_avancada not in fundos_cotas
                ):
                    fundos_cotas_com_datas_ate_d0.append(cota_fundo_com_data_avancada)

                contador = contador + 1

        return fundos_cotas_com_datas_ate_d0

    def __get_codigo_britech_fundo_espelho_by_id_carteira(
        self,
        id_carteira: str,
        linhas_depara_cotas: list[LinhaDeparaCotaFundo],
    ) -> str | None:
        for linha in linhas_depara_cotas:
            if id_carteira == linha.id_carteira:
                if (
                    linha.codigo_britech_fundo_espelho != ""
                    and linha.codigo_britech_fundo_espelho is not None
                    and linha.codigo_britech_fundo_espelho != "nan"
                ):
                    return linha.codigo_britech_fundo_espelho
                else:
                    return None

        return None
