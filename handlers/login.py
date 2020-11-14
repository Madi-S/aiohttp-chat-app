from aiohttp_jinja2 import template
from aiohttp import web
from aiohttp_session import new_session, get_session

DATABASE = None


@template('login/login.html')
async def get_login(request):
    # IF USER EXISTS -> redirect him/her to chat -> raise web.HTTPFound('/chat')
    session = await new_session(request)
    if session.get('user'):
        raise web.HTTPFound('/chat')

    return {'content': 'Please enter login and password'}


@template('login/register.html')
async def get_register(request):
    return {}


async def post_login(request):
    router = request.app.router
    form = await request.post()
    user_signature = (form['name'], form['password'])

    # actually implement business logic to check credentials:
    try:
        user_id = DATABASE.index(user_signature)
        # Always use `new_session` during login to guard against
        # Session Fixation. See aiohttp-session#281
        session = await new_session(request)
        session['user_id'] = user_id
        return web.HTTPFound(router['restricted'].url_for())

    except ValueError:
        return web.Response(text='No such user', status=HTTPStatus.FORBIDDEN)


async def post_logout(request):
    pass


async def post_recover(request):
    # recover user password by its user recovery link in the database `pwd_reset_token`


async def post_register(request):
    # if user registered correctly, redirect him/her to chat


async def get_logout(request):
    pass
