import aioredis
import asyncio
from aiohttp import app
from aiohttp_session import setup, get_session
from aiohttp_session.redis_storage import RedisStorage

from routes import setup_routes

import logging

formatter = logging.Formatter(style='{', fmt='{name} - {levelName} - {asctime} - {pathname} - {lineNo} - {message}')

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

logger = logging.get_logger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)



async def get_redis():
    return await aioredis.create_redis_pool()


async def close_redis():
    redis.close()
    await redis.wait_closed()





def main():
    app = web.Application()

    try:

        loop = asyncio.get_event_loop()
        redis = get_redis()
        redis_loop  =asyncio.run_until_complete(redis)
        storage = RedisStorage(redis_loop)
        app.on_cleanup.append(close_redis)

    except ConnectionRefusedError:

    setup_routes(app)

    setup(app, storage)






if __name__ == '__main__':
    main()