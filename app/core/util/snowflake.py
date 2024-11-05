from snowflake import SnowflakeGenerator

from app.config import settings

gen = SnowflakeGenerator(settings.app.worker_id)


def gen_snowflake_id():
    return next(gen)


if __name__ == "__main__":
    print(gen_snowflake_id())
