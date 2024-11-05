import logging
from pathlib import Path
from typing import Type, Optional

from pydantic import BaseModel, ValidationError, HttpUrl, Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    YamlConfigSettingsSource,
    PydanticBaseSettingsSource,
)

logger = logging.getLogger(__name__)

BASEDIR = Path(__file__).absolute().parent.parent.parent
STATIC_DIR = BASEDIR.joinpath("static")


class AppSettings(BaseModel):
    debug: bool = False
    worker_id: int = 1


class HermesSettings(BaseModel):
    notify_url: HttpUrl = Field(default=None, description="通知地址")
    webhook: str = Field(default=None, description="hook地址")


class XfyunSettings(BaseModel):
    app_id: str
    api_key: str
    api_secret: str


class OpenAISettings(BaseSettings):
    api_key: str
    base_url: Optional[str] = None



class MysqlSettings(BaseModel):
    db_url: str
    engine_args: Optional[dict] = {"pool_recycle": 3600}
    session_args: dict = {"expire_on_commit": False}


class RedisSettings(BaseModel):
    url: str


class JWTSettings(BaseModel):
    secret: str
    lifetime_seconds: int = 60 * 60 * 2
    algorithm: str = "HS256"
    public_key: Optional[str] = None


class KnowledgeSettings(BaseModel):
    base_dir: str
    api_key: str
    rerank_url: str
    rerank_model: str
    embedding_url: str
    embedding_model: str



class Settings(BaseSettings):
    app_name: Optional[str]
    namespace: str = "local"
    version: str = "v1.2"

    file_url: str

    app: AppSettings = AppSettings()
    # hermes: HermesSettings
    # jwt: JWTSettings

    # xfyun: XfyunSettings
    openai: OpenAISettings
    knowledge: KnowledgeSettings

    mysql: MysqlSettings
    redis: RedisSettings

    model_config = SettingsConfigDict(
        extra="ignore",
        env_nested_delimiter="__",
        env_file=BASEDIR.joinpath(".env"),
        yaml_file=BASEDIR.joinpath("configs/default.yaml"),
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ):
        """
        返回顺序即优先级顺序
        从高到低依次为：环境变量，dot变量，yaml文件、默认值
        """
        return (
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            init_settings,
        )


try:
    settings = Settings()
except ValidationError as e:
    logging.basicConfig(level=logging.INFO)
    logger.error("Init Settings Error")
    logger.error(e)

# if __name__ == "__main__":
#     print(Settings.model_json_schema())
