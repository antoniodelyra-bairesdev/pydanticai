import logging
import json

from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import getenv
from typing import Any, Coroutine

from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.message import Message
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import (
    SendMailPostRequestBody,
)
from msgraph.graph_service_client import GraphServiceClient
from sqlalchemy.ext.asyncio.session import AsyncSession

from config.email import sender_mail


class EmailRepository(ABC):
    db: AsyncSession

    @abstractmethod
    def enviar_email(
        self,
        para: list[str],
        assunto: str,
        conteudo: str,
        copia: list[str] = [],
        copia_oculta: list[str] = [],
    ) -> Coroutine[Any, Any, None]: ...


class MockEmailRepository(EmailRepository):
    async def enviar_email(
        self,
        para: list[str],
        assunto: str,
        conteudo: str,
        copia: list[str] = [],
        copia_oculta: list[str] = [],
    ):
        logging.info(
            json.dumps(
                {
                    "para": para,
                    "assunto": assunto,
                    "conteudo": conteudo,
                    "copia": copia,
                    "copia_oculta": copia_oculta,
                },
                indent="\t",
            )
        )


@dataclass
class GraphEmailRepository(EmailRepository):
    db: AsyncSession
    client: GraphServiceClient

    async def enviar_email(
        self,
        para: list[str],
        assunto: str,
        conteudo: str,
        copia: list[str] = [],
        copia_oculta: list[str] = [],
    ):
        await self.client.users.by_user_id(sender_mail).send_mail.post(
            SendMailPostRequestBody(
                message=Message(
                    subject=assunto,
                    body=ItemBody(
                        content_type=BodyType.Html,
                        content=conteudo,
                    ),
                    to_recipients=[
                        Recipient(email_address=EmailAddress(address=recipiente))
                        for recipiente in para
                    ],
                    cc_recipients=[
                        Recipient(email_address=EmailAddress(address=recipiente))
                        for recipiente in copia
                    ],
                    bcc_recipients=[
                        Recipient(email_address=EmailAddress(address=recipiente))
                        for recipiente in copia_oculta
                    ],
                )
            )
        )
