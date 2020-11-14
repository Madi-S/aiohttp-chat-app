import aiomysql
import asyncio

TABLE_NAME = 'chat_users'
INSERT_COMMAND = 'INSERT INTO %s (username, pwd) VALUES (%s, %s)'
CHECK_COMMAND = 'SELECT EXISTS (SELECT 1 FROM %s WHERE username = %s LIMIT 1)'
DELETE_USER_COMMAND = 'DELETE FROM %s WHERE username = %s'


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


async def user_added(pool, data: tuple):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:

            await cur.execute(CHECK_COMMAND, data[0])
            exists = await cur.fetchone()

            if not exists:
                await cur.execute(INSERT_COMMAND, data)
                print(f'User {data} was addded to database')

            else:
                print(f'User {data} was NOT added to database')
                return False

