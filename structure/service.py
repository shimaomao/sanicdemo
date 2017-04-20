from base.service import BaseService
from sanic.exceptions import SanicException
import random


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

    async def get_job_info(self, show_id=False):
        rank_list = await self.model['salary'].get_all_rank(show_id)
        job_mapping = await self.model['salary'].get_job_cate_mapping()
        data = {
            'rank': rank_list,
            'job_category': job_mapping
        }
        return data

    async def get_job_by_cate_rank(self, category_id, rank_id):
        jobs = await self.model['salary'].get_job_by_cate_rank(category_id, rank_id)
        return jobs

    async def get_job_info_by_name(self, name_list):
        jobs = await self.model['salary'].get_job_info_by_name(name_list)
        job_dict = {}
        data = []
        for job in jobs:
            job_dict[job['name_zh']] = {
                'name': job['name_zh'],
                'code': job['code'],
                'rank_code': job['job_grade_code'],
                'rank_name': job['job_grade_name'],
                'job_category_code': job['job_category_code'],
                'job_category_name': job['job_category_name'],
                'market_50': random.randint(10000, 20000)
            }

        [data.append({'job_name':item, 'market_info':job_dict.get(item, None)}) for item in name_list]

        return data
