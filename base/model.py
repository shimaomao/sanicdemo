from .sql_db import PostgresDb
from aioredis import Redis
import asyncio
try:
    import ujson as json
except ImportError:
    import json


class BaseModel:

    def __init__(self, env):
        self.db = env.db
        self.env = env

REDIS_CACHE_NAME = 'redis_model_cache'



