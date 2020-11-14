from aiohttp_jinja2 import template
from aiohttp import web
from aiohttp_session import new_session, get_session
from http import HTTPStatus

from db import user_checked

DATABASE = None


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


def check_cookies(f):
    async def inner(request, *args, **kwargs):
        session = await new_session(request)

        if session.get('user_id') and session.get('remember_me'):
            print(
                'Redirecting user straight to the chat because of saved cookies and remember me checkbox')
            raise web.HTTPFound('/chat')

        return await f(request, *args, **kwargs)

    return inner


@template('login/login.html')
async def get_login(request):
    return {'content': 'Please enter login and password'}


@template('login/register.html')
async def get_register(request):
    return {}


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

        return web.Response(text=f'User {form["username"]} already exists', status=HTTPStatus.FORBIDDEN)

    # Request came from login page
    else:

        # Check user's presence in db
        if await user_checked(pool, data, register=False):
            print(f'User {form["username"]} has been passed login section')
            session['user_id'] = (form['username'], form['password'])
            raise web.HTTPFound('/chat')

        return web.Response(text=f'Username/Password pair does not match, or username {form["username"]} does not exist', status=HTTPStatus.FORBIDDEN)


'''
['ATTRS', 'POST_METHODS', '_MutableMapping__marker', '__abstractmethods__', '__bool__', '__class__', '__class_getitem__',
 '__contains__', '__delattr__', '__delitem__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__',
  '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__module__',
   '__ne__', '__new__', '__orig_bases__', '__parameters__', '__reduce__', '__reduce_ex__', '__repr__', '__reversed__', '__setattr__',
    '__setitem__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '__weakref__', '_abc_impl', '_cache', '_client_max_size',
  '_content_dict', '_content_type', '_headers', '_http_date', '_is_protocol', '_loop', '_match_info', '_message', '_method',
   '_parse_content_type', '_payload', '_payload_writer', '_post', '_prepare_hook', '_protocol', '_read_bytes', '_rel_url', '_state',
   '_stored_content_type', '_task', '_transport_peername', '_transport_sslcontext', '_version', 'app', 'body_exists', 'can_read_body',
    'charset', 'clear', 'clone', 'config_dict', 'content', 'content_length', 'content_type', 'cookies', 'forwarded', 'get', 'has_body',
    'headers', 'host', 'http_range', 'if_modified_since', 'if_range', 'if_unmodified_since', 'items', 'json', 'keep_alive', 'keys', 'loop',
     'match_info', 'message', 'method', 'multipart', 'path', 'path_qs', 'pop', 'popitem', 'post', 'protocol', 'query', 'query_string',
     'raw_headers', 'raw_path', 'read', 'rel_url', 'release', 'remote', 'scheme', 'secure', 'setdefault', 'task', 'text', 'transport',
     'update', 'url', 'values', 'version', 'writer']
'''

#router = request.app.router
# form = await request.post()
#user_signature = (form['name'], form['password'])

# actually implement business logic to check credentials:
# try:
#    user_id = DATABASE.index(user_signature)
#    # Always use `new_session` during login to guard against
#    # Session Fixation. See aiohttp-session#281
#    session = await new_session(request)
#    session['user_id'] = user_id
#    return web.HTTPFound(router['restricted'].url_for())

# except ValueError:
#    return web.Response(text='No such user', status=HTTPStatus.FORBIDDEN)


async def post_logout(request):
    session = await new_session(request)
    session.flush()


async def post_recover(request):
    # recover user password by its user recovery link in the database `pwd_reset_token`
    pass


async def get_logout(request):
    pass
