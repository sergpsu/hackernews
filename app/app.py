from aiohttp import web
from hackernews import HackerNews
from config import logger

routes = web.RouteTableDef()
hackernews = HackerNews()


@routes.get('/topstories')
async def top_stories(request):
    stories = await hackernews.get_best_stories(10)
    return web.json_response(stories)


@routes.get('/stories/{id}')
async def stories_item(request):
    id = request.match_info['id']

    logger.info(f'getting story {id}')
    story = await hackernews.get_story(id, full=True)

    return web.json_response(story)


def create_app():
    app = web.Application()
    app.add_routes(routes)
    return app
