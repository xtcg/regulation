import logging
from typing import List
import requests
import numpy as np
from aiohttp import ClientSession
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as langchain_Document

from app.config import settings, v3
from app.core.client import ai_client
from app.core.client.jina import jina_embedding
from app.core.database import KnowledgeDao
from app.core.database.db import get_session
from app.core.exception import BadRequest, ServerException
from app.core.model import Knowledge
from app.core.schema import MessageData

logger = logging.getLogger(__name__)


class KnowledgeService:
    def __init__(self, base_dir: str, rerank_url: str, api_key: str, model: str):
        self.dbs = {}
        self.base_dir = base_dir
        self.url = rerank_url
        self.api_key = api_key
        self.model = model
        
    async def _load_dbs(self):
        if self.dbs:
            return

        result = []
        async for sess in get_session():
            result = await KnowledgeDao(Knowledge, sess).list()
        
        for item in result:
            if item.knowledge_id != 6:
                continue
            self.dbs[item.knowledge_id] = FAISS.load_local(
                f"{self.base_dir}/{item.folder}",
                embeddings=jina_embedding,
                allow_dangerous_deserialization=True,
            )
        print(len(self.dbs))

    async def get_related_knowledge(
        self, knowledge_id: list, query: str, k: int,threshold=0.85
    ):
        await self._load_dbs()
        docs = []
        for knowledge in knowledge_id:
            db = self.dbs.get(knowledge)
            if not db:
                raise BadRequest(f"invalid knowledge_id {knowledge_id}")


            retriever = db.as_retriever(search_kwargs={"k": k})
            docs.extend(retriever.invoke(query))
        logger.info(f"get_related_knowledge {len(docs)=}")
        return docs[:k]

    async def rerank_content(
        self, query: str, docs: List[langchain_Document], top_n: int = 5
    ):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {"model":self.model, "query": query, "documents": [doc.page_content[:512] for doc in docs]}
        logger.info(f"rerank {self.url=}, {payload=}")
        try:
            response = requests.request("POST", url=self.url, json=payload, headers=headers)
            if response.status_code != 200:
                raise ServerException(
                    f"Error Code {response.status}, {response.text}"
                )
            relevance = response.json()
            logger.info(f"rerank {relevance=}")
            text_selected = [docs[dp["index"]] for dp in relevance["results"][:top_n]]
            return text_selected

        except Exception as err:
            logger.error(f"rerank_content error: {err}")
            raise ServerException("rerank_content failed")

    async def query_and_rerank(self, knowledge_id: list, query, top_n=5):
        docs = await self.get_related_knowledge(knowledge_id, query, top_n)
        if not docs:
            return "", []
        docs = await self.rerank_content(query, docs, top_n)
        if not docs:
            return "", []
        context_str = ""
        filepaths = []
        filepaths_dict = {}
        for i, doc in enumerate(docs):
            if 'raw' not in doc.metadata:
                page_content = doc.page_content
            else:
                index = doc.metadata['raw'].index(doc.page_content)
                if index > 1000:
                    page_content = doc.metadata['raw'][:1000] + doc.metadata['raw'][index-1000:index+3000]
                else:
                    page_content = doc.metadata['raw'][:index+4000]
                if 'ammend' in doc.metadata:
                    page_content += doc.metadata['ammend'][:4000]
            if (
                len(context_str) + len(page_content) >= 16000
                and len(context_str) >= 1
            ):
                break
            else:
                context_str += (
                    f"文档{i+1}相关内容如下:\n{page_content[:8000]}\n"
                )
                file_key = "".join(doc.metadata["source"])
                if file_key not in filepaths_dict:
                    filepaths.append(doc.metadata["source"])
                    filepaths_dict[file_key] = None
        return context_str, filepaths

    @classmethod
    async def is_need_rag(
        cls, chat_history: List[MessageData], context: str, query: str
    ):
        prompt_template = """你是一个多轮对话系统中的智能助手，当前你的任务是判断：当前轮次用户的提问是否需要在重新在文档库内检索新的知识。
具体来说，你将接收到的信息如下：
<之前轮次检索的信息>
{context}
</之前轮次检索到的信息>

<之前的对话历史>
{chat_history}
</之前的对话历史>

<当前用户问题>
{query}
</当前用户问题>

请你理解<之前的对话历史>和<当前用户问题>，并判断<之前轮次检索的信息>中是否包含相关的、有效的信息，可以用来回答<当前用户问题>。
请基于以上信息判断对于当前用户的问题是否需要重新在文档库中检索，并输出（且只输出）True或False。
当<之前轮次检索的信息>和<之前的对话历史>为空时，就代表你正在处理第一轮的对话，你就只需要判断出该用户提出的问题是在和你闲聊还是真的需要你检索数据库即可。

注意，你只需要输出"True"或者"False"，不要输出其他内容。
"""

        chat = ""
        for message in chat_history:
            chat += f"{message['role']}: {message['content']}\n"

        _content = prompt_template.format(
            context=context, chat_history=chat, query=query
        )
        messages = [{"role": "user", "content": _content}]

        result = await ai_client.chat_once(
            model=v3.DEFAULT_MODEL, request_message=messages, temperature=0.99
        )
        logger.info(f"is_need_rag {result=}")

        return True if (result and "True" in result) else False


knowledge_service = KnowledgeService(
    settings.knowledge.base_dir, settings.knowledge.rerank_url, settings.knowledge.api_key, settings.knowledge.rerank_model
)
