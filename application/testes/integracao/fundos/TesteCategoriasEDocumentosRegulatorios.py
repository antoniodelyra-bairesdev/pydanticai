from http import HTTPStatus

from testes.integracao.BaseTesteIntegracao import BaseTesteIntegracao

AUTORIZACAO_ALTERACAO_DOCUMENTOS_REGULATORIOS = (
    "Site Institucional - Alterar documentos regulatórios"
)
MENSAGEM_NAO_AUTORIZADO_DOCUMENTOS_REGULATORIOS = "Você não possui autorização para alterar os documentos regulatórios do site institucional."


class TesteCategoriasEDocumentosRegulatorios(BaseTesteIntegracao):
    async def test_rejeitar_remocao_de_documento_usuario_nao_autorizado(self):
        """Deve rejeitar a remoção de um documento regulatório do site institucional caso o usuário não tenha a permissão necessária."""

        response = await self.delete("/v1/regulatorio/relatorio/0")

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(
            response.json()["detail"], MENSAGEM_NAO_AUTORIZADO_DOCUMENTOS_REGULATORIOS
        )

    async def test_rejeitar_criacao_categoria_usuario_nao_autorizado(self):
        """Deve rejeitar a criação de uma categoria do site institucional caso o usuário não tenha a permissão necessária."""

        response = await self.post("/v1/regulatorio/categoria", {"nome": "..."})

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(
            response.json()["detail"], MENSAGEM_NAO_AUTORIZADO_DOCUMENTOS_REGULATORIOS
        )

    async def test_rejeitar_reordenar_categoria_usuario_nao_autorizado(self):
        """Deve rejeitar a reordenação das categorias de documentos do site institucional caso o usuário não tenha a permissão necessária."""

        response = await self.put("/v1/regulatorio/categoria", [])

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(
            response.json()["detail"], MENSAGEM_NAO_AUTORIZADO_DOCUMENTOS_REGULATORIOS
        )

    async def test_rejeitar_alteracao_plano_de_fundo_categoria_usuario_nao_autorizado(
        self,
    ):
        """Deve rejeitar a alteração de plano de fundo de uma categoria de documentos do site institucional caso o usuário não tenha a permissão necessária."""

        response = await self.put(
            "/v1/regulatorio/categoria/plano-de-fundo?categoria_id=0&plano_de_fundo_id=0"
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(
            response.json()["detail"], MENSAGEM_NAO_AUTORIZADO_DOCUMENTOS_REGULATORIOS
        )

    async def test_rejeitar_remocao_de_categoria_usuario_nao_autorizado(self):
        """Deve rejeitar a remoção de uma categoria de documentos regulatórios do site institucional caso o usuário não tenha a permissão necessária."""

        response = await self.delete("/v1/regulatorio/categoria/0")

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(
            response.json()["detail"], MENSAGEM_NAO_AUTORIZADO_DOCUMENTOS_REGULATORIOS
        )

    async def test_rejeitar_criacao_de_documento_usuario_nao_autorizado(self):
        """Deve rejeitar a criação de um documento regulatório no site institucional caso o usuário não tenha a permissão necessária."""

        response = await self.post(
            "/v1/regulatorio/categoria/0/relatorio",
            data={"metadados": "[]"},
            files={},
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(
            response.json()["detail"], MENSAGEM_NAO_AUTORIZADO_DOCUMENTOS_REGULATORIOS
        )
