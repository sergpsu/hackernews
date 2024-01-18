"""http endpoints"""
import traceback
import time
from functools import wraps
from aiohttp import web
from config import logger
from redis_stories import RedisStories
from hackernews import HackerNews, HNBaseException


routes = web.RouteTableDef()
hackernews = HackerNews()


def return_400_on_exception(http_endpoint):
    """decorator for generic processing of exceptions in http endpoints"""
    @wraps(http_endpoint)
    async def wrapper(*args, **kwargs):
        try:
            res = await http_endpoint(*args, **kwargs)
            return res
        except HNBaseException as e:
            return web.json_response({'error': str(e)}, status=400)
        except Exception:
            logger.error(traceback.format_exc())
            raise

    return wrapper


@routes.get('/topstories')
@return_400_on_exception
async def top_stories(*_unused):
    """returns first 10 stories returned by HN /beststories API"""
    stories = await hackernews.get_best_stories(10)
    return web.json_response(stories)


@routes.get('/stories/{story_id}')
@return_400_on_exception
async def stories_item(request):
    """return story with full tree of comments by id"""
    story_id = request.match_info['story_id']

    logger.info('getting story %s', story_id)
    story = await hackernews.get_story(story_id, full=True)

    return web.json_response(story)


def create_app():
    """used by main.py and tests"""

    # waiting until Redis is ready
    redis = RedisStories()
    while redis.is_ready() is False:
        time.sleep(1)

    # start web app
    app = web.Application()
    app.add_routes(routes)
    return app
