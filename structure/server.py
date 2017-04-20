from base.application import Application
from asyncpg import create_pool
import asyncio
from structure.config import db_config, server_config, redis_config
from base.environment import Environment
from aioredis import create_pool as create_redis_pool
from structure.route import route, err_route, middleware
try:
    import ujson as json
except ImportError:
    import json

try:
    import uvloop as async_loop
except ImportError:
    async_loop = asyncio


loop = async_loop.new_event_loop()
asyncio.set_event_loop(loop=loop)
env = None

async def init_db(*args):
    application = args[0]
    loop = args[1]
    db_host = db_config.get('host', '127.0.0.1')
    database = db_config.get('database')
    db_user = db_config.get('user')
    db_pwd = db_config.get('password')
    db_pool = await create_pool(max_size=50, host=db_host, database=database, user=db_user, password=db_pwd, loop=loop)
    redis_host = redis_config['redis'].get('host')
    redis_port = redis_config['redis'].get('port')
    redis_db = redis_config['redis'].get('db')
    redis_pool = await create_redis_pool((redis_host, redis_port), db=redis_db, loop=loop)
    redis_cache_host = redis_config['redis_cache'].get('host')
    redis_cache_port = redis_config['redis_cache'].get('port')
    redis_cache_db = redis_config['redis_cache'].get('db')
    redis_cache_pool = await create_redis_pool((redis_cache_host, redis_cache_port), db=redis_cache_db, loop=loop)

    application.env = Environment(loop=loop, db_pool=db_pool, redis_pool=redis_pool, redis_cache_pool=redis_cache_pool)


app = Application(route, err_route, middleware, env)


host = server_config.get('host')
port = server_config.get('port')
app.run(host=host, port=port, after_start=init_db, debug=False)