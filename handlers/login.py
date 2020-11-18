from aiohttp import web

from aiohttp_jinja2 import template
from aiohttp_session import new_session, get_session
from aiohttp_csrf import csrf_protect, generate_token

from db import user_checked
from py_settings import log, logger

from config import FORM_FIELD_NAME


# def login_required(f):
#    async def wrapped(request, *args, **kwargs):
#        app = request.app
#        router = app.router
#
#        session = await get_session(request)
#
#        if 'user_id' not in session:
#            return web.HTTPFound(router['login'].url_for())
#
#        user_id = session['user_id']
#        # actually load user from your database (e.g. with aiopg)
#        # user = DATABASE[user_id]
#        app['user'] = user
#        return await f(request, *args, **kwargs)
#
#    return wrapped

@log
def check_cookies(f):
    async def inner(request, *args, **kwargs):
        session = await new_session(request)

        if session.get('user_id') and session.get('remember_me'):
            print(
                'Redirecting user straight to the chat because of saved cookies and remember me checkbox')
            raise web.HTTPFound('/chat')

        return await f(request, *args, **kwargs)

    return inner


@log
@csrf_protect
@template('login/login.html')
async def get_login(request):
    token = await generate_token(request)

    return {'field_name': FORM_FIELD_NAME, 'token': token}


@log
@csrf_protect
@template('login/register.html')
async def get_register(request):
    token = await generate_token(request)

    return {'field_name': FORM_FIELD_NAME, 'token': token}


@log
@csrf_protect
async def post_login(request):
    # If user's inputs are satisfying DB -> redirect to chat
    # If user's inputs are NOT satisfying DB -> return bad response
    form = await request.post()
    session = await get_session(request)

    pool = request.app['pool']
    data = form

    # If user wants to be logged-in automatically
    if form.get('remember', None):
        session['remember_me'] = True
        print('User WANTS to save his cookies')

    else:
        session['remember_me'] = False
        print('User does NOT want to be logged-in automatically')

    # Request came from registration page
    if form.get('password-repeat'):

        # Check if username's absence in db:
        if await user_checked(pool, data):
            print(f'User {form["username"]} has been added to database')
            session['user_id'] = (form['username'], form['password'])
            raise web.HTTPFound('/chat')

        return web.HTTPFound('/register', text=f'User {form["username"]} already exists',)

    # Request came from login page
    else:

        # Check user's presence in db
        if await user_checked(pool, data, register=False):
            print(f'User {form["username"]} has been passed login section')
            session['user_id'] = (form['username'], form['password'])
            raise web.HTTPFound('/chat')

        return web.HTTPFound('/login', text=f'Username/Password pair does not match, or username {form["username"]} does not exist')


@log
async def post_logout(request):
    session = await get_session(request)
    print(f'User {session["user_id"]} has been deleted from session storage')
    del session['user_id']
    del session['remember_me']

    raise web.HTTPFound('/login', text='Successful logout')


@log
async def get_logout(request):
    raise web.HTTPFound('/login', text='Login first')


@log
async def post_recover(request):
    # recover user password by its user recovery link in the database `pwd_reset_token`
    pass
