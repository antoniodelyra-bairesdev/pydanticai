from config.environment import is_prod
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from .repository import EmailRepository, GraphEmailRepository, MockEmailRepository


class EmailServiceFactory:
    @staticmethod
    def criarService(db: AsyncSession):
        if is_prod():
            from config.email import client

            return EmailService(
                email_repository=GraphEmailRepository(db=db, client=client)
            )
        else:
            return EmailService(email_repository=MockEmailRepository())


@dataclass
class EmailService:
    email_repository: EmailRepository

    async def enviar(
        self,
        para: list[str],
        assunto: str,
        conteudo: str,
        copia: list[str] = [],
        copia_oculta: list[str] = [],
    ):
        await self.email_repository.enviar_email(
            para, assunto, conteudo, copia, copia_oculta
        )
