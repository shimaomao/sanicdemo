import asyncio
from asyncpg import create_pool
try:
    import uvloop as async_loop
except ImportError:
    async_loop = asyncio

from config import db_config
from script.create_data import create_data

async def create_db_pool():
    db_host = db_config.get('host', '127.0.0.1')
    database = db_config.get('database')
    db_user = db_config.get('user')
    db_pool = await create_pool(host=db_host, database=database, user=db_user)
    return db_pool


async def _execute(pool, str_sql):
    async with pool.acquire() as conn:
        data = await conn.execute(str_sql)
        return data


async def create_table(pool):
    async with pool.acquire() as conn:

        await conn.execute('DROP TABLE if EXISTS MARKET_SALARY_DATA')
        await conn.execute('DROP TABLE if EXISTS JOB')
        await conn.execute('DROP TABLE if EXISTS JOB_GRADE')
        await conn.execute('DROP TABLE if EXISTS INDUSTRY')
        await conn.execute('DROP TABLE if EXISTS JOB_CATEGORY')
        #await conn.execute('DROP TABLE if EXISTS CITY')
        #await conn.execute('DROP TABLE if EXISTS COMPANY_SCOPE')
        #await conn.execute('DROP TABLE if EXISTS COMPANY_NATURE')

        # ------------ CITY --------------------------
        # await conn.execute('CREATE TABLE CITY ('
        #                    'ID  SERIAL PRIMARY KEY,'
        #                    'CODE INT UNIQUE ,'
        #                    'NAME_ZH VARCHAR,'
        #                    'NAME_EN VARCHAR)')

        # ------------ CATEGORY ----------------------

        await conn.execute('CREATE TABLE JOB_CATEGORY ('
                           'ID  SERIAL PRIMARY KEY,'
                           'CODE INT UNIQUE ,'
                           'NAME_ZH VARCHAR,'
                           'NAME_EN VARCHAR)')

        # ------------ GRADE ----------------------

        await conn.execute('CREATE TABLE JOB_GRADE ('
                           'ID  SERIAL PRIMARY KEY,'
                           'CODE INT UNIQUE ,'
                           'NAME_ZH VARCHAR,'
                           'NAME_EN VARCHAR)')

        # ------------ JOB ---------------------------

        await conn.execute('CREATE TABLE JOB ('
                           'ID  SERIAL PRIMARY KEY,'
                           'CODE INT UNIQUE ,'
                           'NAME_ZH VARCHAR,'
                           'NAME_EN VARCHAR,'
                           'JOB_GRADE_CODE INT REFERENCES JOB_GRADE(CODE),'
                           'JOB_CATEGORY_CODE INT REFERENCES JOB_CATEGORY(CODE))')

        # ------------INDUSTRY --------------------------
        await conn.execute('CREATE TABLE INDUSTRY ('
                           'ID  SERIAL PRIMARY KEY,'
                           'CODE INT UNIQUE,'
                           'NAME_ZH VARCHAR,'
                           'NAME_EN VARCHAR)')

        # # ------------nature --------------------------
        # await conn.execute('CREATE TABLE COMPANY_NATURE ('
        #                    'ID  SERIAL PRIMARY KEY,'
        #                    'CODE INT UNIQUE,'
        #                    'DESCRIPTION VARCHAR)')
        #
        # # ------------nature --------------------------
        # await conn.execute('CREATE TABLE COMPANY_SCOPE ('
        #                    'ID  SERIAL PRIMARY KEY,'
        #                    'CODE INT UNIQUE,'
        #                    'MIN_NUM INT ,'
        #                    'MAX_INT INT )')

        # ------------- main table -------------------
        await conn.execute('CREATE TABLE MARKET_SALARY_DATA('
                           'ID  SERIAL PRIMARY KEY,'
                           'SOURCE VARCHAR,'
                           'CITY_CODE INT REFERENCES  CITY(CODE),'
                           'JOB_CODE INT REFERENCES JOB(CODE),'
                           'INDUSTRY_CODE INT  REFERENCES INDUSTRY(CODE),'
                           'SCOPE_CODE INT REFERENCES COMPANY_SCOPE(CODE),'
                           'NATURE_CODE INT REFERENCES COMPANY_NATURE(CODE),'
                           'BASE_SALARY NUMERIC (11,3),'
                           'FIX_SALARY NUMERIC(11,3),'
                           'TOTAL_SALARY NUMERIC (11,3))')


if __name__ == '__main__':
    loop = async_loop.new_event_loop()
    asyncio.set_event_loop(loop=loop)
    pool = loop.run_until_complete(create_db_pool())
    loop.run_until_complete(create_table(pool))
    loop.run_until_complete(create_data(pool))
