from sanic import response
import logging
import datetime
logging.getLogger().setLevel(logging.INFO)

async def success(req, resp, env=None):

    return response.json({
            'code': 0,
            'msg': 'operation successful',
            'id': 0,
            'data': resp
        })

async def log(req, env=None):
    if req.method == "POST":
        query = req.body
    else:
        query = req.query_string

    logging.info({'path': req.path, 'query': query, 'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} )

