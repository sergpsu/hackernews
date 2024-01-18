import logging
from pydantic import AnyUrl, AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    HACKERNEWS_API_URL: AnyUrl = 'https://hacker-news.firebaseio.com/v0/'

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
#    REDIS_PROTOCOL: int = 2

    LOG_LEVEL: str = 'INFO'


settings = Settings()
logger = logging.getLogger()


def setup_logger():
    level = logging.getLevelName(settings.LOG_LEVEL.upper())
    logger.setLevel(level)

    handler = logging.StreamHandler()
    # handler.setLevel(logging.DEBUG)
    # handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)-5s] %(message)s'))

    logger.addHandler(handler)
