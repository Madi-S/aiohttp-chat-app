import aiohttp_jinja2
import jinja2

import aioreloader

import aiohttp_csrf

from aiohttp import web
from aiohttp_session import setup as setup_session, get_session

from routes import setup_routes
from db import start_db, close_db

from py_settings import log, logger
from config import FORM_FIELD_NAME, COOKIE_NAME, SECRET_PHRASE, REDIS_ADDR, TMPL_FOLDER, STATIC_ROOT_URL, APP_PORT


@log
def main():
    app = web.Application()

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(TMPL_FOLDER))
    app['static_root_url'] = STATIC_ROOT_URL
    #app.router.add_static('/static', 'static', name='static')

    app.on_startup.append(start_db)
    app.on_cleanup.append(close_db)

    # Setup redis storage if redis server is on
    try:
        import asyncio
        import aioredis
        from aiohttp_session.redis_storage import RedisStorage

        async def make_redis_pool(app):
            return await aioredis.create_redis_pool(REDIS_ADDR, timeout=5)

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

    async def custom_async_error_handler(request):
        return web.Response(text='You silly bot, fuck off!', status=403)

    def setup_csrf_protection(app):
        csrf_policy = aiohttp_csrf.policy.FormPolicy(FORM_FIELD_NAME)
        csrf_storage = aiohttp_csrf.storage.CookieStorage(COOKIE_NAME)

        aiohttp_csrf.token_generator.HashedTokenGenerator(SECRET_PHRASE)

        aiohttp_csrf.setup(app, policy=csrf_policy, storage=csrf_storage,
                           error_renderer=custom_async_error_handler)

        # app.middlewares.append(aiohttp_csrf.csrf_middleware)

        # Using middlewares, all handlers will be protected
        # app.middlewares.append(aiohttp_csrf.csrf_middleware)

        # For mannual protection
        # @aiohttp_csrf.csrf_protect - pretection with csrf
        # @aiohttp_csrf.csrf_exempt - no protection with csrf

    setup_routes(app)
    logger.debug('Routes were setup')

    setup_session(app, storage)
    logger.debug('Storage was setup')

    setup_csrf_protection(app)
    logger.debug('csrf protection was setup')

    # aioreloader.start()
    logger.debug('Start with code reload')

    web.run_app(app, port=APP_PORT)


if __name__ == '__main__':
    main()
