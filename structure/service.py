from base.service import BaseService
from sanic.exceptions import SanicException
import base64
import logging
from datetime import datetime, timedelta
from time import time
from base.exception import *



class SalaryService(BaseService):

    async def get_base_info(self, show_id=False):
        city_list = await self.model['salary'].get_all_city(show_id)
        industry_list = await self.model['salary'].get_all_industry(show_id)
        scope_list = await self.model['salary'].get_all_scope(show_id)
        nature_list = await self.model['salary'].get_all_nature(show_id)

        data = {
            'city': city_list,
            'industry': industry_list,
            'scale': scope_list,
            'nature': nature_list
        }
        return data

    async def get_city_list(self):
        city_list = await self.model['salary'].get_all_city()
        return city_list

    async def get_category_list(self):
        category_list = await self.model['salary'].get_all_category()
        return category_list

    async def get_dep_cate_mapping(self):
        dep_cate_mapping = await self.model['salary'].get_dep_cate_mapping()
        return dep_cate_mapping

    async def get_job_dep_mapping(self):
        job_dep_mapping = await self.model['salary'].get_job_dep_mapping()
        return job_dep_mapping
