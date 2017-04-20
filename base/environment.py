import asyncio
from asyncpg import pool, create_pool
from config import db_config, base_config
from base.sql_db import PostgresDb
from time import time
from base.web_utils import SessionManager
try:
    import uvloop as async_loop
except ImportError:
    async_loop = asyncio
try:
    import ujson as json
except ImportError:
    import json
import logging
from base.model import BaseModel


class Environment:
    """
    目前Environment为针对一个公司的共有参数,随程序启动加载,不随request进行初始化及消除
    """

    def __init__(self, loop=None, db_pool=None, redis_pool=None, redis_cache_pool=None):
        self.company_code = base_config.get('company_code', '')
        self.db = PostgresDb(db_pool=db_pool)
        self.redis_pool = redis_pool
        self.redis_cache_pool = redis_cache_pool
        self.lang = base_config.get('lang')
        self.currency_symbol = {}
        self.loop = loop

        # 兼容浦发项目，使能与 center 共用认证的 redis
        if not self.company_code:
            key_template = '{}'
        else:
            key_template = self.company_code + 'oe-session:{}'

        self.session_mgr = SessionManager(
            db_config.get('database'),
            self.redis_pool, key_template=key_template)

    async def get_currency_symbol(self, currency_id):
        symbol = self.currency_symbol.get(currency_id)
        if not symbol:
            data = await self.db.find('res_currency as rc', 'list', {
                'fields': ['rc.symbol'],
                'condition': 'rc.id = {}'.format(currency_id)
            })
            if not data:
                return None

            symbol = data[0]['symbol']
            self.currency_symbol[currency_id] = symbol

        return symbol

    async def get_hash_cache_info(self, table_name: str, identification, fields=None, exist_time=None):
        """
        author: PAN Yang
        对数据库表进行行级缓存, 采用在一个hash table内, 通过相应的值与过期时间命名方式,来取出代表时间的field, value 来判断对应的
        缓存数据field是否过期
        :param table_name:
        :param identification:
        :param fields:
        :param exist_time:
        :return:
        """
        # 参数检查
        if not identification or not isinstance(identification, int):
            return {}
        if fields:
            assert isinstance(fields, list)
        else:
            fields = []
        if exist_time:
            assert isinstance(exist_time, int)
        # redis key, fields命名
        str_key = 'environment_cache_' + self.company_code + '_' + str(table_name)
        str_id = str(identification)
        str_id_expire = str(identification) + 'expire_at'

        async with self.redis_pool.get() as conn:
            data = await conn.hget(str_key, str_id)
            # 过期日期
            expire_at = await conn.hget(str_key, str_id_expire)
            # 需要更新的字段
            uncovered_fields = []
            # 无期限或未过期的data
            if data and (not expire_at or (expire_at and float(expire_at) >= time())):
                data = json.loads(data)
                # 未过期时更新本次查询中不在缓存内的字段
                # [uncovered_fields.append(single) for single in fields if single not in data]
            else:
                # 过期清空缓存,全部重新查询写入缓存
                data = {}
                uncovered_fields = ['*']
            # 重新更新未在缓存内的字段
            if uncovered_fields:
                added_data = await self.db.find(str(table_name), 'list', {
                    'fields': uncovered_fields,
                    'condition': 'id={}'.format(int(identification))
                })
                # 如果有更新字段,重新写入redis缓存,并设置过期时间
                # TODO 可能存在的问题, 每次一次对一行数据中某个字段的更新,会重置整个行缓存的存在时间
                if added_data:
                    data.update(dict(added_data[0]))
                    update_dict = {str_id: json.dumps(data)}
                    if exist_time:
                        update_dict.update({str_id_expire: time() + exist_time})
                    await conn.hmset_dict(str_key, update_dict)
                    logging.warning('using db')
            # 如果查询单一字段,直接返回该字段的值
            if len(fields) == 1:
                data = data.get(fields[0])

            return data


def r_cache(key=None, identification=None, time=None, company_code=None):
    """
    异步缓存装饰器
    :param key:
    :param identification:
    :param time:
    :return:
    """

    def _deco(func):

        async def wrapper(*args, **kwargs):
            model = args[0]
            async with model.env.redis_pool.get() as conn:
                if company_code is None:
                    str_name = 'redis_model_cache_' + model.env.company_code + '_'
                else:
                    str_name = 'redis_model_cache_' + company_code + '_'
                if key and isinstance(model, BaseModel):
                    str_name += str(key)
                    if id and isinstance(identification, int):
                        str_name += str(args[identification])
                    elif isinstance(identification, list):
                        for item in identification:
                            str_name += str(args[item])
                    cache = await conn.get(str_name)
                    if cache:
                        ret = json.loads(cache)
                        return trans_redis_type(ret)
                ret = await (func(*args, **kwargs))
                cache = json.dumps(ret)
                if str_name:
                    await conn.set(str_name, cache)
                if isinstance(time, int):
                    conn.expire(str_name, time)
                return ret

        return wrapper

    return _deco


def trans_redis_type(data):
    new_data = {}
    if isinstance(data, dict):
        for k, v in data.items():
            if v == b'null':
                v = None

            new_data[k] = v
        data = new_data
    elif isinstance(data, bytes) and data == b'null':
        data = None

    return data


def format_num(self):
    # TODO 根据设置进行格式化比如千分位设置
    pass

