import aiomysql
import asyncio

from config import DB_HOST, DB_PORT, DB_USER, DB_PWD, DB_NAME

TABLE_USERS_NAME = 'chat_users'
INSERT_USER_COMMAND = 'INSERT INTO chat_users (username, pwd) VALUES (%s, %s)'
CHECK_USER_COMMAND = 'SELECT EXISTS (SELECT 1 FROM chat_users WHERE username = %s LIMIT 1)'
SATISFY_COMMAND = 'SELECT EXISTS (SELECT 1 FROM chat_users WHERE username = %s and pwd = %s LIMIT 1)'
DELETE_USER_COMMAND = 'DELETE FROM chat_users WHERE username = %s'


TABLE_MESSAGES_NAME = 'chat_messages'
INSERT_MSG_COMMAND = 'INSERT INTO chat_messages (username, msg, time_sent) VALUES (%s, %s, %s)'
GET_10_LAST_MSGS_COMMAND = 'SELECT * FROM (SELECT * FROM chat_messages ORDER BY id DESC LIMIT 10)Var1 ORDER BY id ASC'


TABLE_LIKES_NAME = 'messages_liked'
CHECK_USER_LIKED = 'SELECT * FROM messages_liked WHERE username = %s AND msg_id = %s'
LIKE_MSG_COMMAND = 'SELECT COUNT(like_id) FROM messages_liked WHERE msg_id = %s'


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


async def close_db(app):
    pool = app['pool']
    pool.close()
    await pool.wait_closed()
    print('closing db')


async def get_msgs(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(GET_10_LAST_MSGS_COMMAND)
            msgs = await cur.fetchall()

            return msgs


async def add_msg(pool, data):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(INSERT_MSG_COMMAND, data)
            await conn.commit()

            return True


async def like_msg(pool, msg_id, username):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(LIKE_MSG_COMMAND, msg_id)
            await conn.commit()

            return True


async def dislike_msg(pool, msg_id, username):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:


            return True


async def user_liked(pool, msg_id, username):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(CHECK_USER_LIKED, username, msg_id)
            liked = await cur.fetchone()
            print(bool(liked))

            return liked


async def user_checked(pool, data: tuple, register=True):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:

            # Add user to database
            if register:
                await cur.execute(CHECK_USER_COMMAND, (data['username'], ))
                user_exists = await cur.fetchone()

                # Check if user's login does not exist in database
                if not user_exists[0]:
                    await cur.execute(INSERT_USER_COMMAND, (data['username'], data['password']))
                    await conn.commit()

                    print(f'User {data} was addded to database')
                    return True

                print(
                    f'User {data["username"]} exists - NOT ADDED TO DATABASE')
                return False

            # Check user in database
            else:
                await cur.execute(SATISFY_COMMAND, (data['username'], data['password']))
                user_exists = await cur.fetchone()

                # Check if username/password pair exist and satisfy db
                if user_exists[0]:
                    print(f'User {data["username"]} exists in - SATISFIED DB')
                    return True

                print('Login/Password pair does not match or user does not exists')
                return False
