from hashlib import sha1
import os
from time import time
from random import random
from aioredis import Redis
from aioredis.pool import RedisPool
import asyncio
import re
from aiohttp import request
import logging
try:
    import ujson as json
except ImportError:
    import json

_sha1_re = re.compile(r'^[a-f0-9]{40}$')


class Session(dict):

    def __init__(self, sid, db, data=None):
        self.id = sid
        self.db = db
        self.uid = None
        self.context = {}
        if data:
            super(Session, self).__init__(data)

    def __getattr__(self, attr):
        return self.get(attr, None)

    def __setattr__(self, k, v):
        try:
            object.__getattribute__(self, k)
        except:
            return self.__setitem__(k, v)
        object.__setattr__(self, k, v)

    def get_context(self, uid):

        pass


class SessionManager(object):

    def __init__(self, db, redis_pool, company_code=None,
                 key_template='oe-session:{}', timeout=60 * 60 * 24,
                 session_class=Session):
        self.redis_pool = redis_pool
        self.db = db
        self.key_template = key_template
        self.timeout = timeout
        self.company_code = company_code or ''
        self.session_class = session_class
        self.access_timestamp = time()

    @staticmethod
    def _urandom():
        if hasattr(os, 'urandom'):
            return os.urandom(30)
        return str(random()).encode('ascii')

    @staticmethod
    def generate_key(salt=None):
        if salt is None:
            salt = repr(salt).encode('ascii')
        return sha1(b''.join([
            salt,
            str(time()).encode('ascii'),
            SessionManager._urandom()
        ])).hexdigest()

    def is_valid_key(self, key):
        """Check if a key has the correct format."""
        return _sha1_re.match(key) is not None

    def get_session_key(self, sid):
        if isinstance(sid, str):
            sid = sid
        return self.key_template.format(sid)

    async def get(self, sid):
        if not self.is_valid_key(sid):
            return self.new()
        key = self.company_code + self.get_session_key(sid)
        async with self.redis_pool.get() as conn:
            saved = await conn.hgetall(key)
            if saved:
                data = {}
                for k, v in saved.items():
                    data[k.decode()] = int(v) if v.isdigit() else v.decode()
                await conn.expire(key, self.timeout)
                if isinstance(saved, dict) and 'context' in data:
                    data['context'] = json.loads(data['context'])
                return self.session_class(sid, self.db, data=data)
            else:
                return self.new()

    def new(self):
        return self.session_class(self.generate_key(), self.db)

    async def delete(self, sid):
        key = self.get_session_key(sid)
        async with self.redis_pool.get() as conn:
            return conn.delete(key)

    async def save(self, session):
        key = self.get_session_key(session.id)
        session.access_timestamp = time()
        session = dict(session)
        for k, v in session.items():
            if not isinstance(v, (str, int, float)):
                session[k] = json.dumps(v)
        async with self.redis_pool.get() as conn:
            logging.info('save session {}'.format(session))
            if conn.hmset_dict(key, session):
                return conn.expire(key, self.timeout)


