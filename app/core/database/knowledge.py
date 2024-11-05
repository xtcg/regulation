from typing import Annotated, List

from fastapi import Depends
from mysqlwaves import SqlDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.db import get_session
from app.core.model import Knowledge


class KnowledgeDao(SqlDatabase[Knowledge]):

    async def list(self) -> List[Knowledge]:
        result = await self.session.execute(select(Knowledge))
        return result.scalars().all()


async def get_knowledge_dao(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    yield KnowledgeDao(Knowledge, session)
