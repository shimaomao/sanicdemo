route_config = {
    'mail': {
        'database': {
            'host': '127.0.0.1',
            'port': '',
            'user': '',
            'password': '',
            'db': '',
        },
        'rabbitmq': {
            'host': '127.0.0.1',
            'port': '',
            'exchange': 'mail',
            'type': 'fanout',
            'queue': 'msg_center_queue',
            'binding_key': ''
        }
    }
}