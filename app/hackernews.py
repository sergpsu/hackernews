"""Implements HackerNews API"""
import asyncio
import aiohttp
from config import logger, settings
from redis_stories import RedisStories


class HNBaseException(Exception):
    """Base class for exceptions"""

    def __init__(self, item_id):
        self.item_id = item_id

    def __str__(self):
        return f'{type(self).__name__}: item_id={self.item_id}'


class HNItemNotFound(HNBaseException):
    """Thrown when /item/{item_id} API endpoint returns 404"""


class HNItemNotStory(HNBaseException):
    """Thrown when on getting story item by id API endpoint returns not a 'story' item"""

    def __init__(self, item_id, item_type):
        super().__init__(item_id)
        self.item_type = item_type

    def __str__(self):
        return f'item {self.item_id} is not a story, but {self.item_type}'


class HNItemDeleted(HNBaseException):
    """Throw when item is marked as deleted"""


class HNItemDead(HNBaseException):
    """Throw when item is marked as dead"""


class HackerNews:
    """Implements HackerNews API. Uses Redis for caching results"""
    __slots__ = (
        'redis',
    )

    def __init__(self):
        self.redis = RedisStories()

    async def get_story(self, story_id, full=False):
        """Get a story by id from redis cache or by calling API.
        Parameter `full` is used to either include full tree of comments into result or not """
        if self.redis.has(story_id, full):
            return self.redis.get(story_id, full)

        async with aiohttp.ClientSession() as session:
            url = HackerNews.get_item_url(story_id)
            # logger.info( f'{url=}')
            async with session.get(url) as resp:
                logger.info(resp.status)
                story = await resp.json()
                if story is None:
                    raise HNItemNotFound(story_id)

                if story['type'] != 'story':
                    raise HNItemNotStory(story_id, story['type'])

                if 'deleted' in story and story['deleted'] is True:
                    raise HNItemDeleted(story_id)
                if 'dead' in story and story['dead'] is True:
                    raise HNItemDead(story_id)

                res = {'id': int(story_id),
                       'title': story['title'],
                       'text': story['text'] if 'text' in story else story['url'],
                       'time': story['time']
                       }

                if full is True and 'kids' in story:
                    comments = []
                    await self._get_comments_tree(session, comments, story['kids'])
                    res['comments'] = comments

                self.redis.add(story_id, res, full)

                return res

    async def _get_comments_tree(self, session, res, ids):
        tasks = await asyncio.wait([asyncio.Task(self._get_comment_tree(session, comment_id)) for comment_id in ids])
        for task in tasks[0]:
            res.append(task.result())

    async def _get_comment_tree(self, session, comment_id):
        url = HackerNews.get_item_url(comment_id)
        async with session.get(url) as resp:
            comment = await resp.json()
            if comment['type'] == 'comment':
                # logger.info(comment)

                if ('deleted' not in comment or comment['deleted'] is False) and \
                        ('dead' not in comment or comment['dead'] is False):
                    replies = []
                    if 'kids' in comment:
                        await self._get_comments_tree(session, replies, comment['kids'])
                    return {
                        'id': int(comment['id']),
                        'text': comment['text'],
                        'replies': replies,
                        'time': comment['time']
                    }

    async def get_best_stories(self, limit):
        """/topstories API implementation"""
        async with aiohttp.ClientSession() as session:
            url = HackerNews.get_url('beststories')
            async with session.get(url) as resp:
                res = []
                ids = await resp.json()
                ids = ids[:limit]
                # logger.info(ids)
                tasks = []
                for story_id in ids:
                    tasks.append(asyncio.Task(
                        self.get_story(story_id, full=False)))
                res = await asyncio.wait(tasks)

                return [task.result() for task in res[0]]

    @staticmethod
    def get_url(uri):
        """returns full API url"""
        return f'{settings.HACKERNEWS_API_URL}{uri}.json'

    @staticmethod
    def get_item_url(item_id):
        """returns full /item/{item_id} API url """
        return HackerNews.get_url(f'item/{item_id}')
