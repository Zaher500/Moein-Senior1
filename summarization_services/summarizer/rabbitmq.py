import pika
import json

RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'lecture_texts'

def send_to_queue(data: dict):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT
        )
    )
    channel = connection.channel()

    channel.queue_declare(
        queue=RABBITMQ_QUEUE,
        durable=True
    )

    channel.basic_publish(
        exchange='',
        routing_key=RABBITMQ_QUEUE,
        body=json.dumps(data),
        properties=pika.BasicProperties(
            delivery_mode=2
        )
    )

    connection.close()
