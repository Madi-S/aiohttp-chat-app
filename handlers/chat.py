from aiohttp_jinja2 import template
from aiohttp import web
from aiohttp_session import new_session, get_session


@template('chat/chat.html')
async def get_chat(request):
    session = await get_session(request)
    
    

    if not session.get('user_id'):
        print('Not allowing user to enter chat. Redirecting user to login page')
        raise web.HTTPFound('/register')

    print('Allowing user to enter chat')
    return {}


async def post_send(request):
    return {'Content': 'Your message has been sent'}


async def handle_all(request):
    raise web.HTTPFound('/chat')
