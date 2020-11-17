import asyncio

import aiohttp_jinja2
import jinja2

import aioreloader

import aiohttp_csrf

from aiohttp import web
from aiohttp_session import setup, get_session
from aiohttp_session.redis_storage import RedisStorage

from routes import setup_routes
from db import start_db, close_db

from py_settings import log, logger
from redis_storage import create_redis, close_redis


@log
def main():
    app = web.Application()

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    app['static_root_url'] = '/static'
    app.router.add_static('/static', 'static', name='static')

    app.on_startup.append(start_db)
    app.on_cleanup.append(close_db)

    try:
        loop = asyncio.get_event_loop()
        redis = create_redis(app)
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
    logger.debug('Routes were setup')

    setup(app, storage)
    logger.debug('Storage was setup')

    aioreloader.start()
    logger.debug('Start with code reload')

    web.run_app(app, port=8000)



def setup_csrf(app):
    FORM_FIELD_NAME = '_csrf_token'
    COOKIE_NAME = 'csrf_token'

    csrf_policy = aiohttp_csrf.policy.FormPolicy(FORM_FIELD_NAME)
    csrf_storage = aiohttp_csrf.storage.CookieStorage(COOKIE_NAME)

    aiohttp_csrf.setup(app, policy=csrf_policy, storage=csrf_storage)

    pass


if __name__ == '__main__':
    main()
