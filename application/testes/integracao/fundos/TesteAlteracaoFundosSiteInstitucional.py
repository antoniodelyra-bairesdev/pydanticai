from dataclasses import dataclass
from http import HTTPStatus
from random import randint
from typing import TypedDict

from testes.integracao.BaseTesteIntegracao import BaseTesteIntegracao
from testes.mock.fundos import (
    fake_fundo_custodiante,
    fake_fundo,
    fake_fundo_site_institucional,
)

from modules.fundos.model import Fundo, FundoSiteInstitucional
from modules.fundos.schema import (
    FundosSiteInstitucionalTransacaoSchema,
    UpdateFundoInstitucionalSchema,
    InsertFundoInstitucionalSchema,
)

QTD_CUSTODIANTES = 3
QTD_FUNDOS = 10
QTD_FUNDOS_INSTITUCIONAIS = 5


class TesteAlteracaoFundosSiteInstitucional(BaseTesteIntegracao):
    fundos_nao_institucionais_esperados: dict[int, Fundo] = {}
    fundos_institucionais_esperados: dict[int, FundoSiteInstitucional] = {}

    async def asyncSetUp(self):
        await super().asyncSetUp()
        # Busca as estratégias fixas existentes
        estrategias: list[dict] = (
            await self.get("v1/fundos/institucionais/classificacoes")
        ).json()
        # Busca os tipos fixos existentes
        tipos: list[dict] = (await self.get("v1/fundos/institucionais/tipos")).json()

        # Cria QTD_CUSTODIANTES custodiantes para os fundos utilizarem
        custodiantes = [
            await fake_fundo_custodiante(db=self.db) for _ in range(QTD_CUSTODIANTES)
        ]

        # Limpa os dados esperados
        self.fundos_nao_institucionais_esperados = {}
        self.fundos_institucionais_esperados = {}

        # De QTD_FUNDOS registrados, QTD_FUNDOS_INSTITUCIONAIS serão disponibilizados no site institucional
        for i in range(QTD_FUNDOS):
            custodiante_aleatorio = custodiantes[randint(0, len(custodiantes) - 1)]
            fundo = await fake_fundo(custodiante_aleatorio.id, db=self.db)
            if i < QTD_FUNDOS_INSTITUCIONAIS:
                estrategia_aleatoria = estrategias[randint(0, len(estrategias) - 1)]
                tipo_aleatorio = tipos[randint(0, len(tipos) - 1)]
                fundo_institucional = await fake_fundo_site_institucional(
                    fundo.id,
                    estrategia_aleatoria["id"],
                    tipo_aleatorio["id"],
                    db=self.db,
                )
                self.fundos_institucionais_esperados[fundo_institucional.id] = (
                    fundo_institucional
                )
            else:
                self.fundos_nao_institucionais_esperados[fundo.id] = fundo

    async def test_listar_classificacoes_especificas_fundos_site_institucional(self):
        """Deve buscar exatamente as estratégias fixas no banco de dados que os fundos do site institucional utilizam."""

        response = await self.get("/v1/fundos/institucionais/classificacoes")

        self.assertEqual(response.status_code, HTTPStatus.OK)

        estrategias: list[dict] = response.json()
        estrategias.sort(key=lambda x: x["nome"])

        esperados = [
            "Renda Fixa",
            "Credito Privado",
            "Ações",
            "Multimercado",
            "Imobiliário",
            "Ajustado ao Risco",
            "Data Alvo",
        ]
        esperados.sort()

        self.assertEqual(
            "\n".join([estrategia["nome"] for estrategia in estrategias]),
            "\n".join(esperados),
        )

    async def test_listar_tipos_especificos_fundos_site_institucional(self):
        """Deve buscar exatamente os tipos fixos no banco de dados que os fundos do site institucional utilizam."""

        response = await self.get("/v1/fundos/institucionais/tipos")

        self.assertEqual(response.status_code, HTTPStatus.OK)

        tipos: list[dict] = response.json()
        tipos.sort(key=lambda x: x["nome"])

        esperados = [
            "Fundo de Investimento",
            "Fundo de Previdência (FIE)",
            "Fundo de Previdência (FIFE)",
        ]
        esperados.sort()

        self.assertEqual(
            "\n".join([tipo["nome"] for tipo in tipos]),
            "\n".join(esperados),
        )

    async def test_listar_fundos_site_institucional(self):
        """Deve buscar todos os fundos listados no site institucional corretamente."""

        # Busca os sites institucionais
        response = await self.get("/v1/fundos/institucionais")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        fundos_institucionais_devolvidos: list[dict] = response.json()

        self.assertEqual(
            len(fundos_institucionais_devolvidos),
            len(self.fundos_institucionais_esperados),
        )

        for fundo_institucional_devolvido in fundos_institucionais_devolvidos:
            id: int = fundo_institucional_devolvido["id"]
            fundo_id: int = fundo_institucional_devolvido["fundo_id"]

            with self.subTest(id=id, fundo_id=fundo_id):
                fundo_institucional_esperado = self.fundos_institucionais_esperados[id]

                self.assertNotIn(fundo_id, self.fundos_nao_institucionais_esperados)
                self.assertEqual(
                    fundo_institucional_devolvido["id"], fundo_institucional_esperado.id
                )
                self.assertEqual(
                    fundo_institucional_devolvido["fundo_id"],
                    fundo_institucional_esperado.fundo_id,
                )
                self.assertEqual(
                    fundo_institucional_devolvido["classificacao"]["id"],
                    fundo_institucional_esperado.site_institucional_classificacao_id,
                )
                self.assertEqual(
                    fundo_institucional_devolvido["tipo"]["id"],
                    fundo_institucional_esperado.site_institucional_tipo_id,
                )

    async def test_detalhes_fundo_institucional_existente(self):
        """Deve mostrar detalhes dos fundos listados no site institucional corretamente."""

        response = await self.get("/v1/fundos/institucionais")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        fundos_institucionais_devolvidos: list[dict] = response.json()

        for fundo_institucional_devolvido in fundos_institucionais_devolvidos:
            id: int = fundo_institucional_devolvido["id"]
            fundo_id: int = fundo_institucional_devolvido["fundo_id"]

            with self.subTest(id=id, fundo_id=fundo_id):
                nome = fundo_institucional_devolvido["nome"]
                estrategia_id = fundo_institucional_devolvido["classificacao"]["id"]
                tipo_id = fundo_institucional_devolvido["tipo"]["id"]

                detalhes = await self.get(f"/v1/fundos/institucionais/{fundo_id}")
                self.assertEquals(detalhes.status_code, HTTPStatus.OK)

                informacoes = detalhes.json()

                self.assertEqual(informacoes["id"], id)
                self.assertEqual(informacoes["fundo"]["id"], fundo_id)
                self.assertEqual(informacoes["fundo"]["nome"], nome)
                self.assertEqual(informacoes["classificacao"]["id"], estrategia_id)
                self.assertEqual(informacoes["tipo"]["id"], tipo_id)

    async def test_detalhes_fundo_institucional_nao_encontrado(self):
        """Deve informar que o recurso não existe caso detalhes de um fundo não listado no site institucional seja requisitado."""

        for fundo_id in self.fundos_nao_institucionais_esperados:
            with self.subTest(fundo_id=fundo_id):
                detalhes = await self.get(f"/v1/fundos/institucionais/{fundo_id}")
                self.assertEquals(detalhes.status_code, HTTPStatus.NOT_FOUND)

    async def test_recusar_pedido_usuario_nao_autorizado(self):
        """Deve recusar o pedido de um usuário que não possuir autorização necessária para alterar informações dos fundos institucionais."""

        msg_erro = "Você não possui autorização para alterar os fundos disponibilizados no site institucional."

        response = await self.put(
            "/v1/fundos/institucionais",
            body={"deletados": [], "alterados": [], "inseridos": []},
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        info = response.json()
        self.assertEqual(info["detail"], msg_erro)

    async def test_nao_permitir_fundos_duplicados_site_institucional(self):
        """Deve rejeitar uma alteração em massa em que o estado final após a alteração possui o mesmo fundo mapeado duas vezes no site institucional ."""

        self.assertTrue(QTD_FUNDOS >= 1)
        self.assertTrue(QTD_FUNDOS_INSTITUCIONAIS < QTD_FUNDOS)

        nome_funcao = "Site Institucional - Alterar fundos"

        # Adiciona permissão para o usuário poder alterar a listagem de fundos do site institucional
        funcoes = await self.funcoes_usuario()
        [funcao_alterar_fundos_site_institucional] = [
            funcao for funcao in funcoes.values() if funcao.nome == nome_funcao
        ]
        await self.adicionar_funcao_usuario(funcao_alterar_fundos_site_institucional)

        existente = [*self.fundos_institucionais_esperados.values()][0]
        body = FundosSiteInstitucionalTransacaoSchema(
            deletados=[],
            alterados=[],
            inseridos=[
                InsertFundoInstitucionalSchema(
                    fundo_id=existente.fundo_id,
                    apelido="",
                    classificacao_id=1,
                    tipo_id=1,
                )
            ],
        )
        transacao = await self.put("/v1/fundos/institucionais", body=body.model_dump())
        # Alteração em massa não pode estar OK
        self.assertNotEqual(transacao.status_code, HTTPStatus.OK)

    @dataclass
    class ArrangeTestPersistirAlteracoesEmMassaReturnType:
        body: FundosSiteInstitucionalTransacaoSchema
        removidos_ids: list[int]
        removidos_ids_fundos: list[int]
        alterado_id: int
        alterado_nova_categoria_id: int
        alterado_novo_apelido: str
        adicionado_id: int
        adicionado_novo_apelido: str

    async def arrange_test_persistir_alteracoes_em_massa(self):
        """Configuração do teste de alteração em massa dos fundos do site institucional."""

        nome_funcao = "Site Institucional - Alterar fundos"

        # Adiciona permissão para o usuário poder alterar a listagem de fundos do site institucional
        funcoes = await self.funcoes_usuario()
        [funcao_alterar_fundos_site_institucional] = [
            funcao for funcao in funcoes.values() if funcao.nome == nome_funcao
        ]
        await self.adicionar_funcao_usuario(funcao_alterar_fundos_site_institucional)

        fsi_esperados = [*self.fundos_institucionais_esperados.values()]

        # A transação fará o seguinte:
        # - Removerá todos os fundos do site institucional da lista, exceto o último
        remover = fsi_esperados[:-1]
        # - Irá alterar a categoria e o apelido do último fundo
        [id_alterar] = fsi_esperados[-1:]
        alterar = self.fundos_institucionais_esperados[id_alterar.id]
        apelido_alterado = "Apelido alterado"
        categoria_alterada = (
            2 if alterar.site_institucional_classificacao_id == 1 else 1
        )
        # - Adicionará o último fundo que não aparece na lista do site institucional à lista e irá alterar seu apelido
        adicionar = [*self.fundos_nao_institucionais_esperados.values()][-1]
        apelido_adicionado = "Novo fundo"

        body = FundosSiteInstitucionalTransacaoSchema(
            deletados=[rem.id for rem in remover],
            alterados=[
                UpdateFundoInstitucionalSchema(
                    id=alterar.id,
                    fundo_id=alterar.fundo_id,
                    classificacao_id=categoria_alterada,
                    tipo_id=alterar.site_institucional_tipo_id,
                    apelido=apelido_alterado,
                )
            ],
            inseridos=[
                InsertFundoInstitucionalSchema(
                    fundo_id=adicionar.id,
                    classificacao_id=1,
                    tipo_id=1,
                    apelido=apelido_adicionado,
                )
            ],
        )

        return self.ArrangeTestPersistirAlteracoesEmMassaReturnType(
            body=body,
            removidos_ids=[removido.id for removido in remover],
            removidos_ids_fundos=[removido.fundo_id for removido in remover],
            alterado_id=alterar.id,
            alterado_nova_categoria_id=categoria_alterada,
            alterado_novo_apelido=apelido_alterado,
            adicionado_id=adicionar.id,
            adicionado_novo_apelido=apelido_adicionado,
        )

    async def assert_test_persistir_alteracoes_em_massa_remocao(
        self,
        configuracao: ArrangeTestPersistirAlteracoesEmMassaReturnType,
        fundos_site_institucional: list[dict],
        fundos_fora_do_site_institucionais: list[dict],
    ):
        # Garante que nenhum fundo removido estará nos resultados
        ids_fundos_institucionais = [inst["id"] for inst in fundos_site_institucional]
        for id_removido in configuracao.removidos_ids:
            self.assertNotIn(id_removido, ids_fundos_institucionais)
        # Garante que os fundos removidos continuam existindo internamente
        ids_fundos_internos = [
            fundo["id"] for fundo in fundos_fora_do_site_institucionais
        ]
        for id_fundo_removido in configuracao.removidos_ids_fundos:
            self.assertIn(id_fundo_removido, ids_fundos_internos)

    async def assert_test_persistir_alteracoes_em_massa_alteracao(
        self,
        configuracao: ArrangeTestPersistirAlteracoesEmMassaReturnType,
        fundos_site_institucional: list[dict],
    ):
        # Garante que o fundo alterado estará nos resultados
        [resultado_alterado] = [
            inst
            for inst in fundos_site_institucional
            if inst["id"] == configuracao.alterado_id
        ]
        # Garante que o fundo alterado teve a categoria modificada
        self.assertEqual(
            resultado_alterado["classificacao"]["id"],
            configuracao.alterado_nova_categoria_id,
        )
        # Garante que fundo alterado teve o apelido modificado
        self.assertEqual(
            resultado_alterado["apelido"], configuracao.alterado_novo_apelido
        )

    async def assert_test_persistir_alteracoes_em_massa_insercao(
        self,
        configuracao: ArrangeTestPersistirAlteracoesEmMassaReturnType,
        fundos_site_institucional: list[dict],
    ):
        # Garante que o fundo adicionado estará nos resultados
        [resultado_adicionado] = [
            inst
            for inst in fundos_site_institucional
            if inst["fundo_id"] == configuracao.adicionado_id
        ]
        # Garante que o fundo adicionado teve o apelido modificado
        self.assertEqual(
            resultado_adicionado["apelido"], configuracao.adicionado_novo_apelido
        )

    async def test_persistir_alteracoes_em_massa(self):
        """Deve persistir as informações de fundos do site institucional no banco de dados após uma alteração em massa ser feita por um usuário com acesso."""

        self.assertTrue(QTD_FUNDOS >= 3)
        self.assertTrue(QTD_FUNDOS_INSTITUCIONAIS < QTD_FUNDOS)

        configuracao = await self.arrange_test_persistir_alteracoes_em_massa()

        transacao = await self.put(
            "/v1/fundos/institucionais", body=configuracao.body.model_dump()
        )
        # Alteração em massa feita com sucesso
        self.assertEqual(transacao.status_code, HTTPStatus.OK)

        # Busca informações dos fundos internos
        fundos_internos_response = await self.get("/v1/fundos/")
        self.assertEqual(fundos_internos_response.status_code, HTTPStatus.OK)
        fundos_internos: list[dict] = fundos_internos_response.json()

        # Busca informações dos fundos listados no site institucional, atualizados
        institucionais_response = await self.get("/v1/fundos/institucionais")
        self.assertEqual(institucionais_response.status_code, HTTPStatus.OK)
        institucionais: list[dict] = institucionais_response.json()
        # Verifica se o tamanho do resultado coincide com a operação em massa
        self.assertEqual(
            len(institucionais), 2
        )  # Todos removidos exceto um + novo site institucional

        await self.assert_test_persistir_alteracoes_em_massa_remocao(
            configuracao, institucionais, fundos_internos
        )
        await self.assert_test_persistir_alteracoes_em_massa_alteracao(
            configuracao, institucionais
        )
        await self.assert_test_persistir_alteracoes_em_massa_insercao(
            configuracao, institucionais
        )
