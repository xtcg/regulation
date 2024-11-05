from mysqlwaves import BaseModel
from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.core.model.base import TimeMixin


class User(TimeMixin, BaseModel):
    __tablename__ = "t_user"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    third_user_id: Mapped[str] = mapped_column(String(128))
    username: Mapped[str] = mapped_column(String(255))
    mobile: Mapped[str] = mapped_column(String(32))
    position_id: Mapped[int] = mapped_column(BigInteger, default=0)
    position_name: Mapped[str] = mapped_column(String(255), default="")
    # role_ids: Mapped[list] = mapped_column(JSON, default_factory=dict)
