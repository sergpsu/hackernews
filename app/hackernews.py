import aiohttp
import asyncio
from config import logger, settings
from redis_stories import RedisStories

BASE_URL = 'https://hacker-news.firebaseio.com/v0/'
class HackerNews:
    __slots__ = (
        'redis',
    )
    def __init__(self):
        self.redis = RedisStories(host=settings.REDIS_HOST, 
                             port=settings.REDIS_PORT, 
                             db=settings.REDIS_DB)
                    
    
    async def get_story(self, id, full=False):
        if self.redis.has( id, full ):
            logger.info( f'using cached {id} ({full=})')
            return self.redis.get( id, full )
        
        async with aiohttp.ClientSession() as session:
            url = HackerNews.get_item_url(id)
            #logger.info( f'{url=}')
            async with session.get(url) as resp:
                story = await resp.json()
                #logger.info( f'{story=}')
                
                if story['type'] != 'story':
                    raise Exception( f'item {id} is not a story')
                
                if 'deleted' in story and story['deleted'] is True:
                    raise Exception( f'story {id} is deleted')
                if 'dead' in story and story[ 'dead'] is True:
                    raise Exception( f'story {id} is dead')

                res = {'id': int(id),
                       'title': story['title'],
                       'text': story['text'] if 'text' in story else story['url'],
                       'time': story[ 'time' ]
                    }
                
                if full is True and 'kids' in story:
                    comments = []
                    await self._get_comments_tree( session, comments, story['kids'] )
                    res[ 'comments' ] = comments
                
                self.redis.add(id, res, full )
                
                return res
            
    async def _get_comments_tree( self, session, res, ids ):
        tasks = await asyncio.wait([ asyncio.Task(self._get_comment_tree( session, id )) for id in ids])
        for task in tasks[0]:
            res.append(task.result())
            
    async def _get_comment_tree( self, session, id ):
        url = HackerNews.get_item_url(id)
        async with session.get(url) as resp:
            comment = await resp.json()
            if comment[ 'type' ] == 'comment':
                #logger.info(comment)
                    
                if ('deleted' not in comment or comment[ 'deleted'] is False) and \
                    ('dead' not in comment or comment['dead'] is False):
                    replies = []
                    if 'kids' in comment:
                        await self._get_comments_tree( session, replies, comment['kids'])
                    return {
                        'id': int(comment[ 'id' ]),
                        'text': comment['text'],
                        'replies': replies,
                        'time': comment['time']
                    }

                        
    async def get_best_stories(self, limit):
        async with aiohttp.ClientSession() as session:
            url = HackerNews.get_url('beststories')
            async with session.get(url) as resp:
                res = []
                ids = await resp.json()
                ids = ids[:limit]
                #logger.info(ids)
                tasks = []
                for id in ids:
                    tasks.append( asyncio.Task( self.get_story(id, full=False) ) )
                res = await asyncio.wait( tasks )
                
                for task in res[0]:
                    logger.info(task)
                
                return [task.result() for task in res[0] ]
                
            
    @staticmethod
    def get_url(uri):
        return f'{BASE_URL}{uri}.json'
    
    @staticmethod
    def get_item_url(id):
        return HackerNews.get_url(f'item/{id}')