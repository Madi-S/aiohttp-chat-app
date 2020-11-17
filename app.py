import aiohttp_jinja2
import jinja2

import aioreloader

from aiohttp import web
from aiohttp_session import setup as setup_session, get_session

from routes import setup_routes
from db import start_db, close_db

from py_settings import log, logger
from web_csrf import setup_csrf


@log
def main():
    app = web.Application()

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    app['static_root_url'] = '/static'
    app.router.add_static('/static', 'static', name='static')

    app.on_startup.append(start_db)
    app.on_cleanup.append(close_db)

    # Setup redis storage if redis server is on
    try:
        import asyncio
        import aioredis
        from aiohttp_session.redis_storage import RedisStorage

        async def make_redis_pool(app):
            return await aioredis.create_redis_pool(('127.0.0.1', '6379'), db=5, timeout=5)

        async def dispose_redis_pool(app):
            redis_pool.close()
            await redis_pool.wait_closed()

        loop = asyncio.get_event_loop()
        redis_pool = loop.run_until_complete(make_redis_pool(app))

        storage = RedisStorage(redis_pool)
        app.on_cleanup.append(dispose_redis_pool)

    # Setup encrypted storage if redis server is off
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
    logger.debug('Routes were setup')

    setup_session(app, storage)
    logger.debug('Storage was setup')

    setup_csrf(app, 'csrf_storage')
    logger.debug('csrf protection was setup')

    aioreloader.start()
    logger.debug('Start with code reload')

    web.run_app(app, port=8000)


if __name__ == '__main__':
    main()
