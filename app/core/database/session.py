from typing import Annotated, Tuple

from fastapi import Depends
from mysqlwaves import SqlDatabase
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.db import get_session
from app.core.enums import SessionType, TaskScoreType
from app.core.model import Session


class SessionDao(SqlDatabase[Session]):

    def filter_query(
        self, query, user_id: int = None, position_id: int = None, session_type: int = None, **kwargs
    ) -> Select:
        if user_id:
            query = query.where(Session.user_id == user_id)
        if position_id:
            query = query.where(Session.position_id == position_id)
        if session_type:
            query = query.where(Session.session_type == session_type)
        return query

    async def get_chat_session(self, user_id: int, position_id: int) -> Session:
        result = await self.session.execute(
            select(Session).where(
                Session.deleted.is_(False),
                Session.user_id == user_id,
                Session.position_id == position_id,
                Session.session_type == SessionType.CHAT.value,
            )
        )
        return result.scalars().one_or_none()

    async def update_first_message(self, session_id: int, content: str) -> Session:
        session = await self.get(session_id)
        session.first_message = content
        await self.session.commit()
        return session

    async def update_last_message(self, session_id: int, content: str) -> Session:
        session = await self.get(session_id)
        session.last_message = content
        await self.session.commit()
        return session

    async def update_score(self, session_id: int, score: int) -> Session:
        session = await self.get(session_id)
        session.score = score
        await self.session.commit()
        return session

    async def group_score_by_user(
        self,
        task_id: int,
        score_type: TaskScoreType,
        offset: int = 0,
        page_size: int = 20,
    ) -> Tuple[int, dict[int, int]]:
        count_pipeline = [
            {"$group": {"_id": "$user_id"}},
            {"$count": "total_count"},
        ]
        total_count_result = list(self.model.aggregate(count_pipeline))
        total_count = total_count_result[0]["total_count"] if total_count_result else 0

        score_agg = {"$max": "$score"} if score_type == TaskScoreType.MAX else {"$first": "$score"}
        pipeline = [
            {"$match": {"task_id": task_id}},
            {"$sort": {"create_time": -1}},
            {"$group": {"_id": "$user_id", "score": score_agg}},
            {"$sort": {"_id": 1}},
            {"$skip": offset},
            {"$limit": page_size},
        ]
        result = list(self.model.aggregate(pipeline))
        return total_count, {item["_id"]: item["score"] for item in result}


async def get_session_dao(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    yield SessionDao(Session, session)
