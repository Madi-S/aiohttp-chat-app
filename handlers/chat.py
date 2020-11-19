from aiohttp_jinja2 import template
from aiohttp import web
from aiohttp_session import new_session, get_session

from db import get_msgs, add_msg

from datetime import datetime
from time import strftime


@template('chat/chat.html')
async def get_chat(request):
    session = await get_session(request)

    if 'error' in session:
        del session['error'] 

    if not session.get('user_id'):
        print('Not allowing user to enter chat. Redirecting user to login page')
        raise web.HTTPFound('/register')

    print('Allowing user to enter chat')

    msgs = await get_msgs(request.app['pool'])
    return {'msgs': msgs}


async def post_send(request):
    form = await request.post()
    session = await get_session(request)

    if 'error' in session:
        del session['error'] 

    if session.get('user_id', None):

        msg = form.get('message', 'None')
        if len(msg) <= 2000:
            from_user = session.get('user_id')[0]
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            await add_msg(request.app['pool'], (from_user, msg, time))

        raise web.HTTPFound('/chat')

    else:
        print(
            'User wants to send messsage withoug logging in. Redirecting to the login page')

        raise web.HTTPFound('/login')


async def handle_all(request):
    print('Redirecting user to /chat')

    raise web.HTTPFound('/chat')
