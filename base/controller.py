from collections import namedtuple
from inspect import isawaitable
from sanic.request import Request
from config import db_config
from aiohttp import client

try:
    import ujson as json
except:
    import json
setup = namedtuple('setup', ['identification', 'session', 'lang', 'db'])


class BaseHandler:

    setuper = setup(False, False, False, False)

    def __init__(self, req, env):
        self.request = req
        self.env = env
        self.data = None
        self.identification = None
        self.session = None
        self.trans = None
        self.trans_conn = None

    async def initialize(self):
        for item in self.setuper._fields:
            if item and hasattr(self, 'setup_'+item):
                result = getattr(self, 'setup_'+item)()
                if isawaitable(result):
                    await result

    async def __call__(self, *args, **kwargs):
        await self.initialize()
        result = self.handle(*args, **kwargs)
        if isawaitable(result):
            result = await result
        if self.session:
            await self.env.session_mgr.save(self.session)
        if self.trans_conn:
            await self.trans_conn.close()
        return result

    async def handle(self, *args, **kwargs):
        raise NotImplementedError

    async def transaction(self):
        if self.trans_conn:
            await self.trans_conn.close()
        self.trans_conn = await self.env.db.connection()
        self.trans = self.trans_conn.transaction()

    async def trans_start(self):
        if not self.trans:
            await self.transaction()

        await self.trans.start()

    async def trans_commit(self):
        if not self.trans:
            await self.transaction()

        await self.trans.commit()

    async def trans_rollback(self):
        if not self.trans:
            await self.transaction()

        await self.trans.rollback()


class MjsonHandler(BaseHandler):

    setuper = setup(True, True, True, True)

    def setup_identification(self):
        assert isinstance(self.request, Request)
        self.identification = self.request.json.get('identication', {})
        self.data = self.request.json.get('data', {})

    async def setup_session(self):
        sid = self.identification.get('session_id')
        if sid:
            self.session = await self.env.session_mgr.get(sid)
        else:
            self.session = self.env.session_mgr.new()

    def setup_lang(self):
        assert self.session
        lang = self.identification.get('language')
        if lang:
            if lang.find('zh') > -1:
                self.session.context['lang'] = 'zh_CN'
            elif lang.find('en') > -1:
                self.session.context['lang'] = 'en_US'

    async def setup_db(self):
        database = db_config.get('database')
        db_name = self.request.headers.get('X-Company-Code', '').lower()

        # 兼容config 里指定database 的模式，只有database 为空时才切换连接多数据库
        if (not database) and db_name:
            self.env.db.pool = await self.env.db.create_pool(database=db_name)


class JsonHandler(BaseHandler):

    async def initialize(self):
        await super(JsonHandler, self).initialize()
        self.data = json.loads(self.request.body)


class RedirectHandler(object):

    def __init__(self, req, env):
        self.request = req
        self.env = env
        self.data = None

    async def initialize(self):
        self.request = request

    async def __call__(self, *args, **kwargs):
        await self.initialize()
        result = self.handle(*args, **kwargs)
        if isawaitable(result):
            result = await result
        if self.session:
            await self.env.session_mgr.save(self.session)
        if self.trans_conn:
            await self.trans_conn.close()
        return result

    async def handle(self, *args, **kwargs):
        raise NotImplementedError

