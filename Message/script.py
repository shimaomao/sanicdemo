import pika
from Message.config import route_config


rabbitmq_config = route_config['mail']['rabbitmq']


def mail_mq():
    exchange_name = rabbitmq_config.get('exchange')
    exchange_type = rabbitmq_config.get('type')
    queue_name = rabbitmq_config.get('queue')

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_config.get('host')))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange_name, type=exchange_type)
    channel.queue_declare(queue_name, exclusive=False)
    channel.queue_bind(queue_name, exchange_name)
    connection.close()


if __name__ == '__main__':
    mail_mq()
