from pydantic import BaseModel


class Session(BaseModel):
    session_id: int
    user_id: int
    position_id: int
    session_type: int
    character_id: int
    scene_id: int
    character_name: str
    first_message: str
    last_message: str
    score: int
    deleted: bool

    class Config:
        from_attributes = True
