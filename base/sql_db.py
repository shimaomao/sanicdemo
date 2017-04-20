import asyncio
from asyncpg import pool, create_pool
from config import db_config, base_config


class PostgresDb:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance') or not cls._instance:
            kwargs = {}
            cls._instance = super(PostgresDb, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self, db_pool=None):
        if not db_pool:
            loop = asyncio.get_event_loop()
            loop.stop()
            loop.run_until_complete()
        self.dicConfig = {}
        self.pool = db_pool

    async def create_pool(self, host=None, database=None, user=None,
                          password=None):
        if self.pool and self.pool._connect_kwargs['database'] == database:
            return self.pool

        db_host = db_config.get('host', '127.0.0.1') if not host else host
        database = db_config.get('database') if not database else database
        db_user = db_config.get('user') if not user else user
        db_pwd = db_config.get('password') if not password else password

        # !!! 不同的公司会切换db，使用数据库服务端连接池, 注意客户端连接池数量
        db_pool = await create_pool(min_size=2, host=db_host,
                                    database=database,
                                    user=db_user, password=db_pwd)
        return db_pool

    async def connection(self):
        conn = await self.pool.acquire()
        return conn

    async def _execute(self, str_sql, connection=None):
        if not connection:
            async with self.pool.acquire() as conn:
                data = await conn.execute(str_sql)
        else:
            data = await connection.execute(str_sql)
        return data

    async def _fetch(self, str_sql, connection=None):
        if not connection:
            async with self.pool.acquire() as conn:
                data = await conn.fetch(str_sql)
        else:
            data = await connection.fetch(str_sql)
        return data

    async def _fetchval(self, str_sql, connection=None):
        if not connection:
            async with self.pool.acquire() as conn:
                data = await conn.fetchval(str_sql)
        else:
            data = await connection.fetchval(str_sql)
        return data

    async def _fetchrow(self, str_sql, connection=None):
        if not connection:
            async with self.pool.acquire() as conn:
                data = await conn.fetchrow(str_sql)
        else:
            data = await connection.fetchrow(str_sql)
        return data

    async def find(self, str_table_name, str_type, dic_data, boo_format_data=True, connection=None):
        """ 读取一组数据

        @params str_table_name string 表名
        @params str_type string 类型，可以是list, first
        @prams dic_data dict 数据字典
        @params boo_format_data bool 是否格式化数据，默认为True
        """

        if boo_format_data:
            dic_data = self.formatData(dic_data)

        str_table_name = self.build_table_name(str_table_name)
        str_fields = self.build_fields(dic_data['fields'])
        str_condition = self.build_condition(dic_data['condition'])
        str_join = self.build_join(dic_data['join'])
        str_limit = self.build_limit(dic_data['limit'])
        str_group = self.build_group(dic_data['group'])
        str_order = self.build_order(dic_data['order'])
        str_select = self.build_select(dic_data['distinct'])

        str_sql = "%s %s from %s %s %s %s %s %s" % (str_select, str_fields, str_table_name, str_join, str_condition, str_group,
                                                        str_order, str_limit)
        #print(str_sql)
        if str_type == 'list':
            data = await self._fetch(str_sql, connection=connection)
        elif str_type == 'first':
            data = await self._fetchrow(str_sql, connection=connection)
        return data

    async def insert(self, str_table_name, dic_data, connection=None):
        """ 插入数据

        @params str_table_name string 表名
        @params dic_data dict 数据字典
        """
        dic_data = self.formatData(dic_data)
        str_table_name = self.build_table_name(str_table_name)

        str_sql = "insert into %s (%s) values (%s) RETURNING id" % (str_table_name, dic_data['key'], dic_data['val'])
        # print str_sql
        data = await self._fetchval(str_sql, connection=connection)
        return data

    async def update(self, str_table_name, dic_data, connection=None):
        """ 修改数据

        @params str_table_name string 表名
        @params dic_data dict 数据字典
        """

        dic_data = self.formatData(dic_data)
        str_table_name = self.build_table_name(str_table_name)
        str_fields = dic_data['fields']
        str_condition = self.build_condition(dic_data['condition'])

        str_sql = "update %s set %s %s" % (str_table_name, str_fields, str_condition)
        data = await self._execute(str_sql, connection=connection)
        return data

    async def delete(self, str_table_name, dic_data, connection=None):
        """ 删除数据

        @params str_table_name string 表名
        @params dic_data dict 数据字典
        """
        dic_data = self.formatData(dic_data)
        str_table_name = self.build_table_name(str_table_name)
        str_condition = self.build_condition(dic_data['condition'])

        str_sql = "delete from %s %s" % (str_table_name, str_condition)
        # print str_sql
        data = await self._execute(str_sql, connection=connection)
        return data

    def formatData(self, dic_data):
        """ 格式化数据
        将fields, condition, join 等数据格式化返回

        @params dic_data dict 数据字典
        """
        dic_data['fields'] = dic_data['fields'] if 'fields' in dic_data else ''
        dic_data['join'] = dic_data['join'] if 'join' in dic_data else ''
        dic_data['condition'] = dic_data['condition'] if 'condition' in dic_data else ''
        dic_data['order'] = dic_data['order'] if 'order' in dic_data else ''
        dic_data['group'] = dic_data['group'] if 'group' in dic_data else ''
        dic_data['limit'] = dic_data['limit'] if 'limit' in dic_data else ''
        dic_data['distinct'] = dic_data['distinct'] if 'distinct' in dic_data else False
        if 'key' in dic_data:
            if isinstance(dic_data['key'], list):
                dic_data['key'] = ','.join(dic_data['key'])
        else:
            dic_data['key'] = ''

        if 'val' in dic_data:
            if isinstance(dic_data['val'], list):
                dic_data['val'] = map(lambda f: '\''+f+'\'', dic_data['val'])
                dic_data['val'] = ','.join(dic_data['val'])
        else:
            dic_data['val'] = ''

        return dic_data

    def build_table_name(self, str_table_name):
        """ 构建表名
        根据配置文件中的表前辍，构建表名

        @params str_table_name string 表名
        """
        # str_table_name = self.dicConfig['DB_TABLEPRE'] + str_table_name if self.dicConfig.has_key('DB_TABLEPRE') and \
        #                  self.dicConfig['DB_TABLEPRE'] else str_table_name
        return str_table_name

    def build_fields(self, lis_fields):
        """ 构建读取字段

        @params lis_fields list 字段列表
        """
        str_fields = ','.join(lis_fields) if lis_fields else '*'
        return str_fields

    def build_join(self, str_join):
        """ 构建Join
        @params dicCondition dict 条件字典
        """

        return 'LEFT JOIN %s' % str_join if str_join else ''

    def build_condition(self, str_condition):
        """ 构建条件
        @params dicCondition dict 条件字典
        """

        return 'where %s' % str_condition if str_condition else ''

    def build_group(self, str_group):
        """ 构建order
        未完成
        @params
        """
        return 'group by ' + str_group if str_group else ''

    def build_order(self, str_order):
        """ 构建order
        未完成
        @params
        """
        return 'order by ' + str_order if str_order else ''

    def build_limit(self, lis_limit):
        """ 构建limit

        @params lis_limit list limit
        """
        str_limit = ','.join(lis_limit) if lis_limit else ''
        return 'limit ' + str_limit if str_limit else ''

    def build_select(self, distinct):
        """构建 select
        
        :param distinct: bool 是否包括 DISTINCT
        :return: str
        """
        return 'select distinct' if distinct else 'select'


