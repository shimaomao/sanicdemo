from base.service import BaseService
from sanic.exceptions import SanicException
import base64
import logging
from datetime import datetime, timedelta
from time import time
from base.exception import *
from scipy.stats import chi2

class SalaryService(BaseService):

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
