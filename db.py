import aiomysql
import asyncio

TABLE_NAME = 'chat_users'
INSERT_COMMAND = 'INSERT INTO chat_users (username, pwd) VALUES (%s, %s);'
CHECK_COMMAND = 'SELECT EXISTS (SELECT 1 FROM chat_users WHERE username = %s LIMIT 1);'
SATISFY_COMMAND = 'SELECT EXISTS (SELECT 1 FROM chat_users WHERE username = %s and pwd = %s LIMIT 1);'
DELETE_USER_COMMAND = 'DELETE FROM chat_users WHERE username = %s;'


async def start_db(app):
    loop = asyncio.get_event_loop()
    db_pool = await aiomysql.create_pool(
        host='localhost',
        port=3306,
        user='root',
        password='1234',
        db='webchat',
        loop=loop,
    )

    app['pool'] = db_pool


async def close_db(app):
    pool = app['pool']
    pool.close()
    await pool.wait_closed()
    print('closing db')




async def user_checked(pool, data: tuple, register=True):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:

            # Add user to database
            if register:
                await cur.execute(CHECK_COMMAND, (data['username'], ))
                user_exists = await cur.fetchone()

                # Check if user's login does not exist in database
                if not user_exists[0]:
                    await cur.execute(INSERT_COMMAND, (data['username'], data['password']))
                    await conn.commit()

                    print(f'User {data} was addded to database')
                    return True

                print(f'User {data["username"]} exists - NOT ADDED TO DATABASE')
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