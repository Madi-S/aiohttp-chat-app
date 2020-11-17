import aiohttp_jinja2
import jinja2

import aioreloader

from aiohttp import web
from aiohttp_session import setup as setup_session, get_session

from routes import setup_routes
from db import start_db, close_db

from py_settings import log, logger
from redis_storage import setup_redis_storage, close_redis
from web_csrf import setup_csrf


@log
def main():
    app = web.Application()

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    app['static_root_url'] = '/static'
    app.router.add_static('/static', 'static', name='static')

    app.on_startup.append(start_db)
    app.on_cleanup.append(close_db)

    try:
        storage = setup_redis_storage(app)
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

    setup_session(app, storage)
    logger.debug('Storage was setup')

    setup_csrf(app, storage)
    logger.debug('csrf protection was setup')

    aioreloader.start()
    logger.debug('Start with code reload')

    web.run_app(app, port=8000)


if __name__ == '__main__':
    main()
