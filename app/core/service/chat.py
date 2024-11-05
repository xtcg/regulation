import asyncio
import logging
import uuid
from typing import Optional, List, Annotated, Tuple

from orjson import orjson
from fastapi import Depends
from pydantic import BaseModel

from app.config.v3 import get_model_and_request_message_for_chat
from app.core.client import ai_client
from app.core.client.redis import redis_client
from app.core.enums import Role, StreamStatus
from app.core.manager import HistoryManager, get_history_manager
# from app.core.schema import MessageData, TextPayload
from app.core.service import knowledge_service

logger = logging.getLogger(__name__)

CHAT_KNOWLEDGE_ID = 0


class KnowledgeContextCache(BaseModel):
    context: str
    filepaths: List[str]


class ChatService:

    def __init__(self, history_manager):
        self.history_manager = history_manager

    async def chat(
        self,
        user_id: int,
        session_id: int,
        text: Optional[str],
        audio: Optional[str],
        chat_history: Optional[list],
        dbs: Optional[list],
    ):
        session = await self.history_manager.get_session_by_id(session_id, user_id)

        question = text
        
        await self.history_manager.create_message(session.session_id, user_id, Role.USER, question)


        context, filepaths = await self.get_knowledge_context(session_id, chat_history, question, dbs)
        # print(context, filepaths)
        str_list = []
        message_id = str(uuid.uuid4())
        # async for chunk in self.get_answer(message_id, chat_history, context, question):
        #     data = {"content": chunk}
        #     str_list.append(chunk)
        #     data = orjson.dumps(data, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_DATACLASS)
        #     yield b"data: " + data + b"\n\n"
        answer = await self.get_answer(message_id, chat_history, context, question)
        reference = f"找到 {len(filepaths)} 篇资料参考：\n" + "\n".join(filepaths)
        # print(filepaths)
        # answer = '\n'.join(str_list)
        logger.info((f"quest {text=}, answer {answer=}"))
        if len(filepaths):
            answer += "\n\n"+reference
            # data  = {"content": reference}
            # data = orjson.dumps(data, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_DATACLASS)
            # yield b"data: " + data + b"\n\n"

        await self.history_manager.create_message(session_id, user_id, Role.ASSISTANT, answer)
        # yield f"data: [done]\n\n"
        return answer

    @staticmethod
    async def get_context_from_redis(session_id: int) -> Tuple[str, List[str]]:
        key = f"chat_context_{session_id}"
        cache = await redis_client.get(key)
        if cache:
            return cache.context, cache.filepaths
        else:
            return '', []

    @staticmethod
    async def set_context_to_redis(session_id: int, context: str, filepaths: List[str]):
        key = f"chat_context_{session_id}"
        cache = KnowledgeContextCache(
            context=context,
            filepaths=filepaths,
        )
        await redis_client.set(key, cache)

    @staticmethod
    async def get_knowledge_context(session_id: int, chat_history: Optional[list], question: str, dbs: list):
        context, filepaths = await ChatService.get_context_from_redis(session_id)
        if len(chat_history) == 0:
            context, filepaths = await knowledge_service.query_and_rerank(dbs, question)
        elif await knowledge_service.is_need_rag(chat_history, context, question):
            context, filepaths = await knowledge_service.query_and_rerank(dbs, question)
        logger.info(f"get_knowledge_context {context=}")
        await ChatService.set_context_to_redis(session_id, context, filepaths)
        return context, filepaths

    @staticmethod
    async def get_answer(message_id: str, chat_history: Optional[list], context: str, question: str):
        logger.debug("get_answer")
        model, request_message = get_model_and_request_message_for_chat(chat_history, context, question)
        str_list = []
        # async for chunk in ai_client.chat_return_sentence(model, request_message):
        #     yield chunk
        answer = await ai_client.chat_once(model, request_message)
        logger.info(f"get_answer done, {answer=}")
        return answer


async def get_chat_service(
    history_manager: Annotated[HistoryManager, Depends(get_history_manager)],
):
    yield ChatService(history_manager)

