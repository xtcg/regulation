from typing import Annotated, Any

from fastapi import Depends
from mysqlwaves import SqlDatabase
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.db import get_session
from app.core.model import User
from app.core.schema import ThirdUserInfo


class UserDao(SqlDatabase[User]):

    def filter_query(self, query, **kwargs) -> Select[Any]:
        return query

    async def get_by_third_user_id(self, user_id: str):
        result = await self.session.execute(select(User).where(User.third_user_id == user_id))
        user = result.scalars().first()
        return user

    async def upset(self, user_info: ThirdUserInfo) -> User:
        old_user = await self.get_by_third_user_id(user_info.third_user_id)
        if old_user:
            return await self.update(old_user, user_info.model_dump())
        else:
            return await self.create(user_info.model_dump())

    async def get_users_by_ids(self, user_ids: list[int]) -> list[User]:
        result = await self.session.execute(select(User).where(User.user_id.in_(user_ids)))
        users = result.scalars().all()
        return users


async def get_user_dao(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    yield UserDao(User, session)
