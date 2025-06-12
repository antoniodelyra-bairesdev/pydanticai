import asyncio
from dataclasses import dataclass
from modules.websockets.schema import WSNotification, WSMessageType, WSMessage
from modules.websockets.service import WebSocketService

from .repository import NotificationRepository
from .schema import NotificationSchema


@dataclass
class NotificationService:
    notification_repository: NotificationRepository

    async def all(self, user_id: int):
        return await self.notification_repository.all(user_id)

    async def send(self, notifications: list[NotificationSchema]):
        await self.notification_repository.store(notifications)
        notify = [
            WebSocketService.send_message_to_user(
                notification.user_id,
                WSMessage(
                    type=WSMessageType.NOTIFICATION,
                    content=WSNotification(
                        text=notification.text, link=notification.link
                    ),
                ),
            )
            for notification in notifications
        ]
        if len(notify) > 0:
            await asyncio.gather(*notify)
