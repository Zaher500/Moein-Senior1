import json
import pika
from django.conf import settings


def publish_quiz_job(payload: dict):
    credentials = pika.PlainCredentials(
        settings.RABBITMQ_USER,
        settings.RABBITMQ_PASSWORD
    )

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=credentials
        )
    )

    channel = connection.channel()

    channel.queue_declare(
        queue=settings.RABBITMQ_QUEUE,
        durable=True
    )

    channel.basic_publish(
        exchange='',
        routing_key=settings.RABBITMQ_QUEUE,
        body=json.dumps(payload),
        properties=pika.BasicProperties(
            delivery_mode=2
        )
    )

    connection.close()
