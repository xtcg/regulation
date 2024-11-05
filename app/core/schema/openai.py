from typing_extensions import TypedDict, Literal


class MessageData(TypedDict, total=False):
    role: Literal["user", "assistant"]
    content: str
