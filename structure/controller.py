from sanic import response
from sanic.exceptions import ServerError
from base.controller import BaseHandler
import logging
from structure.service import SalaryService
try:
    import ujson as json
except ImportError:
    import json


class GetBaseInfo(BaseHandler):

    async def handle(self):
        try:
            salary_service = SalaryService(env=self.env)
            result = await salary_service.get_base_info()
            return result
        except Exception as e:
            raise ServerError(str(e.args))