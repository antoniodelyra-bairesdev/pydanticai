from pandas import DataFrame

from .schema import ResponseSchema
from modules.caracteristicas_fundos.service import CaracteristicasFundosService
from modules.caracteristicas_fundos.types import FundoInfo
from modules.util.caracteristicas_fundos import CaractersticasFundosHelper
from modules.posicao.xml_anbima_401.service import XMLAnbima401Service
from modules.util.temp_file import TempFileHelper


class BatimentoXmlsService:
    def get_batimento_xmls(
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

        service_caracteristicas_fundos: CaracteristicasFundosService = (
            CaracteristicasFundosService(
                dataframe_caracteristicas_fundos=dataframe_caracteristicas_fundos
            )
        )
        service_xml_anbima_401: XMLAnbima401Service = XMLAnbima401Service()

        fundos_infos: list[FundoInfo] = (
            service_caracteristicas_fundos.get_fundos_infos()
        )
        fundos_infos_sem_xml: list[FundoInfo] = []
        nomes_arqs_originais: list[str] = [
            nomes_arq[1] for nomes_arq in nomes_arqs_xmls_anbima_401
        ]
        for fundo_info in fundos_infos:
            is_cnpj_in_nomes_arqs: bool = self.__is_cnpj_in_nomes_arqs(
                cnpj=fundo_info.cnpj,
                nomes_arqs=nomes_arqs_originais,
                service_xml_anbima_401=service_xml_anbima_401,
            )

            if is_cnpj_in_nomes_arqs is False:
                fundos_infos_sem_xml.append(fundo_info)

        return ResponseSchema(fundos_sem_xml=fundos_infos_sem_xml)

    def __is_cnpj_in_nomes_arqs(
        self,
        cnpj: str,
        nomes_arqs: list[str],
        service_xml_anbima_401: XMLAnbima401Service,
    ) -> bool:
        for nome_arq in nomes_arqs:
            if cnpj == service_xml_anbima_401.get_cnpj_from_nome_arquivo(nome_arq):
                return True

        return False
