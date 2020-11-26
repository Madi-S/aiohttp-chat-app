import aiomysql
import asyncio

from config import DB_HOST, DB_PORT, DB_USER, DB_PWD, DB_NAME

# Queries to manipulate over chat_users (info about user) table
TABLE_USERS_NAME = 'chat_users'
INSERT_USER_COMMAND = 'INSERT INTO chat_users (username, pwd) VALUES (%s, %s)'
CHECK_USER_COMMAND = 'SELECT EXISTS (SELECT 1 FROM chat_users WHERE username = %s LIMIT 1)'
SATISFY_COMMAND = 'SELECT EXISTS (SELECT 1 FROM chat_users WHERE username = %s and pwd = %s LIMIT 1)'
DELETE_USER_COMMAND = 'DELETE FROM chat_users WHERE username = %s'


# Queries to manipulate over chat_message (info about every message) table
TABLE_MESSAGES_NAME = 'chat_messages'
INSERT_MSG_COMMAND = 'INSERT INTO chat_messages (username, msg, time_sent) VALUES (%s, %s, %s)'
GET_10_LAST_MSGS_COMMAND = 'SELECT * FROM (SELECT * FROM chat_messages ORDER BY msg_id DESC LIMIT 10)Var1 ORDER BY msg_id ASC'


# Queries to like/dislike messages (stores info about every liked message)
TABLE_LIKES_NAME = 'messages_liked'
CHECK_USER_LIKED_COMMAND = 'SELECT * FROM messages_liked WHERE username = %s AND msg_id = %s'
LIKE_MSG_COMMAND = 'INSERT INTO messages_liked (username, msg_id) VALUES (%s, %s)'
DISLIKE_MSG_COMMAND = 'DELETE FROM messages_liked WHERE username = %s and msg_id = %s'
GET_LIKES_COUNT_COMMAND = 'SELECT COUNT(msg_id) FROM messages_liked WHERE msg_id = %s'


# Start db and add `db_pool` to the app, so it can be accessible anytime
async def start_db(app):
    loop = asyncio.get_event_loop()
    db_pool = await aiomysql.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PWD,
        db=DB_NAME,
        loop=loop,
    )

    app['pool'] = db_pool


# Method to gracefully shut down MySQL db (added to app's cleanup)
async def close_db(app):
    pool = app['pool']
    pool.close()
    await pool.wait_closed()
    print('Closing DB')


# Method to get 10 last messages
async def get_msgs(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(GET_10_LAST_MSGS_COMMAND)
            msgs = await cur.fetchall()

            return msgs


# Method to store message in the db
async def add_msg(pool, from_user, msg_text, msg_date):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(INSERT_MSG_COMMAND, (from_user, msg_text, msg_date))
            await conn.commit()

            return 'Message added'


# Method to get likes count on given messages
async def get_likes_count(pool, msgs):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            likes = []
            for msg in msgs:
                await cur.execute(GET_LIKES_COUNT_COMMAND, (msg[0], ))
                likes.append(await cur.fetchone())

            return likes


# Method to like or cancel a like
async def like_dislike_msg(pool, msg_id, username):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(CHECK_USER_LIKED_COMMAND, (username, msg_id))
            user_liked = await cur.fetchone()

            # If user did not already liked the message
            if not user_liked:
                await cur.execute(LIKE_MSG_COMMAND, (username, msg_id))
                await conn.commit()
                return 'Liked'

            # Otherwise cancel his/her like - delete the row
            await cur.execute(DISLIKE_MSG_COMMAND, (username, msg_id))
            await conn.commit()
            return 'Disliked'


# Method to check if user exists/register user/check password&login pair
async def user_checked(pool, username, pwd, register=True):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:

            # Add user to database
            if register:
                await cur.execute(CHECK_USER_COMMAND, (username, ))
                user_exists = await cur.fetchone()

                # Check if user's login does not exist in database
                if not user_exists[0]:
                    await cur.execute(INSERT_USER_COMMAND, (username, pwd))
                    await conn.commit()

                    print(f'User {username} was addded to database')
                    return True

                print(
                    f'User {username} exists - NOT ADDED TO DATABASE')
                return False

            # Check user in database
            else:
                await cur.execute(SATISFY_COMMAND, (username, pwd))
                user_exists = await cur.fetchone()

                # Check if username/password pair exist and satisfy db
                if user_exists[0]:
                    print(f'User {username} exists in - SATISFIED DB')
                    return True

                print('Login/Password pair does not match or user does not exists')
                return False
