from structure.controller import GetBaseInfo
from middlemare import success


route = {

    '/get_base_info': GetBaseInfo
}

middleware = {
    'response': [success]
}

err_route = {}