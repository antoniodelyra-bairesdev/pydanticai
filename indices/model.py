from collections import UserList
from decimal import Decimal
from sqlalchemy import INTEGER, BIGINT, BOOLEAN, TEXT, DATE, NUMERIC, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Model, SchemaIcatu
from datetime import date
from modules.medidas.model import Medida
from modules.moedas.model import Moeda
from modules.fontes_dados.model import FonteDados
from modules.integrations.enums import FontesDadosEnum
from modules.calculos.service import CalculosService


class Indice(Model, SchemaIcatu):
    __tablename__ = "indices"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    nome: Mapped[str] = mapped_column(TEXT, nullable=False)
    descricao: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    is_sintetico: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)
    data_inicio_coleta: Mapped[date] = mapped_column(DATE, nullable=False)
    atraso_coleta_dias: Mapped[int] = mapped_column(INTEGER, nullable=False)

    moeda_principal_id: Mapped[int] = mapped_column(
        INTEGER,
        ForeignKey("icatu.moedas.id"),
    )
    moeda: Mapped[Moeda] = relationship(lazy="joined")

    fonte_dado_principal_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.fontes_dados.id")
    )
    fonte_dado: Mapped[FonteDados] = relationship(lazy="joined")

    medida_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("icatu.medidas.id"))
    medida: Mapped[Medida] = relationship(lazy="joined")

    identificadores: Mapped[list["IndiceIdentificador"]] = relationship(
        back_populates="indice",
        lazy="joined",
    )

    def get_codigo_moeda(self) -> str:
        return self.moeda.codigo

    def get_identificadores_collection(self) -> "IndiceIdentificadorCollection":
        return IndiceIdentificadorCollection(self.identificadores)

    def get_nome_fonte_dados(self) -> str:
        return self.fonte_dado.get_nome_completo_fonte_dados()

    def get_identificador_by_fonte_dado(
        self, fonte_dado: FontesDadosEnum
    ) -> "IndiceIdentificador | None":
        identificadores: IndiceIdentificadorCollection = (
            self.get_identificadores_collection()
        )
        return identificadores.get_indice_identificador_by_fonte_dado(
            fonte_dado=fonte_dado
        )

    def get_data_ultima_cotacao(self, feriados=None) -> date:
        if not feriados:
            return CalculosService.get_data_d_util_menos_x_dias(
                x_dias=self.atraso_coleta_dias,
                data_input=date.today(),
            )

        return CalculosService.get_data_d_util_menos_x_dias(
            x_dias=self.atraso_coleta_dias,
            data_input=date.today(),
            feriados=feriados,
        )


class IndiceCollection(UserList["Indice"]):
    def get_nomes(self) -> list[str]:
        return [indice.nome for indice in self.data]

    def get_indice_by_fonte_dado_identificador(
        self,
        nome_completo_fonte_dado: str,
        codigo_identificador: str,
    ) -> Indice | None:
        for indice in self.data:
            for identificador in indice.get_identificadores_collection():
                if (
                    identificador.get_nome_completo_fonte_dados()
                    == nome_completo_fonte_dado
                    and identificador.codigo == codigo_identificador
                ):
                    return indice

        return None

    def get_indices_by_fonte_dado_principal(
        self, nome_completo_fonte_dado: str
    ) -> "IndiceCollection":
        return IndiceCollection(
            list(
                filter(
                    lambda indice: indice.get_nome_fonte_dados()
                    == nome_completo_fonte_dado,
                    self.data,
                )
            )
        )

    def get_indices_by_codigo_moeda(self, codigo_moeda: str) -> "IndiceCollection":
        return IndiceCollection(
            list(
                filter(
                    lambda indice: indice.get_codigo_moeda() == codigo_moeda, self.data
                )
            )
        )

    def get_nomes_fonte_dados(self) -> list[str]:
        return list(*set([indice.get_nome_fonte_dados() for indice in self.data]))

    def get_indice_by_nome(self, nome: str) -> Indice | None:
        for indice in self.data:
            if indice.nome == nome:
                return indice

        return None

    def get_menor_e_maior_data_ultima_cotacao(self, feriados=None) -> tuple[date, date]:
        datas_ultima_cotacao: list[date] = [
            indice.get_data_ultima_cotacao(feriados=feriados) for indice in self.data
        ]

        data_mais_recente_ultima_cotacao: date = max(datas_ultima_cotacao)
        data_menos_recente_ultima_cotacao: date = min(datas_ultima_cotacao)

        return (data_menos_recente_ultima_cotacao, data_mais_recente_ultima_cotacao)


class IndiceIdentificador(Model, SchemaIcatu):
    __tablename__ = "indices_identificadores"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    codigo: Mapped[str] = mapped_column(TEXT, nullable=False)
    descricao: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    indice_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.indices.id"), nullable=False
    )
    indice: Mapped[Indice] = relationship(
        back_populates="identificadores", lazy="joined"
    )

    fonte_dado_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.fontes_dados.id"), nullable=False
    )
    fonte_dado: Mapped[FonteDados] = relationship(lazy="joined")

    def get_nome_completo_fonte_dados(self) -> str:
        return self.fonte_dado.get_nome_completo_fonte_dados()

    def get_nome_fornecedor(self) -> str:
        return self.fonte_dado.get_nome_fornecedor()


class IndiceIdentificadorCollection(UserList["IndiceIdentificador"]):
    def get_indice_identificador_by_fonte_dado(
        self, fonte_dado: FontesDadosEnum
    ) -> "IndiceIdentificador | None":
        for item in self.data:
            if fonte_dado.value == item.get_nome_completo_fonte_dados():
                return item

        return None


class IndiceCotacao(Model, SchemaIcatu):
    __tablename__ = "indices_cotacoes"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, nullable=False)
    data_referente: Mapped[date] = mapped_column(DATE, nullable=False)
    cotacao: Mapped[Decimal] = mapped_column(NUMERIC, nullable=False)

    indice_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.indices.id"), nullable=False
    )
    indice: Mapped[Indice] = relationship()

    fonte_dado_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.fontes_dados.id"), nullable=False
    )
    fonte_dados: Mapped[FonteDados] = relationship()

    moeda_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("icatu.moedas.id"), nullable=False
    )
    moeda: Mapped[Moeda] = relationship()
