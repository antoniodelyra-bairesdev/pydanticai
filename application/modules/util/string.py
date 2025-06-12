from typing import Any, TypedDict
from unidecode import unidecode

__SOH__ = chr(1)
__ENTER__ = "\n"
__TAB__ = "\t"


def tokenize_word(word: str):
    return "".join([frag for frag in unidecode(word.lower()).split(" ") if frag])


def get_cnpj_sem_formatacao(cnpj: str):
    return cnpj.replace(".", "").replace("-", "").replace("/", "")


def get_cnpj_com_formatacao(cnpj: str) -> str:
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def get_numero_decimal_tratado_from_numero_string(numero: str) -> float:
    n: str = numero.replace(".", "_").replace(",", "_")
    partes = n.rsplit("_", 1)
    numero_tratado: float = float(".".join(partes).replace("_", ""))

    return numero_tratado


class ErroEstruturado(TypedDict):
    resumo: str
    detalhes: list[str]


def estrutura_erros(str_erros: str, erros: dict[int, str]) -> Any:
    dtls = str_erros.replace("]", "").split("[")
    resumo = int(dtls.pop()) if len(dtls) > 0 else 0
    infos = [int(id_erro) for id_erro in dtls.pop().split(",")] if len(dtls) > 0 else []
    return ErroEstruturado(
        resumo=(erros[resumo] if resumo in erros else f"Erro {resumo}"),
        detalhes=[
            (erros[info] if info in erros else f"Erro {resumo}" if info != 0 else "")
            for info in infos
        ],
    )
