db_config = dict({
    'port': 6625,
    'host': '127.0.0.1',
    'database': 'salary',
    'user': 'Py',
    'password':'',

})
server_config = dict({
    'port': 6623,
    'host': '0.0.0.0',
})

redis_config = dict({
    'redis': dict({
                'host': '127.0.0.1',
                'port': 6379,
                'db': 3,
                'user_name': '',
                'password': ''
    }),
    'redis_cache': dict({
                    'host': '127.0.0.1',
                    'port': 6379,
                    'db': 3,
                    'user_name': '',
                    'password': ''
        })

})

base_config = {}