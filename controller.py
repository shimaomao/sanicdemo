from sanic import response
from sanic.exceptions import ServerError
from base.controller import BaseHandler
import logging
from service import SalaryService
try:
    import ujson as json
except ImportError:
    import json

n=0

class CityList(BaseHandler):

    async def handle(self):
        try:
            salary_service = SalaryService(env=self.env)
            result = await salary_service.get_city_list()
            return result
        except Exception as e:
            raise ServerError(str(e.args))


class CategoryList(BaseHandler):
    async def handle(self):
        try:
            salary_service = SalaryService(env=self.env)
            result = await salary_service.get_category_list()
            return result
        except Exception as e:
            raise ServerError(str(e.args))


class CateDepMapping(BaseHandler):
    async def handle(self):
        try:
            salary_service = SalaryService(env=self.env)
            result = await salary_service.get_dep_cate_mapping()
            return result
        except Exception as e:
            raise ServerError(str(e.args))


class DepJobMapping(BaseHandler):
    async def handle(self):
        try:
            salary_service = SalaryService(env=self.env)
            result = await salary_service.get_job_dep_mapping()
            return result
        except Exception as e:
            raise ServerError(str(e.args))


class CompanyDetail(BaseHandler):
    def handle(self, *args, **kwargs):
        return  {
                "nature": [
                    {
                        "id": 1,
                        'name': "国企"
                    }, {
                        "id": 2,
                        'name': "上市公司"
                    }, {
                        "id": 3,
                        'name': "私营单位"
                    }
                ],
                "stage": [
                    {
                        "id": 1,
                        'name': "初创"
                    }, {
                        "id": 2,
                        'name': "成长"
                    }, {
                        "id": 3,
                        'name': "稳定"
                    }, {
                        "id": 4,
                        'name': "衰退"
                    }
                ],
                "scale": [
                    {
                        "id": 1,
                        'name': "1-50"
                    }, {
                        "id": 2,
                        'name': "50-500"
                    }, {
                        "id": 3,
                        'name': "500-5000"
                    }
                ],
                "record": [
                    {
                        "id": 1,
                        'name': "本科"
                    }, {
                        "id": 2,
                        'name': "硕士"
                    }, {
                        "id": 3,
                        'name': "博士"
                    }
                ]

            }


class SalaryData(BaseHandler):
    def handle(self, *args, **kwargs):
        import time
        print(self.request)