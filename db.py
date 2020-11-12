import aiomysql
import asyncio


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

    conn = await db_pool.acquire()
    cur = await conn.cursor()

    app['db'] = conn
    app['cur'] = cur


async def close_db(app):
    await app['db'].close()


