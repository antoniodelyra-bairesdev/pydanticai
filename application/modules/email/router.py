from fastapi import APIRouter, Request, Depends
from config.swagger import token_field

from .schema import DadosEmailSchema
from .service import EmailService, EmailServiceFactory

router = APIRouter(prefix="/email", tags=["E-mail"], dependencies=[token_field])


def get_service(request: Request):
    session = request.state.db
    return EmailServiceFactory.criarService(session)


@router.post("/")
async def enviar_email(
    dados: DadosEmailSchema, service: EmailService = Depends(get_service)
):
    await service.enviar(
        dados.para, dados.assunto, dados.conteudo, dados.copia, dados.copia_oculta
    )
