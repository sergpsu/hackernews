"""testing endpoints"""
import pytest
from redis_stories import RedisStories
from app import create_app


@pytest.fixture(name='redis')
def redis_f():
    res = RedisStories()
    res.clear()
    return res


@pytest.fixture(name='server')
async def server_f(aiohttp_server):
    app = create_app()
    return await aiohttp_server(app)


@pytest.fixture(name='client')
async def client_f(aiohttp_client, server):
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
