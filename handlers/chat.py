import time

from aiohttp_jinja2 import template
from aiohttp import web
from aiohttp_session import new_session, get_session

from db import get_msgs, add_msg, like_dislike_msg, get_likes_count

from datetime import datetime
from time import strftime


@template('chat/chat.html')
async def get_chat(request):
    session = await get_session(request)

    if not session.get('user_id'):
        print('Not allowing user to enter chat. Redirecting user to login page')
        raise web.HTTPFound('/register')

    print('Allowing user to enter chat')

    pool = request.app['pool']
    error = session.get('error')
    msgs = await get_msgs(pool)
    likes_count = await get_likes_count(pool, msgs)

    if 'error' in session:
        del session['error']

    return {'msgs': msgs, 'likes': likes_count, 'error': error}


async def post_chat(request):
    form = await request.post()
    session = await get_session(request)

    if 'error' in session:
        del session['error']

    if session.get('user_id'):

        # For both
        pool = request.app['pool']
        from_user = session.get('user_id')[0]

        # For post sending messages
        msg = form.get('message')

        # For post liking message
        msg_id = form.get('msg_id')
        like = form.get('like')

        # If it was post method to send a message
        if msg:
            user_waited = session.get('user_waited', 30)

            # If user waited 30 seconds before sending another message (by calculating difference of two times)
            if (time.time() - user_waited >= 30):
                if len(msg) <= 2000:
                    # Format message sent date
                    msg_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Add user's message to DB
                    await add_msg(pool, (from_user, msg, msg_date))

                    # Set user's last message time
                    session['user_waited'] = time.time()

                raise web.HTTPFound('/chat')

            # If user sends too much messages within a short period of time
            else:
                # Display user an error
                session['error'] = True
                print(f'User {session["user_id"][0]} sends too many messsages')
                raise web.HTTPFound('/chat')

        # If it was post method to like a message
        elif like and msg_id:
            result = await like_dislike_msg(pool, msg_id, from_user)
            print(result, 'in chat.py')

            raise web.HTTPFound('/chat')

        # If something weird happened
        else:
            raise web.HTTPFound('/chat')

    # If user was not logged in - redirect to the login page
    else:
        print(
            'User wants to send messsage withoug logging in. Redirecting to the login page')

        raise web.HTTPFound('/login')


async def handle_all(request):
    print('Redirecting user to /chat')

    raise web.HTTPFound('/chat')
