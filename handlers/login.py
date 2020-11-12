from aiohttp_jinja2 import template
from aiohttp import web
from aiohttp_session import new_session, get_session


@template('login.html')
async def get_login(request):
    # IF USER EXISTS -> redirect him/her to chat -> raise web.HTTPFound('/chat')
    session = await new_session(request)
    if session.get('user'):
        raise web.HTTPFound('/chat')

    return {'content': 'Please enter login and password'}


@template('logout.html')
async def get_logout(request):
    pass


@template('register.html')
async def get_register(request):
    pass


async def post_login(request):
    pass


async def post_logout(request):
    pass


async def post_register(request):
    pass
