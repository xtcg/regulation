from typing import Annotated, Tuple

from fastapi import Depends
from sqlalchemy import desc

from app.core.database import SessionDao, MessageDao, get_session_dao, get_message_dao, UserDao, get_user_dao
from app.core.enums import Role, SessionType, FeedbackType, TaskScoreType
from app.core.exception import SessionNoFound, MessageNoFound
from app.core.model import Session, Message


class HistoryManager:

    def __init__(self, session_dao: SessionDao, message_dao: MessageDao, user_dao: UserDao):
        self.session_dao = session_dao
        self.message_dao = message_dao
        self.user_dao = user_dao

    async def create_chat_session(self, user_id: int) -> Session:
        return await self.session_dao.create(
            Session(
                user_id=user_id,
                session_type=SessionType.CHAT.value,
            ).model_dump()
        )

    async def create_exercise_session(
        self,
        user_id: int,
        position_id: int,
        character_id: int = 0,
        scene_id: int = 0,
        character_name: str = "",
        first_message: str = "",
    ) -> Session:
        return await self.session_dao.create(
            Session(
                user_id=user_id,
                position_id=position_id,
                session_type=SessionType.EXERCISE.value,
                character_id=character_id,
                scene_id=scene_id,
                character_name=character_name,
                first_message=first_message,
            ).model_dump()
        )

    async def create_task_session(
        self,
        user_id: int,
        task_id: int,
        session_type: SessionType,
        character_name: str,
        first_message: str,
    ) -> Session:
        return await self.session_dao.create(
            Session(
                user_id=user_id,
                task_id=task_id,
                session_type=session_type.value,
                character_name=character_name,
                first_message=first_message,
            ).model_dump()
        )

    async def create_message(self, session_id: int, user_id: int, role: Role, content: str) -> None:
        await self.message_dao.create(
            Message(
                session_id=session_id,
                user_id=user_id,
                role=role.value,
                content=content,
            ).model_dump()
        )

    async def update_first_message_in_session(self, session_id: int, content: str) -> None:
        await self.session_dao.update_first_message(session_id, content)

    async def update_last_message_in_session(self, session_id: int, content: str) -> None:
        await self.session_dao.update_last_message(session_id, content)

    async def update_score_in_session(self, session_id: int, score: int) -> None:
        await self.session_dao.update_score(session_id, score)

    async def list_session(
        self,
        user_id: int,
        position_id: int,
        session_type: int,
        offset: int = 0,
        page_size: int = 20,
    ) -> Tuple[int, list[dict]]:
        total, data = await self.session_dao.pagination(
            user_id=user_id,
            position_id=position_id,
            session_type=session_type,
            offset=offset,
            page_size=page_size,
            sort=[desc(Session.create_time)],
        )
        res = [item.model_dump() for item in data]
        return total, res

    async def list_message(
        self,
        user_id: int,
        position_id: int,
        session_id: int,
        offset: int = 0,
        page_size: int = 20,
    ) -> Tuple[int, list[dict]]:
        total, data = await self.message_dao.pagination(
            user_id=user_id,
            position_id=position_id,
            session_id=session_id,
            offset=offset,
            page_size=page_size,
            sort=[desc(Message.session_id), desc(Message.create_time)],
        )
        return total, data

    async def update_message_feedback(
        self,
        user_id: int,
        message_id: int,
        feedback_type: FeedbackType,
        feedback_content: str,
    ):
        message = await self.message_dao.get(message_id)
        if not message or message.user_id != user_id:
            raise MessageNoFound()

        return await self.message_dao.update(
            message,
            {
                "feedback_type": feedback_type.value,
                "feedback_content": feedback_content,
            },
        )

    async def get_session_by_id(self, session_id: int, user_id: int) -> Session:
        sess = await self.session_dao.get(session_id)
        if not sess or sess.user_id != user_id:
            raise SessionNoFound()
        return sess

    async def list_task_score(self, task_id: int, score_type: TaskScoreType, offset: int = 0, page_size: int = 20):
        total, score_dict = await self.session_dao.group_score_by_user(task_id, score_type, offset, page_size)
        user_ids = list(score_dict.keys())
        users = await self.user_dao.get_users_by_ids(user_ids)
        data = []
        for user in users:
            data.append({**user.model_dump(), "score": score_dict.get(user.user_id, 0)})
        return total, data


async def get_history_manager(
    session_dao: Annotated[SessionDao, Depends(get_session_dao)],
    message_dao: Annotated[MessageDao, Depends(get_message_dao)],
    user_dao: Annotated[UserDao, Depends(get_user_dao)],
):
    yield HistoryManager(session_dao, message_dao, user_dao)
