from mysqlwaves import BaseModel
from sqlalchemy import BigInteger, Boolean, Text, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.model.base import TimeMixin


class Session(TimeMixin, BaseModel):
    __tablename__ = "t_session"

    session_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    position_id: Mapped[int] = mapped_column(BigInteger, default=0)
    session_type: Mapped[int] = mapped_column(Integer, default=0)
    character_id: Mapped[int] = mapped_column(BigInteger, default=0)
    scene_id: Mapped[int] = mapped_column(BigInteger, default=0)
    character_name: Mapped[str] = mapped_column(String(255), default="")
    first_message: Mapped[str] = mapped_column(Text, default="")
    last_message: Mapped[str] = mapped_column(Text, default="")
    score: Mapped[int] = mapped_column(BigInteger, default=0)
    task_id: Mapped[int] = mapped_column(BigInteger, default=0)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
