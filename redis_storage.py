import aioredis
import asyncio

from aiohttp_session.redis_storage import RedisStorage

from py_settings import log, logger


@log
async def setup_redis_storage(app):
    logger.debug('Creating redis pool')

    loop = asyncio.get_event_loop()
    redis = await aioredis.create_redis_pool('redis://localhost', db=9, timeout=10)
    redis_loop = loop.run_until_complete(redis)

    app['redis'] = redis

    return RedisStorage(redis_loop)


@log
async def close_redis(app):
    logger.info('Shutting down redis server')
    redis = app['redis']
    redis.close()
    await redis.wait_closed()
