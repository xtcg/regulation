from pydantic import BaseModel
from starlette.authentication import BaseUser


class CurrentUser(BaseUser):
    user_id: int
    username: str

    def __init__(self, user_id: int, username: str):
        self.user_id = user_id
        self.username = username

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def identity(self) -> str:
        return str(self.user_id)


class ThirdUserInfo(BaseModel):
    third_user_id: str
    username: str
    mobile: str
