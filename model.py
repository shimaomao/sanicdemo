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

    async def get_all_city(self):

        data = await self.db.find('x_city', 'list', {})
        city_list = []
        [city_list.append({item['id']: item['name'].strip()}) for item in data]
        return city_list

    async def get_all_category(self):
        data = await self.db.find('x_category', 'list', {})
        category_list = []
        [category_list.append({item['id']: item['name'].strip()}) for item in data]
        return category_list

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
