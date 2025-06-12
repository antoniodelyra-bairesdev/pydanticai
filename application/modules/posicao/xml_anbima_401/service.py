from io import BytesIO
from xsdata.formats.dataclass.parsers.config import ParserConfig
from xsdata.formats.dataclass.context import XmlContext
from xsdata.formats.dataclass.parsers import XmlParser
from zipfile import ZipFile

from modules.util.temp_file import TempFileHelper
from .types import XMLAnbima401Posicao


class XMLAnbima401Service:
    def cria_arquivos_xml_fundos_from_zips(
        self, buffers_arquivos_zip: list[BytesIO], identificador_arqs_temp: str
    ) -> list[tuple[str, str]]:
        PREFIXO_FUNDO: str = "FD"

        nomes_arqs_tuples: list[tuple] = []

        for buffer_arquivo_zip in buffers_arquivos_zip:
            with ZipFile(buffer_arquivo_zip, "r") as zip_ref:
                for nome_arquivo_original in zip_ref.namelist():
                    if nome_arquivo_original.startswith(PREFIXO_FUNDO):
                        with zip_ref.open(nome_arquivo_original) as file:
                            conteudo_arquivo: bytes = file.read()
                            nome_arquivo_temporario: str = TempFileHelper.sync_cria(
                                conteudo_arquivo, identificador_arqs_temp
                            )

                            nomes_arqs_tuples.append(
                                (nome_arquivo_temporario, nome_arquivo_original)
                            )

        return nomes_arqs_tuples

    def get_cnpj_from_nome_arquivo(self, nome_arquivo: str) -> str:
        partes_nome_arquivo: list[str] = nome_arquivo.split("_")
        cnpj: str = partes_nome_arquivo[0][2:]
        return cnpj

    def get_posicao(self, xml_anbima_401_buffer: bytes) -> XMLAnbima401Posicao:
        config = ParserConfig(fail_on_converter_warnings=True)
        context = XmlContext()
        parser = XmlParser(context=context, config=config)

        posicao: XMLAnbima401Posicao = parser.from_bytes(
            xml_anbima_401_buffer, XMLAnbima401Posicao
        )
        return posicao
