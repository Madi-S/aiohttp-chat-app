import aioredis

from py_settings import log, logger


@log
async def create_redis(app):
    logger.debug('Creating redis pool')
    redis = await aioredis.create_redis_pool('redis://localhost', db=9, timeout=10)
    app['redis'] = redis
    return redis


@log
async def close_redis(app):
    logger.info('Shutting down redis server')
    redis = app['redis']
    redis.close()
    await redis.wait_closed()
