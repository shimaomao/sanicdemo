from sanic import response
from sanic.exceptions import ServerError
from base.controller import BaseHandler, JsonHandler
import logging
from structure.config import route_config
import pika
from structure.service import SalaryService
try:
    import ujson as json
except ImportError:
    import json


class GetBaseInfo(BaseHandler):

    async def handle(self):
        try:
            salary_service = SalaryService(env=self.env)
            result = await salary_service.get_base_info(show_id=True)
            return result
        except Exception as e:
            raise ServerError(str(e.args))


class GetJobInfo(BaseHandler):

    async def handle(self):
        try:
            salary_service = SalaryService(env=self.env)
            result = await salary_service.get_job_info(show_id=True)
            return result
        except Exception as e:
            raise ServerError(str(e.args))


class GetJobByCateAndRank(JsonHandler):

    async def handle(self):
        try:
            rank_code = self.data.get('rank_code')
            category_code = self.data.get('category_code')
            salary_service = SalaryService(env=self.env)
            result = await salary_service.get_job_by_cate_rank(category_code, rank_code)
            return result
        except Exception as e:
            raise ServerError(str(e.args))


class JobMapping(JsonHandler):

    async def handle(self):
        try:
            name_list = self.data.get('job_list')
            salary_service = SalaryService(env=self.env)
            result = await salary_service.get_job_info_by_name(name_list)
            return result
        except Exception as e:
            raise ServerError(str(e.args))


class ExcelUpload(BaseHandler):

    async def handle(self):
        try:
            result = self.excel_mq()
            return result
        except Exception as e:
            raise ServerError(str(e.args))

    def excel_mq(self):

        rabbitmq_config = route_config.get('excel')
        exchange_name = rabbitmq_config.get('exchange')
        exchange_type = rabbitmq_config.get('type')
        queue_name = rabbitmq_config.get('queue')

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_config.get('host')))
        channel = connection.channel()
        result = channel.basic_publish(exchange=exchange_name,
                      routing_key='excel',
                      body='hello')
        connection.close()
        return result