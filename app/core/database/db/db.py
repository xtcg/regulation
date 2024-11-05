from mysqlwaves import SessionMaker, BaseModel
from sqlalchemy import create_engine

from app.config import settings

_db = SessionMaker(**settings.mysql.model_dump())


async def get_session():
    async with _db.get_session() as sess:
        yield sess


def create_all():
    url = settings.mysql.db_url.replace("asyncmy", "pymysql")
    engine = create_engine(url, echo=True)
    BaseModel.metadata.create_all(engine)
