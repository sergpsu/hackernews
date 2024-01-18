"""HN stories cache implemented as redis hashes"""
import json
import redis

from config import settings

STORIES_HASH_NAME = 'stories'
FULL_STORIES_HASH_NAME = 'stories_full'


class RedisStoriesMeta(type):
    """helper class for singleton implementation"""
    _instances = {}

    def __call__(cls):
        """singleton implementation"""
        if cls not in cls._instances:
            instance = super().__call__(host=settings.REDIS_HOST,
                                        port=settings.REDIS_PORT,
                                        db=settings.REDIS_DB)
            cls._instances[cls] = instance
        return cls._instances[cls]


class RedisStories(metaclass=RedisStoriesMeta):
    """implements caching. Use get_instance() to single"""

    __slots__ = (
        'redis',
    )

    def __init__(self, host, port, db):
        self.redis = redis.Redis(
            host=host, port=port, db=db
        )

    def is_ready(self) -> bool:
        """checks if redis server is up"""
        try:
            self.redis.ping()
            return True
        except redis.exceptions.ConnectionError:
            return False

    def add(self, story_id, story, full):
        """adds a story to cache"""
        self.redis.hset(
            STORIES_HASH_NAME if not full else FULL_STORIES_HASH_NAME, story_id, json.dumps(story))

    def has(self, story_id, full) -> bool:
        """checks if story is in cache"""
        return self.redis.hexists(STORIES_HASH_NAME if not full else FULL_STORIES_HASH_NAME, story_id)

    def get(self, story_id, full):
        """gets story from cache"""
        raw_story = self.redis.hget(
            STORIES_HASH_NAME if not full else FULL_STORIES_HASH_NAME, story_id)
        return json.loads(raw_story)

    def clear(self):
        """remove all cached items"""
        self.redis.delete(STORIES_HASH_NAME)
        self.redis.delete(FULL_STORIES_HASH_NAME)
