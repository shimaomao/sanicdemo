from sanic import response


async def success(req, resp, env=None):

    return response.json({
            'code': 0,
            'msg': 'operation successful',
            'id': 0,
            'data': resp
        })
