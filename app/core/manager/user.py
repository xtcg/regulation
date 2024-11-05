from typing import Annotated

from fastapi import Depends

from app.core import database
from app.core.database import UserDao
from app.core.exception import BadRequest
# from app.vo import UserPaginationQuery


class UserManager:
    def __init__(self, user_dao: UserDao):
        self.user_dao = user_dao

    async def update_user(self, user_id: int, update_dict: dict):
        user = await self.user_dao.get(user_id)
        if not user:
            raise BadRequest("user not found")
        return await self.user_dao.update(user, update_dict)

    # async def list_user(self, pg: UserPaginationQuery):
    #     return await self.user_dao.pagination(**pg.model_dump())


async def get_user_manager(user_dao: Annotated[UserDao, Depends(database.get_user_dao)]) -> UserManager:
    return UserManager(user_dao)
