from mysqlwaves import BaseModel
from sqlalchemy import BigInteger, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.model.base import TimeMixin


class Knowledge(BaseModel):
    __tablename__ = "t_knowledge"

    knowledge_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    folder: Mapped[str] = mapped_column(String(1024))
    
