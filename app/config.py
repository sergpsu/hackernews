"""configuration class and logger utils"""
import logging
from pydantic import AnyUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """settings taken from env vars"""
    HACKERNEWS_API_URL: AnyUrl = 'https://hacker-news.firebaseio.com/v0/'

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    LOG_LEVEL: str = 'INFO'


settings = Settings()
logger = logging.getLogger()


def setup_logger():
    """should be called on the app start"""
    level = logging.getLevelName(settings.LOG_LEVEL.upper())
    logger.setLevel(level)

    handler = logging.StreamHandler()
    logger.addHandler(handler)
