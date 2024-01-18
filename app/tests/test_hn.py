import pytest
from hackernews import HackerNews, HNItemNotFound, HNItemNotStory
from redis_stories import RedisStories


@pytest.fixture
def redis():
    res = RedisStories()
    return res


@pytest.fixture
def hn(redis):
    redis.clear()
    return HackerNews()


async def test_non_existing_item(hn):
    try:
        await hn.get_story(0xffffffff)
        assert False
    except HNItemNotFound:
        assert True
    except Exception:
        assert False


async def test_non_story(hn):
    try:
        await hn.get_story(234509)
        assert False
    except HNItemNotStory:
        assert True
    except Exception:
        assert False


async def test_redis_singleton():
    r1 = RedisStories()
    r2 = RedisStories()
    assert r1 is r2
