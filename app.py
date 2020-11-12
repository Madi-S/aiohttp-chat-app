import aioredis
import asyncio

import aiohtt_jinja2
import jinja2

from aiohttp import web
from aiohttp_session import setup, get_session
from aiohttp_session.redis_storage import RedisStorage

from routes import setup_routes
from db import start_db, close_db

import logging

formatter = logging.Formatter(
    style='{', fmt='{name} - {levelName} - {asctime} - {pathname} - {lineNo} - {message}')

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def log(f):
    def inner(*args, **kwargs):
        method = f.__name__
        try:
            logger.debug('Method %s was called received: %s and %s',
                         method, *args, **kwargs)
            return f(*args, **kwargs)
        except Exception:
            logger.exception('Error in method %s:', method, exc_info=True)
            raise

    return inner


@log
async def get_redis(app):
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


@log
def main():
    app = web.Application()

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))

    app.on_cleanup.append(start_db)
    app.on_cleanup.append(close_db)

    try:
        loop = asyncio.get_event_loop()
        redis = get_redis(app)
        redis_loop = loop.run_until_complete(redis)
        storage = RedisStorage(redis_loop)
        app.on_cleanup.append(close_redis)

    except ConnectionRefusedError:
        logger.warning(
            'Cannot connect to redis server, switching to standard "EncryptedCookieStorage"')
        import base64
        from cryptography import fernet
        from aiohttp_session.cookie_storage import EncryptedCookieStorage

        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        storage = EncryptedCookieStorage(secret_key)

    setup_routes(app)
    setup(app, storage)


if __name__ == '__main__':
    main()
