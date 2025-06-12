from dataclasses import dataclass

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio.session import AsyncSession

from .model import Notification
from .schema import NotificationSchema


@dataclass
class NotificationRepository:
    db: AsyncSession

    async def all(self, user_id: int):
        results = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        return results.scalars().all()

    async def store(self, notifications: list[NotificationSchema]):
        await self.db.execute(
            insert(Notification).values(
                [notification.model_dump() for notification in notifications]
            )
        )
