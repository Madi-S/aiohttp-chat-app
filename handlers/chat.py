from aiohttp_jinja2 import template
from aiohttp import web
from aiohttp_session import new_session, get_session


def check_cookies(f):
    async def inner(request, *args, **kwargs):
        session = await new_session(request)

        if session.get('user_id') and session.get('remember_me'):
            print('Allowing user not to login')
            raise web.HTTPFound('/chat')

        return await f(request, *args, **kwargs)

    return inner


@check_cookies
@template('chat/chat.html')
async def get_chat(request):
    session = await new_session(request)

    if session.get('user_id') and session.get('remember_me'):
        print('Allowing user not to login')
        raise web.HTTPFound('/chat')

    else:
        raise web.HTTPFound('/register')


async def post_send(request):
    pass


async def handle_all(request):
    raise web.HTTPFound('/chat')
