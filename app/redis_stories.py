import json

import redis

STORIES_HASH_NAME = 'stories'
FULL_STORIES_HASH_NAME = 'stories_full'

class RedisStories:
    def __init__(self, host, port=6379, db=0):
        
        self.redis = redis.Redis(
            host=host, port=port, db=db
        )

    def is_ready(self) -> bool:
        try:
            self.redis.ping()
            return True
        except redis.exceptions.ConnectionError:
            return False

    def add( self, id, story, full ):
        self.redis.hset( STORIES_HASH_NAME if not full else FULL_STORIES_HASH_NAME, id, json.dumps(story))

    def has(self, id, full) -> bool:
        return self.redis.hexists( STORIES_HASH_NAME if not full else FULL_STORIES_HASH_NAME, id )

    def get(self, id, full):
        raw_story = self.redis.hget( STORIES_HASH_NAME if not full else FULL_STORIES_HASH_NAME, id )
        return json.loads(raw_story)

    def clear(self):
        self.redis.delete(STORIES_HASH_NAME)
        self.redis.delete(FULL_STORIES_HASH_NAME)