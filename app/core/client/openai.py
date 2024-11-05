import logging
from datetime import datetime

from openai import AsyncOpenAI
from prometheus_client import Counter, Histogram

from app.config.base import settings

logger = logging.getLogger(__name__)

AI_REQUEST_TOTAL = Counter(
    name="ai_request_total",
    documentation="Total count of ai requests",
    labelnames=["func", "client", "error"],
)

AI_REQUEST_FIRST_TOKEN_SECONDS = Histogram(
    name="ai_request_first_token_seconds",
    documentation="first token duration of ai requests",
    labelnames=["func", "client"],
    buckets=(0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, float("inf")),
)

AI_REQUEST_DURATION_SECONDS = Histogram(
    name="ai_request_duration_seconds",
    documentation="process duration of ai requests",
    labelnames=["func", "client", "error"],
    buckets=(1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 30.0, 40.0, 50.0, float("inf")),
)


class Client:

    def __init__(self, api_key: str, base_url: str = None):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    # def speech_to_text(self, audio_path: str) -> str:
    #     audio_file = open(audio_path, "rb")
    #     transcription = self.client.audio.transcriptions.create(
    #         model="whisper-1", file=audio_file
    #     )
    #     return transcription.text
    #
    # def text_to_speech(self, input: str, audio_path: str):
    #     response = self.client.audio.speech.create(
    #         model="tts-1", voice="alloy", input=input
    #     )
    #     response.stream_to_file(audio_path)

    async def chat(self, model, request_message, temperature=1, top_p=1):
        logger.info(f"openai.chat {model=}, {request_message=}")
        retry = 0
        while retry < 3:
            start = datetime.now().timestamp()
            err_name = ""
            try:
                completion = await self.client.chat.completions.create(
                    model=model,
                    messages=request_message,
                    max_tokens=4095,
                    temperature=temperature,
                    top_p=top_p,
                    timeout=30,
                )
                return completion.choices[0].message.content

            except BaseException as e:
                logger.error(f"An unexpected error occurred: {e}")
                retry += 1
                err_name = type(e).__name__
            finally:
                duration = datetime.now().timestamp() - start
                logger.info(f"openai.chat {duration = }")
                AI_REQUEST_TOTAL.labels("openai.chat", model, err_name).inc()
                AI_REQUEST_DURATION_SECONDS.labels(
                    "openai.chat", model, err_name
                ).observe(duration)

    async def chat_stream(self, model, request_message, temperature=1, top_p=1):
        # logger.info(f"openai.chat {model = }, {request_message =}")
        retry = 0
        while retry < 3:
            start = datetime.now().timestamp()
            err_name = ""
            try:
                stream = await self.client.chat.completions.create(
                    model=model,
                    messages=request_message,
                    stream=True,
                    max_tokens=4095,
                    temperature=temperature,
                    top_p=top_p,
                    timeout=15,
                )
                first_token = True
                response = ""
                async for chunk in stream:
                    if not chunk.choices:
                        continue

                    if first_token:
                        first_token = False
                        first_token_duration = datetime.now().timestamp() - start
                        AI_REQUEST_FIRST_TOKEN_SECONDS.labels(
                            "openai.chat_stream", model
                        ).observe(first_token_duration)

                    chunk_response = chunk.choices[0].delta.content
                    if chunk_response:
                        response += chunk_response
                        yield chunk_response
                        # logger.info(f"{chunk_response =} ")
                return

            except BaseException as e:
                logger.error(f"An unexpected error occurred: {e}")
                retry += 1
                err_name = type(e).__name__
            finally:
                duration = datetime.now().timestamp() - start
                logger.info(f"openai.chat_stream {duration = }")
                AI_REQUEST_TOTAL.labels("openai.chat_stream", model, err_name).inc()
                AI_REQUEST_DURATION_SECONDS.labels(
                    "openai.chat", model, err_name
                ).observe(duration)


openai_client = Client(**settings.openai.model_dump())
