from datetime import datetime
from config.database import Model, SchemaSistema
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TIMESTAMP, BigInteger, SmallInteger, Text


class Notification(Model, SchemaSistema):
    __tablename__ = "notificacoes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
