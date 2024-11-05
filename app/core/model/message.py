from mysqlwaves import BaseModel
from sqlalchemy import String, Text, BigInteger, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.core.model.base import TimeMixin


class Message(TimeMixin, BaseModel):
    __tablename__ = "t_message"

    message_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    session_id: Mapped[int] = mapped_column(BigInteger)
    role: Mapped[str] = mapped_column(String(64))
    content: Mapped[str] = mapped_column(Text)
    feedback_type: Mapped[int] = mapped_column(SmallInteger, default=0)
    feedback_content: Mapped[str] = mapped_column(Text, default="")
