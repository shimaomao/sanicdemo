from base.application import Application
from asyncpg import create_pool
import asyncio
from config import db_config, server_config, redis_config
from base.environment import Environment
from aioredis import create_pool as create_redis_pool
from route import route, err_route, middleware
import sys
import os
ddd
    redis_host = redis_config['redis'].get('host')
    redis_port = redis_config['redis'].get('port')
    redis_db = redis_config['redis'].get('db')
    redis_pool = await create_redis_pool((redis_host, redis_port), db=redis_db, loop=loop)
    redis_cache_host = redis_config['redis_cache'].get('host')
    redis_cache_port = redis_config['redis_cache'].get('port')
    redis_cache_db = redis_config['redis_cache'].get('db')
    redis_cache_pool = await create_redis_pool((redis_cache_host, redis_cache_port), db=redis_cache_db, loop=loop)
    global env
    env = Environment(loop=loop, db_pool=db_pool, redis_pool=redis_pool, redis_cache_pool=redis_cache_pool)


loop.run_until_complete(init_db())



app = Application(route, err_route, middleware, env)


host = server_config.get('host')
port = server_config.get('port')
app.run(host=host, port=port, loop=loop, debug=False)