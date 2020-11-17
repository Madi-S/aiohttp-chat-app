import aiohttp_csrf

from aiohttp import web

FORM_FIELD_NAME = '_csrf_token'
COOKIE_NAME = 'csrf_token'


def setup_csrf(app, storage):
    csrf_policy = aiohttp_csrf.policy.FormPolicy(FORM_FIELD_NAME)
    csrf_storage = aiohttp_csrf.storage.SessionStorage(storage)

    aiohttp_csrf.token_generator.HashedTokenGenerator

    aiohttp_csrf.setup(app, policy=csrf_policy, storage=csrf_storage)
    app.middlewares.append(aiohttp_csrf.csrf_middleware)


async def generate_csrf_token(request):
    return await aiohttp_csrf.generate_token(request)


# @aiohttp_csrf.csrf_protect - pretection with csrf
# @aiohttp_csrf.csrf_exempt - no protection with csrf


async def custom_async_error_handler(request):
    return web.Response(text='You silly bot, fuck off!', status=403)
