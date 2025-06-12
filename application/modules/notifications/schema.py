from pydantic import BaseModel as Schema


class NotificationSchema(Schema):
    user_id: int
    text: str
    link: str | None = None
