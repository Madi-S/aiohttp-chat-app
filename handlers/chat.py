from aiohttp_jinja2 import template
from aiohttp import web
from aiohttp_session import new_session, get_session

from db import get_msgs


@template('chat/chat.html')
async def get_chat(request):
    session = await get_session(request)

    if not session.get('user_id'):
        print('Not allowing user to enter chat. Redirecting user to login page')
        raise web.HTTPFound('/register')

    print('Allowing user to enter chat')

    msgs = await get_msgs(request.app['pool'])
    print(msgs)
    return {'msgs': msgs}


async def post_send(request):
    form = await request.post()
    print(form, request, 'in post_send')

    return {'Content': 'Your message has been sent'}


async def handle_all(request):
    form = await request.post()
    print(form, 'in handle_all')

    raise web.HTTPFound('/chat')
