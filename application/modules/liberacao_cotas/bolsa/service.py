from io import BytesIO
from zipfile import ZipFile
from json import dumps
from pandas import DataFrame
from typing import Literal
from datetime import date, datetime
from xml.etree.ElementTree import fromstring, Element, ParseError

from modules.posicao.xml_anbima_401.enums import Tags
from modules.liberacao_cotas.service import LiberacaoCotasService
from modules.util.temp_file import TempFileHelper
from modules.liberacao_cotas.bolsa.helper import BolsaHelper
from modules.liberacao_cotas.types import (
    Ativo,
    Log,
    LogMensagem,
)
from modules.liberacao_cotas.bolsa.types import (
    Acao,
    Futuro,
    Opcao,
    CodigosOpcao,
    CodigosFuturo,
    OffshoreLinhaDEPARADerivativo,
)


class BolsaService(LiberacaoCotasService):
    def get_zip_buffer_bolsa_e_bmf(
        self,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        nome_arq_xlsm_depara_derivativos: str,
        usdbrl: float,
    ) -> tuple[BytesIO, str]:
        (
            dataframe_bolsa_offshore,
            dataframe_bmf_offshore,
            avisos,
        ) = self.__get_bolsa_bmf_e_avisos(
            nomes_arqs_xmls_anbima_401=nomes_arqs_xmls_anbima_401,
            nome_arq_xlsm_depara_derivativos=nome_arq_xlsm_depara_derivativos,
            usdbrl=usdbrl,
        )

        BOLSA_SHEET_NAME: str = "Equity"
        buffer_excel_bolsa_offshore: BytesIO = self._get_excel_buffer(
            dataframe=dataframe_bolsa_offshore, sheet_name=BOLSA_SHEET_NAME
        )
        BMF_SHEET_NAME: str = "Future"
        buffer_excel_bmf_offshore: BytesIO = self._get_excel_buffer(
            dataframe=dataframe_bmf_offshore, sheet_name=BMF_SHEET_NAME
        )

        zip_buffer: BytesIO = BytesIO()
        nome_arquivo_xlsx_bolsa: str = "ImportBolsa.xlsx"
        nome_arquivo_xlsx_bmf: str = "ImportBMF.xlsx"

        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr(
                nome_arquivo_xlsx_bolsa, buffer_excel_bolsa_offshore.read()
            )
            zip_file.writestr(nome_arquivo_xlsx_bmf, buffer_excel_bmf_offshore.read())

        avisos_dicts = [aviso.__dict__ for aviso in avisos]

        return (zip_buffer, dumps(avisos_dicts))

    def __get_bolsa_bmf_e_avisos(
        self,
        usdbrl: float,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        nome_arq_xlsm_depara_derivativos: str,
    ) -> tuple[DataFrame, DataFrame, list[Log]]:
        linhas_depara_derivativos: list[OffshoreLinhaDEPARADerivativo] = (
            BolsaHelper.get_linhas_depara_derivativos(nome_arq_xlsm_depara_derivativos)
        )

        acoes, opcoes_acoes, futuros, opcoes_derivativos, avisos = (
            self.__get_bolsa_bmf_e_avisos_from_xmls(
                usdbrl=usdbrl,
                nomes_arqs_xmls_anbima_401=nomes_arqs_xmls_anbima_401,
                linhas_depara_derivativos=linhas_depara_derivativos,
            )
        )

        linhas_bolsa_offshore: list[dict] = []
        for opcao in sorted(opcoes_acoes, key=lambda opcao: opcao.codigo):
            assert opcao.preco_unitario
            assert opcao.preco_exercicio

            data_referente: date = opcao.data_referente
            codigo_ativo: str = opcao.codigo
            pu_medio: float = opcao.preco_unitario
            pu_fechamento: float = opcao.preco_unitario

            linha_bolsa_offshore: dict = {
                "Data": data_referente.strftime("%d/%m/%Y"),
                "CodigoAtivo": codigo_ativo,
                "PUMedio": pu_medio,
                "PUFechamento": pu_fechamento,
            }
            linhas_bolsa_offshore.append(linha_bolsa_offshore)

            linha_bolsa_offshore_d0: dict = {
                "Data": date.strftime(date.today(), "%d/%m/%Y"),
                "CodigoAtivo": codigo_ativo,
                "PUMedio": pu_medio,
                "PUFechamento": pu_fechamento,
            }
            linhas_bolsa_offshore.append(linha_bolsa_offshore_d0)

        for acao in sorted(acoes, key=lambda acao: acao.codigo):
            assert acao.data_referente
            assert acao.preco_unitario

            data_referente: date = acao.data_referente
            codigo_ativo: str = acao.codigo
            pu_medio: float = acao.preco_unitario
            pu_fechamento: float = acao.preco_unitario

            linha_bolsa_offshore: dict = {
                "Data": data_referente.strftime("%d/%m/%Y"),
                "CodigoAtivo": codigo_ativo,
                "PUMedio": pu_medio,
                "PUFechamento": pu_fechamento,
            }
            linhas_bolsa_offshore.append(linha_bolsa_offshore)

            linha_bolsa_offshore_d0: dict = {
                "Data": date.strftime(date.today(), "%d/%m/%Y"),
                "CodigoAtivo": codigo_ativo,
                "PUMedio": pu_medio,
                "PUFechamento": pu_fechamento,
            }
            linhas_bolsa_offshore.append(linha_bolsa_offshore_d0)

        linhas_bmf_offshore: list[dict] = []
        for opcao in opcoes_derivativos:
            assert isinstance(opcao.ativo_objeto, Futuro)
            assert opcao.preco_unitario

            data_referente: date = opcao.data_referente
            codigo_ativo: str = opcao.ativo_objeto.codigo
            serie: str = opcao.codigo_serie
            preco_unitario: float = opcao.preco_unitario
            preco_unitario_corrigido: float = opcao.preco_unitario

            linha_bmf_offshore: dict = {
                "Data": data_referente.strftime("%d/%m/%Y"),
                "CodigoAtivo": codigo_ativo,
                "Serie": serie,
                "PU": preco_unitario,
                "PUCorrigido": preco_unitario_corrigido,
            }
            linhas_bmf_offshore.append(linha_bmf_offshore)

            linha_bmf_offshore_d0: dict = {
                "Data": date.strftime(date.today(), "%d/%m/%Y"),
                "CodigoAtivo": codigo_ativo,
                "Serie": serie,
                "PU": preco_unitario,
                "PUCorrigido": preco_unitario_corrigido,
            }
            linhas_bmf_offshore.append(linha_bmf_offshore_d0)

        for futuro in futuros:
            assert futuro.data_referente
            assert futuro.codigo_vencimento
            assert futuro.preco_unitario

            data_referente: date = futuro.data_referente
            codigo_ativo: str = futuro.ativo_objeto.codigo
            serie: str = futuro.codigo_vencimento
            preco_unitario: float = futuro.preco_unitario
            preco_unitario_corrigido: float = futuro.preco_unitario

            linha_bmf_offshore: dict = {
                "Data": data_referente.strftime("%d/%m/%Y"),
                "CodigoAtivo": codigo_ativo,
                "Serie": serie,
                "PU": preco_unitario,
                "PUCorrigido": preco_unitario_corrigido,
            }
            linhas_bmf_offshore.append(linha_bmf_offshore)

            linha_bmf_offshore_d0: dict = {
                "Data": date.strftime(date.today(), "%d/%m/%Y"),
                "CodigoAtivo": codigo_ativo,
                "Serie": serie,
                "PU": preco_unitario,
                "PUCorrigido": preco_unitario_corrigido,
            }
            linhas_bmf_offshore.append(linha_bmf_offshore_d0)

        dataframe_bolsa_offshore: DataFrame = DataFrame(linhas_bolsa_offshore)
        dataframe_bmf_offshore: DataFrame = DataFrame(linhas_bmf_offshore)

        return (dataframe_bolsa_offshore, dataframe_bmf_offshore, avisos)

    def __get_bolsa_bmf_e_avisos_from_xmls(
        self,
        usdbrl: float,
        nomes_arqs_xmls_anbima_401: list[tuple[str, str]],
        linhas_depara_derivativos: list[OffshoreLinhaDEPARADerivativo],
    ) -> tuple[
        list[Acao],
        list[Opcao],
        list[Futuro],
        list[Opcao],
        list[Log],
    ]:
        avisos: list[Log] = []
        acoes: list[Acao] = []
        opcoes_acoes: list[Opcao] = []
        futuros: list[Futuro] = []
        opcoes_derivativos: list[Opcao] = []

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
                continue

            if root is None:
                aviso.mensagens.append(LogMensagem.FUNDO_CORROMPIDO)
                continue

            node_data_posicao: Element | None = root.find(
                f".//{Tags.HEADER.value}/{Tags.DTPOSICAO.value}"
            )
            if node_data_posicao is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_DATA_POSICAO_CORROMPIDA)
                continue
            data_posicao: date | None = (
                datetime.strptime(node_data_posicao.text, "%Y%m%d").date()
                if node_data_posicao.text is not None
                else None
            )
            if data_posicao is None:
                aviso.mensagens.append(LogMensagem.FUNDO_HEADER_DATA_POSICAO_CORROMPIDA)
                continue

            node_acoes: list[Element] | None = list(root.findall(Tags.ACOES.value))
            if node_acoes is None:
                aviso.mensagens.append(LogMensagem.FUNDO_ACOES_CORROMPIDO.value)
                continue

            for node in node_acoes:
                if BolsaHelper.is_node_ativo_offshore(node) == False:
                    continue

                acao: Acao | None = self.__get_acao_offshore_from_xml_e_appenda_avisos(
                    node_acao=node,
                    usdbrl=usdbrl,
                    data_posicao=data_posicao,
                    aviso=aviso,
                    avisos=avisos,
                )

                if acao is not None and acao not in acoes:
                    acoes.append(acao)

            node_opcoes_acoes: list[Element] | None = list(
                root.findall(Tags.OPCOESACOES.value)
            )
            if node_opcoes_acoes is None:
                aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_ACOES_CORROMPIDA)
                continue

            for node in node_opcoes_acoes:
                opcao_acao: Opcao | None = (
                    self.__get_opcao_acao_from_xml_e_appenda_avisos(
                        node_opcao_acao=node,
                        usdbrl=usdbrl,
                        data_posicao=data_posicao,
                        aviso=aviso,
                        avisos=avisos,
                        linhas_depara_derivativos=linhas_depara_derivativos,
                    )
                )

                if opcao_acao is not None and opcao_acao not in opcoes_acoes:
                    opcoes_acoes.append(opcao_acao)

            node_futuros: list[Element] | None = list(root.findall(Tags.FUTUROS.value))
            if node_futuros is None:
                aviso.mensagens.append(LogMensagem.FUNDO_FUTUROS_CORROMPIDO)
                continue

            for node in node_futuros:
                if BolsaHelper.is_node_ativo_offshore(node) == False:
                    continue

                futuro: Futuro | None = self.__get_futuro_offshore_e_appenda_avisos(
                    node_futuro=node,
                    usdbrl=usdbrl,
                    data_posicao=data_posicao,
                    aviso=aviso,
                    avisos=avisos,
                    linhas_depara_derivativos=linhas_depara_derivativos,
                )

                if futuro is not None and futuro not in futuros:
                    futuros.append(futuro)

            node_opcoes_derivativos: list[Element] | None = list(
                root.findall(Tags.OPCOESDERIV.value)
            )
            if node_opcoes_derivativos is None:
                aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
                avisos.append(aviso)
                continue

            for node in node_opcoes_derivativos:
                opcao_derivativo: Opcao | None | Literal[-1] = (
                    self.get_opcao_derivativo_from_xml_e_appenda_avisos(
                        node_opcao_derivativo=node,
                        usdbrl=usdbrl,
                        data_posicao=data_posicao,
                        linhas_depara_derivativos=linhas_depara_derivativos,
                        aviso=aviso,
                        avisos=avisos,
                    )
                )
                if type(opcao_derivativo) == int:
                    if aviso not in avisos:
                        avisos.append(aviso)
                    continue

                if opcao_derivativo is None:
                    aviso.mensagens.append(
                        LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA
                    )
                    if aviso not in avisos:
                        avisos.append(aviso)
                    continue

                if opcao_derivativo not in opcoes_derivativos:
                    assert type(opcao_derivativo) == Opcao
                    opcoes_derivativos.append(opcao_derivativo)

        return (acoes, opcoes_acoes, futuros, opcoes_derivativos, avisos)

    def __get_acao_offshore_from_xml_e_appenda_avisos(
        self,
        node_acao: Element,
        usdbrl: float,
        data_posicao: date,
        aviso: Log,
        avisos: list[Log],
    ) -> Acao | None:
        node_codigo: Element | None = node_acao.find(Tags.CODATIVO.value)
        if node_codigo is None:
            aviso.mensagens.append(LogMensagem.FUNDO_ACOES_CORROMPIDO)
            avisos.append(aviso)
            return None
        codigo: str | None = node_codigo.text
        if codigo is None:
            aviso.mensagens.append(LogMensagem.FUNDO_ACOES_CORROMPIDO)
            avisos.append(aviso)
            return None

        node_isin: Element | None = node_acao.find(Tags.ISIN.value)
        if node_isin is None:
            aviso.mensagens.append(LogMensagem.FUNDO_ACOES_CORROMPIDO)
            avisos.append(aviso)
            return None
        isin: str | None = node_isin.text
        if isin is None:
            aviso.mensagens.append(LogMensagem.FUNDO_ACOES_CORROMPIDO)
            avisos.append(aviso)
            return None

        node_tamanho_lote: Element | None = node_acao.find(Tags.LOTE.value)
        if node_tamanho_lote is None:
            aviso.mensagens.append(LogMensagem.FUNDO_ACOES_CORROMPIDO)
            avisos.append(aviso)
            return None
        tamanho_lote: int | None = (
            int(node_tamanho_lote.text) if node_tamanho_lote.text is not None else None
        )
        if tamanho_lote is None:
            aviso.mensagens.append(LogMensagem.FUNDO_ACOES_CORROMPIDO)
            avisos.append(aviso)
            return None

        acao_node_preco_unitario_lote: Element | None = node_acao.find(
            Tags.PUPOSICAO.value
        )
        if acao_node_preco_unitario_lote is None:
            aviso.mensagens.append(LogMensagem.FUNDO_ACOES_CORROMPIDO)
            avisos.append(aviso)
            return None
        acao_preco_unitario_lote: float | None = (
            float(acao_node_preco_unitario_lote.text)
            if acao_node_preco_unitario_lote.text is not None
            else None
        )
        if acao_preco_unitario_lote is None:
            aviso.mensagens.append(LogMensagem.FUNDO_ACOES_CORROMPIDO)
            avisos.append(aviso)
            return None

        preco_unitario: float = (acao_preco_unitario_lote / tamanho_lote) / usdbrl

        acao: Acao = Acao(
            isin=isin,
            codigo=codigo,
            tamanho_lote=tamanho_lote,
            data_referente=data_posicao,
            preco_unitario=preco_unitario,
        )

        return acao

    def __get_opcao_acao_from_xml_e_appenda_avisos(
        self,
        node_opcao_acao: Element,
        usdbrl: float,
        data_posicao: date,
        aviso: Log,
        avisos: list[Log],
        linhas_depara_derivativos: list[OffshoreLinhaDEPARADerivativo],
    ) -> Opcao | None:
        node_codigo: Element | None = node_opcao_acao.find(Tags.CODATIVO.value)
        if node_codigo is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_ACOES_CORROMPIDA)
            avisos.append(aviso)
            return None
        codigo: str | None = node_codigo.text
        if codigo is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_ACOES_CORROMPIDA)
            avisos.append(aviso)
            return None

        node_isin: Element | None = node_opcao_acao.find(Tags.ISIN.value)
        if node_isin is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_ACOES_CORROMPIDA)
            avisos.append(aviso)
            return None
        isin: str | None = node_isin.text
        if isin is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_ACOES_CORROMPIDA)
            avisos.append(aviso)
            return None

        if isin.startswith("*"):
            aviso.mensagens.append(
                LogMensagem.get_fundo_opcao_acao_isin_generico(
                    codigo_xml=codigo, isin=isin
                )
            )
            avisos.append(aviso)

        node_preco_exercicio: Element | None = node_opcao_acao.find(
            Tags.PRECOEXERCICIO.value
        )
        if node_preco_exercicio is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_ACOES_CORROMPIDA)
            avisos.append(aviso)
            return None
        preco_exercicio: float | None = (
            float(node_preco_exercicio.text)
            if node_preco_exercicio.text is not None
            else None
        )
        if preco_exercicio is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_ACOES_CORROMPIDA)
            avisos.append(aviso)
            return None

        node_puposicao: Element | None = node_opcao_acao.find(Tags.PUPOSICAO.value)
        if node_puposicao is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_ACOES_CORROMPIDA)
            avisos.append(aviso)
            return None

        opcao: Opcao
        if BolsaHelper.is_node_ativo_offshore(node_codigo):
            opcao_preco_lote: float | None = (
                float(node_puposicao.text) if node_puposicao.text is not None else None
            )
            if opcao_preco_lote is None:
                aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_ACOES_CORROMPIDA)
                avisos.append(aviso)
                return None

            xml_codigos_opcao: CodigosOpcao = (
                BolsaHelper.get_codigos_opcao_acao_offshore(codigo)
            )
            xml_codigo_ativo_objeto: str = xml_codigos_opcao.codigo_ativo_objeto
            xml_codigo_serie: str = xml_codigos_opcao.codigo_serie

            depara_ativo: OffshoreLinhaDEPARADerivativo | None = (
                BolsaHelper.get_linha_depara_derivativos_by_xml_codigo_ativo_objeto(
                    xml_tag=Tags.OPCOESACOES,
                    xml_codigo_ativo_objeto=xml_codigo_ativo_objeto,
                    linhas_depara_derivativos=linhas_depara_derivativos,
                )
            )

            codigo_serie: str = xml_codigo_serie
            codigo_ativo_objeto: str = xml_codigo_ativo_objeto

            if depara_ativo:
                aviso.mensagens.append(
                    LogMensagem.get_fundo_opcao_acao_encontrada_depara(
                        codigo_xml=codigo,
                        isin=isin,
                        codigo_depara=codigo_ativo_objeto + codigo_ativo_objeto,
                    )
                )
                avisos.append(aviso)

                tamanho_lote: int = 100
                codigo_ativo_objeto = depara_ativo.xml_codigo_ativo_objeto
                if depara_ativo.tamanho_lote:
                    tamanho_lote = depara_ativo.tamanho_lote

            ativo_objeto: Acao = Acao(
                isin=None,
                codigo=codigo_ativo_objeto,
                tamanho_lote=1,
                data_referente=None,
                preco_unitario=None,
            )

            tipo_opcao: Literal["C", "P"] | None = (
                BolsaHelper.get_tipo_opcao_acao_offshore(codigo_opcao=codigo)
            )
            if tipo_opcao is None:
                aviso.mensagens.append(
                    LogMensagem.get_fundo_opcao_acao_tipo_nao_detectado(
                        codigo_xml=codigo, isin=isin
                    )
                )
                avisos.append(aviso)
                return None

            preco_unitario: float = (opcao_preco_lote / tamanho_lote) / usdbrl
            opcao = Opcao(
                isin=isin,
                ativo_objeto=ativo_objeto,
                data_referente=data_posicao,
                codigo_serie=codigo_serie,
                preco_unitario=preco_unitario,
                preco_exercicio=preco_exercicio,
                tamanho_lote=tamanho_lote,
                tipo=tipo_opcao,
            )
        else:
            opcao_preco_unitario: float | None = (
                float(node_puposicao.text) if node_puposicao.text is not None else None
            )
            if opcao_preco_unitario is None:
                aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_ACOES_CORROMPIDA)
                avisos.append(aviso)
                return None

            xml_codigos_opcao: CodigosOpcao = BolsaHelper.get_codigos_opcao_acao_b3(
                codigo
            )
            xml_codigo_ativo_objeto: str = xml_codigos_opcao.codigo_ativo_objeto
            xml_codigo_serie: str = xml_codigos_opcao.codigo_serie
            ativo_objeto: Acao = Acao(
                isin=None,
                codigo=xml_codigo_ativo_objeto,
                tamanho_lote=1,
                data_referente=None,
                preco_unitario=None,
            )

            tipo_opcao: Literal["C", "P"] | None = BolsaHelper.get_tipo_opcao_acao_b3(
                codigo_opcao=codigo
            )
            if tipo_opcao is None:
                aviso.mensagens.append(
                    LogMensagem.get_fundo_opcao_acao_tipo_nao_detectado(
                        codigo_xml=codigo, isin=isin
                    )
                )
                avisos.append(aviso)
                return None

            preco_unitario: float = opcao_preco_unitario
            opcao = Opcao(
                isin=isin,
                ativo_objeto=ativo_objeto,
                data_referente=data_posicao,
                codigo_serie=xml_codigo_serie,
                preco_unitario=preco_unitario,
                preco_exercicio=preco_exercicio,
                tamanho_lote=None,
                tipo=tipo_opcao,
            )

        return opcao

    def __get_futuro_offshore_e_appenda_avisos(
        self,
        node_futuro: Element,
        usdbrl: float,
        data_posicao: date,
        aviso: Log,
        avisos: list[Log],
        linhas_depara_derivativos: list[OffshoreLinhaDEPARADerivativo],
    ) -> Futuro | None:
        node_codigo: Element | None = node_futuro.find(Tags.ATIVO.value)
        if node_codigo is None:
            aviso.mensagens.append(LogMensagem.FUNDO_FUTUROS_CORROMPIDO)
            avisos.append(aviso)
            return None
        codigo: str | None = node_codigo.text
        if codigo is None:
            aviso.mensagens.append(LogMensagem.FUNDO_FUTUROS_CORROMPIDO)
            avisos.append(aviso)
            return None

        node_isin: Element | None = node_futuro.find(Tags.ISIN.value)
        if node_isin is None:
            aviso.mensagens.append(LogMensagem.FUNDO_FUTUROS_CORROMPIDO)
            avisos.append(aviso)
            return None
        isin: str | None = node_isin.text
        if isin is None:
            aviso.mensagens.append(LogMensagem.FUNDO_FUTUROS_CORROMPIDO)
            avisos.append(aviso)
            return None

        node_codigo_serie: Element | None = node_futuro.find(Tags.SERIE.value)
        if node_codigo_serie is None:
            aviso.mensagens.append(LogMensagem.FUNDO_FUTUROS_CORROMPIDO)
            avisos.append(aviso)
            return None
        codigo_serie: str | None = node_codigo_serie.text
        if codigo_serie is None:
            aviso.mensagens.append(LogMensagem.FUNDO_FUTUROS_CORROMPIDO)
            avisos.append(aviso)
            return None

        node_quantidade: Element | None = node_futuro.find(Tags.QUANTIDADE.value)
        if node_quantidade is None:
            aviso.mensagens.append(LogMensagem.FUNDO_FUTUROS_CORROMPIDO)
            avisos.append(aviso)
            return None
        quantidade: float | None = (
            float(node_quantidade.text) if node_quantidade.text is not None else None
        )
        if quantidade is None:
            aviso.mensagens.append(LogMensagem.FUNDO_FUTUROS_CORROMPIDO)
            avisos.append(aviso)
            return None
        if quantidade == 0:
            aviso.mensagens.append(
                LogMensagem.get_fundo_futuros_com_quantidade_zerada(
                    codigo_xml=codigo, isin=isin
                )
            )
            avisos.append(aviso)
            return None

        node_valor_posicao: Element | None = node_futuro.find(Tags.VLTOTALPOS.value)
        if node_valor_posicao is None:
            aviso.mensagens.append(LogMensagem.FUNDO_FUTUROS_CORROMPIDO)
            avisos.append(aviso)
            return None
        valor_posicao: float | None = (
            float(node_valor_posicao.text)
            if node_valor_posicao.text is not None
            else None
        )
        if valor_posicao is None:
            aviso.mensagens.append(LogMensagem.FUNDO_FUTUROS_CORROMPIDO)
            avisos.append(aviso)
            return None

        depara_ativo: OffshoreLinhaDEPARADerivativo | None = (
            BolsaHelper.get_linha_depara_derivativos_by_xml_codigo_ativo_objeto(
                xml_tag=Tags.FUTUROS,
                xml_codigo_ativo_objeto=codigo,
                linhas_depara_derivativos=linhas_depara_derivativos,
            )
        )

        if depara_ativo is None:
            aviso.mensagens.append(
                LogMensagem.get_fundo_futuros_nao_encontrado_depara(
                    codigo_xml=codigo, isin=isin
                )
            )
            avisos.append(aviso)
            return None

        codigo_vencimento: str = codigo_serie
        tamanho_lote: int | None = depara_ativo.tamanho_lote
        assert tamanho_lote

        preco_unitario: float = (valor_posicao / (quantidade * tamanho_lote)) / usdbrl

        ativo_objeto: Ativo = Ativo(isin=None, codigo=codigo)

        futuro: Futuro = Futuro(
            isin=isin,
            ativo_objeto=ativo_objeto,
            data_referente=data_posicao,
            codigo_vencimento=codigo_vencimento,
            preco_unitario=preco_unitario,
            tamanho_lote=tamanho_lote,
        )

        return futuro

    def get_opcao_derivativo_from_xml_e_appenda_avisos(
        self,
        node_opcao_derivativo: Element,
        usdbrl: float,
        data_posicao: date,
        linhas_depara_derivativos: list[OffshoreLinhaDEPARADerivativo],
        aviso: Log,
        avisos: list[Log],
    ) -> Opcao | None:
        node_codigo: Element | None = node_opcao_derivativo.find(Tags.ATIVO.value)
        if node_codigo is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
            avisos.append(aviso)
            return None
        codigo: str | None = node_codigo.text
        if codigo is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
            avisos.append(aviso)
            return None

        node_isin: Element | None = node_opcao_derivativo.find(Tags.ISIN.value)
        if node_isin is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
            avisos.append(aviso)
            return None
        isin: str | None = node_isin.text
        if isin is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
            avisos.append(aviso)
            return None

        node_preco_exercicio: Element | None = node_opcao_derivativo.find(
            Tags.PRECOEXERCICIO.value
        )
        if node_preco_exercicio is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
            avisos.append(aviso)
            return None
        preco_exercicio: float | None = (
            float(node_preco_exercicio.text)
            if node_preco_exercicio.text is not None
            else None
        )
        if preco_exercicio is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
            avisos.append(aviso)
            return None

        node_codigo_serie: Element | None = node_opcao_derivativo.find(Tags.SERIE.value)
        if node_codigo_serie is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
            avisos.append(aviso)
            return None
        xml_codigo_serie: str | None = node_codigo_serie.text
        if xml_codigo_serie is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
            avisos.append(aviso)
            return None

        node_quantidade: Element | None = node_opcao_derivativo.find(
            Tags.QUANTIDADE.value
        )
        if node_quantidade is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
            avisos.append(aviso)
            return None
        quantidade: float | None = (
            float(node_quantidade.text) if node_quantidade.text is not None else None
        )
        if quantidade is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
            avisos.append(aviso)
            return None

        node_valor_posicao: Element | None = node_opcao_derivativo.find(
            Tags.VALORFINANCEIRO.value
        )
        if node_valor_posicao is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
            avisos.append(aviso)
            return None
        valor_posicao: float | None = (
            float(node_valor_posicao.text)
            if node_valor_posicao.text is not None
            else None
        )
        if valor_posicao is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
            avisos.append(aviso)
            return None

        node_callput: Element | None = node_opcao_derivativo.find(Tags.CALLPUT.value)
        if node_callput is None:
            aviso.mensagens.append(
                LogMensagem.get_fundo_opcao_acao_tipo_nao_detectado(
                    codigo_xml=codigo, isin=isin
                )
            )
            avisos.append(aviso)
            return None
        callput: str | None = node_callput.text
        if callput is None:
            aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
            avisos.append(aviso)
            return None
        tipo_opcao: str = callput
        if tipo_opcao != "C" and tipo_opcao != "P":
            aviso.mensagens.append(
                LogMensagem.get_fundo_opcao_acao_tipo_nao_detectado(
                    codigo_xml=codigo, isin=isin
                )
            )
            avisos.append(aviso)
            return None

        opcao: Opcao
        if BolsaHelper.is_node_ativo_offshore(node_opcao_derivativo):
            xml_codigos_futuro: CodigosFuturo = BolsaHelper.get_codigos_futuros(codigo)
            xml_codigo_ativo_objeto_ativo_objeto: str = (
                xml_codigos_futuro.codigo_ativo_objeto
            )

            depara_ativo: OffshoreLinhaDEPARADerivativo | None = (
                BolsaHelper.get_linha_depara_derivativos_by_xml_codigo_ativo_objeto(
                    xml_tag=Tags.OPCOESDERIV,
                    xml_codigo_ativo_objeto=xml_codigo_ativo_objeto_ativo_objeto,
                    linhas_depara_derivativos=linhas_depara_derivativos,
                )
            )

            if depara_ativo is None:
                aviso.mensagens.append(
                    LogMensagem.get_fundo_opcao_derivativo_nao_encontrado_depara(
                        codigo_xml=codigo, isin=isin or ""
                    )
                )
                avisos.append(aviso)
                return None

            codigo_ativo_objeto_ativo_objeto: str = (
                depara_ativo.bloomberg_codigo_ativo_objeto
            )

            ativo_objeto_ativo_objeto: Ativo = Ativo(
                isin=None, codigo=codigo_ativo_objeto_ativo_objeto
            )

            ativo_objeto: Ativo = Futuro(
                isin=None,
                ativo_objeto=ativo_objeto_ativo_objeto,
                data_referente=None,
                codigo_vencimento=xml_codigos_futuro.codigo_vencimento,
                preco_unitario=None,
                tamanho_lote=None,
            )

            tamanho_lote: int | None = depara_ativo.tamanho_lote
            assert tamanho_lote

            preco_unitario: float = (
                valor_posicao / (quantidade * tamanho_lote)
            ) / usdbrl

            opcao = Opcao(
                isin=isin,
                ativo_objeto=ativo_objeto,
                data_referente=data_posicao,
                codigo_serie=xml_codigo_serie,
                preco_unitario=preco_unitario,
                preco_exercicio=preco_exercicio,
                tamanho_lote=tamanho_lote,
                tipo=tipo_opcao,
            )
        else:
            node_puposicao: Element | None = node_opcao_derivativo.find(
                Tags.PUPOSICAO.value
            )
            if node_puposicao is None:
                aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
                avisos.append(aviso)
                return None
            valor_puposicao: float | None = (
                float(node_puposicao.text) if node_puposicao.text is not None else None
            )
            if valor_puposicao is None:
                aviso.mensagens.append(LogMensagem.FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA)
                avisos.append(aviso)
                return None

            codigo_ativo_objeto_ativo_objeto: str = codigo
            ativo_objeto_ativo_objeto: Ativo = Ativo(
                isin=None, codigo=codigo_ativo_objeto_ativo_objeto
            )

            ativo_objeto = Futuro(
                isin=None,
                ativo_objeto=ativo_objeto_ativo_objeto,
                data_referente=None,
                codigo_vencimento=None,
                preco_unitario=None,
                tamanho_lote=None,
            )

            preco_unitario: float = valor_puposicao

            opcao = Opcao(
                isin=isin,
                ativo_objeto=ativo_objeto,
                data_referente=data_posicao,
                codigo_serie=xml_codigo_serie,
                preco_unitario=preco_unitario,
                preco_exercicio=preco_exercicio,
                tamanho_lote=None,
                tipo=tipo_opcao,
            )

        return opcao
