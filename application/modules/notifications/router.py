from fastapi import Depends, Request
from fastapi.routing import APIRouter
from config.swagger import token_field
from sqlalchemy.ext.asyncio.session import AsyncSession

from modules.util.request import db, get_user
from modules.auth.model import Usuario

from .service import NotificationService
from .repository import NotificationRepository

router = APIRouter(
    prefix="/notificacoes", tags=["Notificações"], dependencies=[token_field]
)


def get_service(request: Request):
    session = db(request)
    return NotificationService(
        notification_repository=NotificationRepository(db=session)
    )


@router.get("/")
async def notificacoes(
    service: NotificationService = Depends(get_service),
    user: Usuario = Depends(get_user),
):
    return await service.all(user.id)
