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


'''

['ATTRS', 'POST_METHODS',
    '_abc_impl', '_cache', '_client_max_size', '_content_dict', '_content_type', '_headers', '_http_date', '_is_protocol',
     '_loop', '_match_info', '_message', '_method', '_parse_content_type', '_payload', '_payload_writer', '_post', '_prepare_hook',
      '_protocol', '_read_bytes', '_rel_url', '_state', '_stored_content_type', '_task', '_transport_peername', '_transport_sslcontext', 
      '_version', 'app', 'body_exists', 'can_read_body', 'charset', 'clear', 'clone', 'config_dict', 'content', 'content_length',
       'content_type', 'cookies', 'forwarded', 'get', 'has_body', 'headers', 'host', 'http_range', 'if_modified_since',
        'if_range', 'if_unmodified_since', 'items', 'json', 'keep_alive', 'keys', 'loop', 'match_info', 'message', 'method',
         'multipart', 'path', 'path_qs', 'pop', 'popitem', 'post', 'protocol', 'query', 'query_string', 'raw_headers', 
         'raw_path', 'read', 'rel_url', 'release', 'remote', 'scheme', 'secure', 'setdefault', 'task', 'text', 'transport',
          'update', 'url', 'values', 'version', 'writer']
'''


@log
@csrf_protect
@template('login/login.html')
async def get_login(request):
    token = await generate_token(request)
    session = await get_session(request)

    error = session.get('error')
    if 'error' in session:
        del session['error']

    return {'field_name': FORM_FIELD_NAME, 'token': token, 'error': error}


@log
@csrf_protect
@template('login/register.html')
async def get_register(request):
    token = await generate_token(request)
    session = await get_session(request)

    error = session.get('error')
    if 'error' in session:
        del session['error']

    return {'field_name': FORM_FIELD_NAME, 'token': token, 'error': error}


@log
@csrf_protect
async def post_login(request):
    # If user's inputs are satisfying DB -> redirect to chat
    # If user's inputs are NOT satisfying DB -> return bad response
    form = await request.post()
    session = await get_session(request)

    if 'error' in session:
        del session['error']

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

        session['error'] = True
        return web.HTTPFound('/register')

    # Request came from login page
    else:

        # Check user's presence in db
        if await user_checked(pool, data, register=False):
            print(f'User {form["username"]} has been passed login section')
            session['user_id'] = (form['username'], form['password'])
            raise web.HTTPFound('/chat')

        # If login & password pair do not match or user with such login does not exist
        session['error'] = True
        return web.HTTPFound('/login')


@log
async def post_logout(request):
    session = await get_session(request)
    print(f'User {session["user_id"]} has been deleted from session storage')
    del session['user_id']
    del session['remember_me']
    if 'error' in session:
        del session['error']

    raise web.HTTPFound('/login', text='Successful logout')


@log
async def get_logout(request):
    raise web.HTTPFound('/login', text='Login first')


@log
async def post_recover(request):
    # recover user password by its user recovery link in the database `pwd_reset_token`
    pass
