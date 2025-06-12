from typing import Literal

from .types import CodigosOpcao, CodigosFuturo


class XMLAnbima401OffshoreService:
    def get_tipo_opcao_acao_b3(self, codigo_opcao: str) -> Literal["C", "P"] | None:
        for char in reversed(codigo_opcao):
            if "A" <= char <= "L":
                return "C"
            if "M" <= char <= "X":
                return "P"

        return None

    def get_tipo_opcao_acao_offshore(
        self, codigo_opcao: str
    ) -> Literal["C", "P"] | None:
        for char in reversed(codigo_opcao):
            if char == "C":
                return "C"
            if char == "P":
                return "P"

        return None

    def get_codigos_opcao_acao_offshore(self, xml_codigo: str) -> CodigosOpcao:
        indice_digito_call_ou_put: int
        if xml_codigo.rfind("C") != -1:
            indice_digito_call_ou_put = xml_codigo.rfind("C")
        elif xml_codigo.rfind("P") != -1:
            indice_digito_call_ou_put = xml_codigo.rfind("P")
        else:
            indice_digito_call_ou_put = -1

        LENGTH_CODIGO_VENCIMENTO = 6
        assert LENGTH_CODIGO_VENCIMENTO < indice_digito_call_ou_put

        indice_comeco_codigo_vencimento: int = (
            indice_digito_call_ou_put - LENGTH_CODIGO_VENCIMENTO
        )
        codigo_ativo_objeto: str = xml_codigo[:indice_comeco_codigo_vencimento]
        codigo_serie: str = xml_codigo[indice_comeco_codigo_vencimento:]

        return CodigosOpcao(
            codigo_ativo_objeto=codigo_ativo_objeto, codigo_serie=codigo_serie
        )

    def get_codigos_opcao_acao_b3(self, xml_codigo: str) -> CodigosOpcao:
        indice_digito_call_ou_put: int | None = None
        for i in range(len(xml_codigo) - 1, 0, -1):
            char = xml_codigo[i]

            if "A" <= char <= "X":
                indice_digito_call_ou_put = i

        assert indice_digito_call_ou_put
        codigo_ativo_objeto: str = xml_codigo[:indice_digito_call_ou_put]
        codigo_serie: str = xml_codigo[indice_digito_call_ou_put:]

        return CodigosOpcao(
            codigo_ativo_objeto=codigo_ativo_objeto, codigo_serie=codigo_serie
        )

    def get_codigos_futuros(self, xml_codigo: str) -> CodigosFuturo:
        codigo_ativo_objeto: str = xml_codigo[:-2]
        codigo_vencimento: str = xml_codigo[-2:]

        return CodigosFuturo(
            codigo_ativo_objeto=codigo_ativo_objeto, codigo_vencimento=codigo_vencimento
        )
