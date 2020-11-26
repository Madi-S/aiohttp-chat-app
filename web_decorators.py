from aiohttp_session import get_session
from aiohttp import web


# Decorator to automatically check if any errors must be displayed and the delete them:
def check_del_error(f):
    async def inner(request, *args, **kwargs):
        session = await get_session(request)
        error = session.get('error')
        if 'error' in session:
            del session['error']
            print('Error was deleted')
        if 'get' in f.__name__:
            return await f(request, error, *args, **kwargs)
        else:
            return await f(request, *args, **kwargs)

    return inner


# Decorator to check user's cookies (if he/she already loginned) to straightly redirect him to the /chat page
def check_cookies(f):
    async def inner(request, *args, **kwargs):
        session = await get_session(request)
        if session.get('user_id') and session.get('remember_me'):
            print('Redirecting user straight to the chat: saved cookies and remember me')
            raise web.HTTPFound('/chat')
        return await f(request, *args, **kwargs)

    return inner
