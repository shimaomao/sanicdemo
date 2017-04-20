from base.model import BaseModel
from base.environment import r_cache

from collections import defaultdict

import asyncio
import itertools
try:
    import uvloop as async_loop
except ImportError:
    async_loop = asyncio

try:
    import ujson as json
except ImportError:
    import json

loop = async_loop.new_event_loop()
asyncio.set_event_loop(loop=loop)


class SalaryModel(BaseModel):

    def data_format(self, data, show_id=False):

        data_list = []
        if show_id:
            [data_list.append({item['id']: item['name_zh'].strip()}) for item in data if item]
        else:
            [data_list.append(item['name_zh'].strip()) for item in data if item]
        return data_list

    async def get_all_city(self, show_id=False):

        data = await self.db.find('city', 'list', {})
        city_list = self.data_format(data,show_id)

        return city_list

    async def get_all_industry(self, show_id=False):
        data = await self.db.find('industry', 'list', {})
        category_list = self.data_format(data, show_id)

        return category_list

    async def get_all_scope(self, show_id=False):
        data = await self.db.find('company_scope', 'list', {})
        scope_list = self.data_format(data, show_id)
        return scope_list

    async def get_all_nature(self, show_id=False):
        data = await self.db.find('company_scope', 'list', {})
        nature_list = self.data_format(data, show_id)
        return nature_list



    async def get_dep_cate_mapping(self):
        data = await self.db.find('x_department as dep', 'list', {
            'fields': ['dep.id', 'dep.name as dep_name', 'cate.name as cate_name', 'category_id'],
            'join': 'x_category as cate on cate.id = dep.category_id'
        })
        mapping_dict = {}
        for item in data:
            if item['category_id'] in mapping_dict:
                mapping_dict[item['category_id']].append({item['id']: item['dep_name'].strip()})
            else:
                mapping_dict[item['category_id']] = [{item['id']: item['dep_name'].strip()}]
        return mapping_dict

    async def get_job_dep_mapping(self):
        data = await self.db.find('x_job as job', 'list', {
            'fields': ['job.id', 'job.name as job_name', 'dep.name as dep_name', 'department_id'],
            'join': 'x_department as dep on dep.id = job.department_id'
        })
        mapping_dict = {}
        for item in data:
            if item['department_id'] in mapping_dict:
                mapping_dict[item['department_id']].append({item['id']: item['job_name'].strip()})
            else:
                mapping_dict[item['department_id']] = [{item['id']: item['job_name'].strip()}]
        return mapping_dict