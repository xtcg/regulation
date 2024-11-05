# 使用总的知识库来问答

import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse
from utilswaves.authentication import get_current_user
from utilswaves.schema import ApiResponse
from app.config.db import get_db_info, get_db_tier1, searchdb
from app.core.manager import (
    HistoryManager,
    get_history_manager,
)
from app.core.schema import CurrentUser, Session
from app.core.service.chat import ChatService, get_chat_service
from app.vo.session import SendMessageRequest, UserLogin, AnswerRequest, SendDbinfo, DBtier1, DBtier2, SearchDB

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "/init_session",
    summary="初始化会话",
    response_model=ApiResponse[Session],
)
async def init_session(
    body: UserLogin,
    history_manager: Annotated[HistoryManager, Depends(get_history_manager)],
):
    session = await history_manager.create_chat_session(body.user_id)
    return ApiResponse(data=session)

@router.post(
    "/db_info",
    summary="获取知识库二级信息",
    response_model=ApiResponse[DBtier2],
)
async def init_session(
    body: SendDbinfo,
):
    res = get_db_info(body.db_info)
    return ApiResponse(data=res)

@router.get(
    "/db_info_tier1",
    summary="获取知识库一级信息",
    response_model=ApiResponse[DBtier1],
)
async def init_session():
    res = get_db_tier1()
    return ApiResponse(data=res)

@router.post(
    "/send_msg",
    summary="发送问题，获取答案",
    response_model=ApiResponse[AnswerRequest],
)
async def send_msg(
    body: SendMessageRequest,
    service: Annotated[ChatService, Depends(get_chat_service)],
    history_manager: Annotated[HistoryManager, Depends(get_history_manager)],
):  

    ans = await service.chat(body.user_id, body.session_id, body.text, body.audio, body.chat_history, body.selected_dbs)
    res = AnswerRequest(session_id=body.session_id,text=ans,files=[],audio='',chat_history=[{}])
    return ApiResponse(data=res.model_dump())
    # return StreamingResponse(service.chat(body.user_id, body.session_id, body.text, body.audio, body.chat_history, body.selected_dbs), media_type="text/event-stream")


@router.post(
    "/search",
    summary="获取知识库一级信息",
    response_model=ApiResponse[DBtier1],
)
async def search(body: SearchDB):
    res = searchdb(body.db_info)
    return ApiResponse(data=res)