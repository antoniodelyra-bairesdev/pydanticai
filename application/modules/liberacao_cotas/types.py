from dataclasses import dataclass
from datetime import date
from typing import Literal


@dataclass
class Ativo:
    isin: str | None
    codigo: str

    def __eq__(self: "Ativo", other: "Ativo") -> bool:
        return self.isin == other.isin and self.codigo == other.codigo


class AtivoRendaFixa(Ativo):
    id_titulo_britech: str | None
    id_serie_britech: str | None
    data_referente: date | None
    preco_unitario: float | None

    def __init__(
        self,
        isin: str | None,
        codigo: str,
        id_titulo_britech: str | None,
        id_serie_britech: str | None,
        data_referente: date | None,
        preco_unitario: float | None,
    ):
        self.isin = isin
        self.codigo = codigo
        self.id_titulo_britech = id_titulo_britech
        self.id_serie_britech = id_serie_britech
        self.data_referente = data_referente
        self.preco_unitario = preco_unitario

    def __eq__(self: "AtivoRendaFixa", other: "AtivoRendaFixa") -> bool:
        return (
            self.isin == other.isin
            and self.codigo == other.codigo
            and self.id_titulo_britech == other.id_titulo_britech
            and self.id_serie_britech == other.id_serie_britech
            and self.data_referente == other.data_referente
            and self.preco_unitario == other.preco_unitario
        )

    def __repr__(self) -> str:
        return f"TituloCreditoPrivado(data_referente='{self.data_referente}', isin='{self.isin}', codigo='{self.codigo}', id_titulo_britech={self.id_titulo_britech}, id_serie_britech='{self.id_serie_britech}', preco_unitario='{self.preco_unitario}')"

    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class Log:
    tipo_id: Literal[
        "fundo_xml_nome", "fundo_codigo_administrador", "fundo_codigo_corretora"
    ]
    id: str
    mensagens: list[str]


class LogMensagem:
    ESTRUTURA_XML_CORROMPIDA: str = "Estrutura do XML corrompida"
    FUNDO_PROVISAO_CORROMPIDA: str = (
        'Tag "<fundo><provisao></provisao></fundo>" corrompida'
    )
    FUNDO_PROVISAO_VALOR_CORROMPIDO: str = (
        'Tag "<fundo><provisao><valor></valor></provisao></fundo>" corrompida'
    )
    FUNDO_CORROMPIDO: str = 'Tag "<fundo></fundo>" corrompida'
    FUNDO_HEADER_CORROMPIDO: str = 'Tag "<fundo><header></header></fundo>" corrompida'
    FUNDO_HEADER_ISIN_CORROMPIDO: str = (
        'Tag "<fundo><header><isin></isin></header></fundo> corrompida'
    )
    FUNDO_HEADER_CNPJ_CORROMPIDO: str = (
        'Tag "<fundo><header><cnpj></cnpj></fundo>" corrompida'
    )
    FUNDO_HEADER_VALOR_COTA_CORROMPIDA: str = (
        'Tag "<fundo><header><valorcota></valorcota></fundo>" corrompida'
    )
    FUNDO_HEADER_DATA_POSICAO_CORROMPIDA: str = (
        'Tag "<fundo><header><dtposicao></dtposicao></header></fundo>" corrompida'
    )
    FUNDO_HEADER_QUANTIDADE_CORROMPIDA: str = (
        'Tag "<fundo><header><quantidade></quantidade></header></fundo>" corrompida'
    )
    FUNDO_HEADER_PATRIMONIO_LIQUIDO_CORROMPIDO: str = (
        'Tag "<fundo><header><patliq></patliq></header></fundo>" corrompida'
    )
    FUNDO_ACOES_CORROMPIDO: str = 'Tag "<fundo><acoes></acoes></fundo>" corrompida'
    FUNDO_OPCOES_ACOES_CORROMPIDA: str = (
        'Tag "<fundo><opcoesacoes></opcoesacoes></fundo>" corrompida'
    )
    FUNDO_FUTUROS_CORROMPIDO: str = (
        'Tag "<fundo><futuros></futuros></fundo>" corrompida'
    )
    FUNDO_OPCOES_DERIVATIVOS_CORROMPIDA: str = (
        'Tag "<fundo><opcoesderiv></opcoesderiv></fundo>" corrompida'
    )
    FUNDO_TITULO_PRIVADO_CORROMPIDO: str = (
        'Tag "<fundo><titprivado></titprivado></fundo>" corrompida'
    )
    FUNDO_DEBENTURE_CORROMPIDA: str = (
        'Tag "<fundo><debenture></debenture></fundo> corrompida'
    )
    FUNDO_TITULO_PUBLICO_CORROMPIDO: str = (
        'Tag "<fundo><titpublico></titpublico></fundo>" corrompida'
    )
    FUNDO_TITULO_PUBLICO_COMPROMISSO_CORROMPIDO: str = (
        'Tag "<fundo><titpublico><compromisso></compromisso></titpublico></fundo>" corrompida'
    )
    FUNDO_COTAS_CORROMPIDA: str = 'Tag "<fundo><cotas></cotas></fundo>" corrompida'
    FUNDO_COTAS_QUANTIDADE_DISPONIVEL_CORROMPIDA: str = (
        'Tag "<fundo><cotas><qtdisponivel></qtdisponivel></cotas></fundo>" corrompida'
    )
    FUNDO_COTAS_QUANTIDADE_GARANTIDA_CORROMPIDA: str = (
        'Tag "<fundo><cotas><qtgarantia></qtgarantia></cotas></fundo>" corrompida'
    )
    FUNDO_COTAS_PU_POSICAO_CORROMPIDO: str = (
        'Tag "<fundo><cotas><puposicao></puposicao></cotas></fundo>" corrompida'
    )

    @staticmethod
    def get_fundo_nao_encontrado_planilha_despesas_britech(
        fundo_codigo_brit: str,
    ) -> str:
        return f'Fundo (Código Britech "{(fundo_codigo_brit)}") não encontrado na planilha de despesas Britech'

    @staticmethod
    def get_fundo_futuros_nao_encontrado_depara(codigo_xml: str, isin: str) -> str:
        return f'Futuro (código: "{codigo_xml}", isin: "{isin}") não encontrado na planilha de DE/PARA de derivativos'

    @staticmethod
    def get_fundo_opcao_acao_isin_generico(codigo_xml: str, isin: str) -> str:
        return f'Opção (código: {codigo_xml}, isin: "{isin}") com ISIN genérico. Verifique se essa opção é offshore, caso seja, seu PU será calculado errado por causa do ISIN'

    @staticmethod
    def get_fundo_opcao_acao_encontrada_depara(
        codigo_xml: str, isin: str, codigo_depara: str
    ) -> str:
        return f'Opção (código: "{codigo_xml}", isin: "{isin}") encontrado na planilha de DE/PARA de derivativos. Seu código foi transformado para: "{codigo_depara}"'

    @staticmethod
    def get_fundo_opcao_acao_tipo_nao_detectado(codigo_xml: str, isin: str) -> str:
        return f'Opção (código: "{codigo_xml}", isin: "{isin}"): não foi possível detectar o tipo, se é call ou put'

    @staticmethod
    def get_fundo_futuros_com_quantidade_zerada(codigo_xml: str, isin: str) -> str:
        return f'Futuro (código: "{codigo_xml}", isin: "{isin}") com quantidade zerada'

    @staticmethod
    def get_fundo_opcao_derivativo_nao_encontrado_depara(
        codigo_xml: str, isin: str
    ) -> str:
        return f'Opção de derivativo (código: "{codigo_xml}", isin: "{isin}") não encontrado na planilha de DE/PARA de derivativos'

    @staticmethod
    def get_fundo_titulo_privado_nao_encontrado_depara_bonds(
        codigo_xml: str, isin: str
    ) -> str:
        return f'Bond (código: "{codigo_xml}", isin: "{isin}") não encontrado na planiha de DE/PARA de bonds'

    @staticmethod
    def get_fundo_codigo_britech_nao_encontrado_caracteristicas(
        id_label: str, id_value: str
    ) -> str:
        return f'Código Britech do fundo de {id_label} "{id_value}" não encontrado na planiha de características dos fundos'

    @staticmethod
    def get_fundo_administrador_nao_encontrado_caracteristicas_by_codigo_britech(
        codigo_britech: str,
    ) -> str:
        return f'Administrador do fundo de código britech "{codigo_britech}" não encontrado na planilha de características dos fundos'

    @staticmethod
    def get_fundo_administrador_vazio_caracteristicas_by_codigo_britech(
        codigo_britech: str,
    ) -> str:
        return f'Fundo de código britech "{codigo_britech}" está com o administrador vazio na planilha de características dos fundos'
