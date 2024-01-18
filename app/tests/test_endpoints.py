import pytest
from app import create_app
from redis_stories import RedisStories
from config import settings


@pytest.fixture
def redis():
    res = RedisStories()
    res.clear()
    return res


@pytest.fixture
async def server(aiohttp_server):
    app = create_app()
    return await aiohttp_server(app)


@pytest.fixture
async def client(aiohttp_client, server):
    return await aiohttp_client(server)



async def test_topstories(client, redis):
    resp = await client.get('/topstories')

    assert resp.status == 200

    stories = await resp.json()
    assert len(stories) == 10

    for story in stories:
        assert redis.has(story['id'], full=False)


async def test_story1(client, redis):
    # cache is clear
    assert redis.has(1, True) is False

    # story is fetched from web
    resp = await client.get('/stories/1')
    assert resp.status == 200
    story = await resp.json()
    assert story['id'] == 1

    # now cache contains full story with id=1
    assert redis.has(1, True) is True


    