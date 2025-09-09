import config.database as db

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from http import HTTPStatus
from typing import Any, Callable, Literal, TypedDict

from modules.calculos.service import CalculosService


from modules.util.datas import str_ymd_to_date
from modules.util.queries import (
    ColType,
    mapeamento_filtros,
    mapeamento_ordenacao,
    OrderingType,
)
from sqlalchemy.exc import IntegrityError

from .model import (
    Ativo,
    AtivoFluxo,
    AtivoFluxoTipo,
    AtivoIndice,
    AtivoTipo,
    Emissor,
)

from .schema import (
    GrupoSchema,
    InsertAssetSchema,
    InsertEmissorSchema,
    InsertGrupoSchema,
    InsertSetorSchema,
    SetorSchema,
    UpdateAssetSchema,
    UpdateEmissorSchema,
)

from .enums import SideOperacao

from fastapi.exceptions import HTTPException
from fastapi import BackgroundTasks

from .schema import (
    IndiceAtivosSchema,
    TipoEventoSchema,
    TipoAtivosSchema,
)

from .repository import AtivosRepository

from modules.notifications.schema import NotificationSchema
from modules.notifications.service import NotificationService
from modules.notifications.repository import NotificationRepository


@dataclass
class AtivosService:
    ativos_repository: AtivosRepository
    background_tasks: BackgroundTasks

    async def lista_ativos(
        self,
        deslocamento: int,
        quantidade: int,
        dados_ordenacao: list[tuple[str, OrderingType]],
        filtros: dict[str, tuple[str, list[str]]],
    ):
        mapeamento_colunas: dict[str, ColType] = {
            "codigo": Ativo.codigo,
            "emissor": Emissor.nome.collate("pt-BR-x-icu"),
            "indice": AtivoIndice.nome.collate("pt-BR-x-icu"),
            "tipo": AtivoTipo.nome.collate("pt-BR-x-icu"),
            "valor_emissao": Ativo.valor_emissao,
            "data_emissao": Ativo.data_emissao,
            "inicio_rentabilidade": Ativo.inicio_rentabilidade,
            "data_vencimento": Ativo.data_vencimento,
            "taxa": Ativo.taxa,
            "apelido": Ativo.apelido.collate("pt-BR-x-icu"),
            "isin": Ativo.isin,
            "serie": Ativo.serie,
            "emissao": Ativo.emissao,
        }
        conversao: dict[str, Callable[[Any], Any]] = {
            "valor_emissao": float,
            "data_emissao": str_ymd_to_date,
            "inicio_rentabilidade": str_ymd_to_date,
            "data_vencimento": str_ymd_to_date,
            "taxa": float,
        }
        ordem_ordenacao = mapeamento_ordenacao(dados_ordenacao, mapeamento_colunas)
        filtros_orm = mapeamento_filtros(filtros, mapeamento_colunas, conversao)
        colunas_solicitadas = {coluna for coluna, _ in dados_ordenacao}
        if "codigo" not in colunas_solicitadas:
            ordem_ordenacao.append(Ativo.codigo.asc())
        return await self.ativos_repository.lista_ativos(
            deslocamento, quantidade, ordem_ordenacao, filtros_orm
        )

    async def lista_eventos(
        self,
        deslocamento: int,
        quantidade: int,
        dados_ordenacao: list[tuple[str, OrderingType]],
        filtros: dict[str, tuple[str, list[str]]],
    ):
        mapeamento_colunas: dict[str, ColType] = {
            "ativo_codigo": AtivoFluxo.ativo_codigo,
            "data_pagamento": AtivoFluxo.data_pagamento,
            "tipo_evento": AtivoFluxoTipo.nome,
            "percentual": AtivoFluxo.percentual,
            "pu_evento": AtivoFluxo.pu_evento,
            "pu_calculado": AtivoFluxo.pu_calculado,
        }
        conversao: dict[str, Callable[[Any], Any]] = {
            "data_pagamento": str_ymd_to_date,
            "percentual": float,
            "pu_evento": float,
            "pu_calculado": float,
        }
        ordem_ordenacao = mapeamento_ordenacao(dados_ordenacao, mapeamento_colunas)
        filtros_orm = mapeamento_filtros(filtros, mapeamento_colunas, conversao)
        colunas_solicitadas = {coluna for coluna, _ in dados_ordenacao}
        if "data_pagamento" not in colunas_solicitadas:
            ordem_ordenacao.append(AtivoFluxo.data_pagamento.desc())
        ordem_ordenacao.append(AtivoFluxo.id.asc())
        return await self.ativos_repository.lista_eventos(
            deslocamento, quantidade, ordem_ordenacao, filtros_orm
        )

    async def lista_codigos(self):
        codigos = await self.ativos_repository.lista_codigos()
        return [*codigos]

    async def nomes_emissores(self):
        nomes = await self.ativos_repository.nomes_emissores()
        return [{"id": id, "nome": nome} for id, nome in nomes]

    async def ativo(self, codigo: str):
        ativo = await self.ativos_repository.ativo(codigo)
        if not ativo:
            raise HTTPException(HTTPStatus.NOT_FOUND)
        return ativo

    async def tipo_evento(self, supported: bool = True) -> list[TipoEventoSchema]:
        tipos = await self.ativos_repository.tipo_evento(supported)
        return [TipoEventoSchema.from_model(tipo) for tipo in tipos]

    async def tipo_ativos(self) -> list[TipoAtivosSchema]:
        tipos = await self.ativos_repository.tipo_ativos()
        return [TipoAtivosSchema(id=tipo.id, nome=tipo.nome) for tipo in tipos]

    async def indice_ativos(self) -> list[IndiceAtivosSchema]:
        indices = await self.ativos_repository.indices()
        return [
            IndiceAtivosSchema(id=indice.id, nome=indice.nome) for indice in indices
        ]

    async def total_ativos(self):
        return await self.ativos_repository.total_ativos()

    async def total_eventos(self):
        return await self.ativos_repository.total_eventos()

    async def transacao(
        self,
        deletar_schema: list[str],
        atualizar_schema: list[UpdateAssetSchema],
        inserir_schema: list[InsertAssetSchema],
    ):
        datas_fornecidas: list[date] = []
        for atualizado in atualizar_schema:
            datas_fornecidas += [
                atualizado.data_emissao,
                atualizado.inicio_rentabilidade,
                atualizado.data_vencimento,
            ] + [
                evento.data_pagamento
                for evento in atualizado.fluxos.added + atualizado.fluxos.modified
            ]
        for inserido in inserir_schema:
            datas_fornecidas += [
                inserido.data_emissao,
                inserido.inicio_rentabilidade,
                inserido.data_vencimento,
            ] + [evento.data_pagamento for evento in inserido.fluxos]

        datas_corrigidas = CalculosService.dias_uteis_seguintes(datas_fornecidas)

        date_i = 0
        for atualizado in atualizar_schema:
            atualizado.data_emissao = datas_corrigidas[date_i]
            atualizado.inicio_rentabilidade = datas_corrigidas[date_i + 1]
            atualizado.data_vencimento = datas_corrigidas[date_i + 2]
            date_i += 3
            for evento in atualizado.fluxos.added + atualizado.fluxos.modified:
                evento.data_pagamento = datas_corrigidas[date_i]
                date_i += 1

        for inserido in inserir_schema:
            inserido.data_emissao = datas_corrigidas[date_i]
            inserido.inicio_rentabilidade = datas_corrigidas[date_i + 1]
            inserido.data_vencimento = datas_corrigidas[date_i + 2]
            date_i += 3
            for evento in inserido.fluxos:
                evento.data_pagamento = datas_corrigidas[date_i]
                date_i += 1

        try:
            await self.ativos_repository.transacao(
                deletar_schema, atualizar_schema, inserir_schema
            )
        except IntegrityError as err:
            # Entradas duplicadas
            failure = str(err._message()).split("=")
            failure = failure[1] if len(failure) >= 2 else "=".join(failure)
            raise HTTPException(HTTPStatus.CONFLICT, failure)

    async def emissores(self, deslocamento: int, quantidade: int):
        emissores, total = await self.ativos_repository.emissores(
            deslocamento, quantidade
        )
        return emissores, total

    class UsuarioEmissor(TypedDict):
        analista_id: int
        user_id: int | None
        emissor_id: int
        emissor_nome: str
        atualizacao: Literal["alocado", "desalocado", "atualizado"]

    @staticmethod
    async def send_notifications(analistas: list[UsuarioEmissor]):
        async with db.get_session(db.engine) as session:
            notification_service = NotificationService(
                notification_repository=NotificationRepository(db=session)
            )
            messages: list[NotificationSchema] = []
            for dados in analistas:
                if not dados["user_id"]:
                    continue
                texto = ""
                emissor = dados["emissor_nome"]
                att = dados["atualizacao"]
                match att:
                    case "alocado":
                        texto = f"Você foi alocado para o emissor {emissor}."
                    case "atualizado":
                        texto = f"As informações do emissor {emissor} foram alteradas no banco de dados."
                    case "desalocado":
                        texto = f"Você não está mais alocado para o emissor {emissor}"
                messages.append(
                    NotificationSchema(
                        user_id=dados["user_id"],
                        link="/emissores/" + str(dados["emissor_id"]),
                        text=texto,
                    )
                )
            await notification_service.send(messages)
            await session.commit()

    @staticmethod
    async def notificar_alteracoes(
        emissores_antigos: list[UpdateEmissorSchema],
        emissores_atualizados: list[UpdateEmissorSchema],
        emissores_criados: list[UpdateEmissorSchema],
    ):
        async with db.get_session(db.engine) as session:
            ativos_repository = AtivosRepository(db=session)

            notificados: dict[int, AtivosService.UsuarioEmissor] = {}

            for inserted in emissores_criados:
                if not inserted.analista_credito_id:
                    continue
                notificados[inserted.analista_credito_id] = {
                    "analista_id": inserted.analista_credito_id,
                    "emissor_id": inserted.id,
                    "emissor_nome": inserted.nome,
                    "user_id": None,
                    "atualizacao": "alocado",
                }
            for pos, antigo in enumerate(emissores_antigos):
                atualizado = emissores_atualizados[pos]
                if antigo.analista_credito_id != atualizado.analista_credito_id:
                    if atualizado.analista_credito_id:
                        notificados[atualizado.analista_credito_id] = {
                            "analista_id": atualizado.analista_credito_id,
                            "emissor_id": atualizado.id,
                            "emissor_nome": atualizado.nome,
                            "user_id": None,
                            "atualizacao": "alocado",
                        }
                    if antigo.analista_credito_id:
                        notificados[antigo.analista_credito_id] = {
                            "analista_id": antigo.analista_credito_id,
                            "emissor_id": atualizado.id,
                            "emissor_nome": atualizado.nome,
                            "user_id": None,
                            "atualizacao": "desalocado",
                        }
                    continue
                elif antigo.analista_credito_id and (
                    antigo.cnpj != atualizado.cnpj
                    or antigo.nome != atualizado.nome
                    or antigo.grupo_id != atualizado.grupo_id
                    or antigo.setor_id != atualizado.setor_id
                    or antigo.tier != atualizado.tier
                    or antigo.codigo_cvm != atualizado.codigo_cvm
                ):
                    notificados[antigo.analista_credito_id] = {
                        "analista_id": antigo.analista_credito_id,
                        "emissor_id": antigo.id,
                        "emissor_nome": antigo.nome,
                        "user_id": None,
                        "atualizacao": "atualizado",
                    }
            analistas_preenchidos = await ativos_repository.analistas_from_ids(
                [id for id in notificados]
            )
            for preenchido in analistas_preenchidos:
                notificados[preenchido.id]["user_id"] = preenchido.user_id

            await AtivosService.send_notifications(
                [notificados[id] for id in notificados]
            )

    async def transacao_emissores(
        self, update: list[UpdateEmissorSchema], insert: list[InsertEmissorSchema]
    ):
        try:
            new_ids, old = await self.ativos_repository.transacao_emissores(
                update, insert
            )
            self.background_tasks.add_task(
                AtivosService.notificar_alteracoes,
                old,
                update,
                [
                    UpdateEmissorSchema(**ins.model_dump(), id=new_ids[i])
                    for i, ins in enumerate(insert)
                ],
            )
        except IntegrityError as err:
            # Entradas duplicadas
            failure = str(err._message()).split("=")
            failure = failure[1] if len(failure) >= 2 else "=".join(failure)
            raise HTTPException(HTTPStatus.CONFLICT, failure)

    async def emissor(self, id: int):
        return await self.ativos_repository.emissor(id)

    async def setores(self, with_sys_data: bool = False):
        return await self.ativos_repository.setores(with_sys_data)

    async def transacao_setores(
        self,
        atualizar_schema: list[SetorSchema],
        inserir_schema: list[InsertSetorSchema],
    ):
        try:
            await self.ativos_repository.transacao_setores(
                atualizar_schema, inserir_schema
            )
        except IntegrityError as err:
            # Entradas duplicadas
            failure = str(err._message()).split("=")
            failure = failure[1] if len(failure) >= 2 else "=".join(failure)
            raise HTTPException(HTTPStatus.CONFLICT, failure)

    async def grupos(self):
        return await self.ativos_repository.grupos()

    async def transacao_grupos(
        self,
        atualizar_schema: list[GrupoSchema],
        inserir_schema: list[InsertGrupoSchema],
    ):
        try:
            await self.ativos_repository.transacao_grupos(
                atualizar_schema, inserir_schema
            )
        except IntegrityError as err:
            # Entradas duplicadas
            failure = str(err._message()).split("=")
            failure = failure[1] if len(failure) >= 2 else "=".join(failure)
            raise HTTPException(HTTPStatus.CONFLICT, failure)

    async def analistas(self):
        return await self.ativos_repository.analistas()

    @staticmethod
    def is_ativo_offshore(isin: str) -> bool:
        return isin.startswith("US")

    @staticmethod
    def get_quantidade_tratada(
        quantidade: Decimal, side_operacao: SideOperacao
    ) -> Decimal:
        if side_operacao in {SideOperacao.COMPRADO}:
            return quantidade
        if side_operacao in {SideOperacao.VENDIDO}:
            return quantidade * -1

        return Decimal(0)

    @staticmethod
    def get_aviso_isin(
        isin: str | None,
        identificador_ativo: str,
        tipo_ativo: str,
    ) -> str | None:
        if isin is None or isin.startswith("*"):
            return f'{tipo_ativo} "{identificador_ativo}" sem ISIN ({isin})'
