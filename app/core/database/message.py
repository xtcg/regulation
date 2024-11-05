from typing import Annotated

from fastapi import Depends
from mysqlwaves import SqlDatabase
from sqlalchemy import select, func, literal
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.db import get_session
from app.core.model import Message, Session


class MessageDao(SqlDatabase[Message]):
    async def pagination(
        self,
        *,
        offset: int = 0,
        page_size: int = 20,
        sort: list = None,
        count=True,
        user_id: int = None,
        session_id: int = None,
        position_id: int = None,
    ) -> tuple[int, list[dict]]:

        if position_id is not None:
            query = (
                select(
                    Message.message_id,
                    Message.session_id,
                    Message.role,
                    Message.content,
                    Message.create_time,
                    Session.character_id,
                )
                .select_from(Message)
                .join(Session, Message.session_id == Session.session_id)
            )
            query = query.where(Session.position_id == position_id)
        else:
            query = select(
                Message.message_id,
                Message.session_id,
                Message.role,
                Message.content,
                Message.create_time,
                literal(0).label("character_id"),
            ).select_from(Message)

        if user_id is not None:
            query = query.where(Message.user_id == user_id)
        if session_id is not None:
            query = query.where(Message.session_id == session_id)

        if count:
            total_stmt = select(func.count()).select_from(query.subquery())
            total = await self.session.scalar(total_stmt)
        else:
            total = None

        if sort:
            query = query.order_by(*sort)

        query = query.offset(offset).limit(page_size)

        result = await self.session.execute(query)
        rows = result.fetchall()

        # 将每一行转换为字典
        items = [dict(row._mapping) for row in rows]

        return total, items

    async def update_feedback(
        self, user_id: int, message_id: int, feedback_type: int, feedback_content: str
    ) -> Message:
        message = await self.get(message_id)
        if not message:
            return None
        if message.user_id != user_id:
            return None
        message.feedback_type = feedback_type
        message.feedback_content = feedback_content
        await self.session.commit()
        return message


async def get_message_dao(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    yield MessageDao(Message, session)
