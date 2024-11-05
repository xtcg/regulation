import json
import logging
import re
import random
from app.config import BASEDIR
from app.core.client import openai


logger = logging.getLogger(__name__)


filepath = BASEDIR.joinpath("configs/model_keys.json")
with open(filepath) as config_file:
    model_keys: dict[str, dict] = json.load(config_file)


def get_client(model):
    model_key = model_keys.get(model, None)
    if model_key:
        model_key = model_key[0]
        return openai.Client(
            api_key=model_key["api_key"],
            base_url=model_key["base_url"],
        )
    return None



async def chat_stream(model, request_message):
    client = get_client(model)
    async for text in client.chat_stream(model, request_message):
        yield text


async def chat_once(model, request_message, temperature=0.8, top_p=1):
    client = get_client(model)
    return await client.chat(model, request_message, temperature, top_p)


async def chat_return_sentence(model, request_message, temperature=0.8, top_p=1):

    def split_sentences(text: str) -> list[str]:
        # 使用正则表达式按照标点符号切割句子，并保留标点符号
        return re.split(r"(?<=[。？！])", text)

    client = get_client(model)

    buffer = ""
    async for part in client.chat_stream(model, request_message, temperature, top_p):
        buffer += part

        # 检查缓冲区中是否有标点符号
        if re.search(r"[。？！]", buffer):
            sentences = split_sentences(buffer)

            # 保留最后一个部分，可能是未完成的句子
            if sentences:
                buffer = sentences.pop()

            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:  # 确保不返回空字符串
                    # logger.info(f"chat_return_sentence {sentence =} ")
                    yield sentence

    # 最后处理剩余的缓冲区内容
    buffer = buffer.strip()
    if buffer:
        # logger.info(f"chat_return_sentence {buffer =} ")
        yield buffer

