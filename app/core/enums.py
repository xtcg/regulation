from enum import Enum, StrEnum, IntEnum


class WebsocketCmdType(Enum):
    QUESTION = "question"
    ANSWER = "answer"
    SCORE = "score"
    CHAT = "chat"


class StreamStatus(IntEnum):
    START = 0
    PROCESSING = 1
    END = 2


class OpenaiCmdType(StrEnum):
    QUESTION = "question"
    SCORE = "score"
    SINGLE_SCORE = "single_score"
    ANSWER = "answer"
    SINGLE_ANALYSE = "single_analyse"


class Category(StrEnum):
    PANEL = "panel"
    WARDROBE = "wardrobe"
    WALLBOARD = "wallboard"
    DEFAULT = "default"
    WOODEN_DOOR = "wooden_door"


class Role(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    ASSISTANT_SCORE = "assistant_score"
    SCORE = "score"
    SYSTEM = "system"


class SessionType(Enum):
    CHAT = 1
    EXERCISE = 2
    TASK_EXERCISE = 3
    TASK_EXAM = 4


class FeedbackType(Enum):
    LIKE = 1
    UNLIKE = 2


class CourseType(IntEnum):
    ONLINE = 1
    OFFLINE = 2
    MIX = 3


class TaskType(IntEnum):
    AI = 1


class TaskScoreType(IntEnum):
    MAX = 1
    LAST = 2
