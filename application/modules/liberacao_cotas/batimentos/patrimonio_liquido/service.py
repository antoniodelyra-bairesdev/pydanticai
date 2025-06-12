from datetime import date, datetime
from decimal import Decimal
from pandas import DataFrame

from .schema import ComparacaoPLSchema, ResponseSchema
from modules.caracteristicas_fundos.service import CaracteristicasFundosService
from modules.posicao.xml_anbima_401.service import XMLAnbima401Service
from modules.posicao.xml_anbima_401.types import (
    XMLAnbima401Posicao,
    XMLAnbima401Fundo,
)
from modules.util.api_warning import APIWarning
from modules.util.caracteristicas_fundos import CaractersticasFundosHelper
from modules.util.temp_file import TempFileHelper


class BatimentoPatrimonioLiquidoService:
    def get_batimento_patrimonio_liquido(
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

        comparacoes: list[ComparacaoPLSchema] = []
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

            pl_xml: Decimal = fundo.header.patliq
            pl_calculado: Decimal = posicao.get_pl_calculado()
            diferenca_pl: Decimal = Decimal(abs(pl_xml - pl_calculado))

            comparacao: ComparacaoPLSchema = ComparacaoPLSchema(
                fundo_codigo_britech=codigo_britech,
                fundo_codigo_administrador=codigo_administrador,
                fundo_cnpj=cnpj,
                fundo_nome=nome_fundo,
                data_referente=data_posicao,
                pl_xml=pl_xml,
                pl_calculado=pl_calculado,
                diferenca_pl=diferenca_pl,
            )

            comparacoes.append(comparacao)

        response: ResponseSchema = ResponseSchema(
            batimento_pls=comparacoes, warnings=avisos if len(avisos) > 0 else None
        )

        return response
