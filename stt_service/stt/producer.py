import pika
import json
from django.conf import settings


def send_job_to_queue(job_payload):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
    )
    channel = connection.channel()

    channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=settings.RABBITMQ_QUEUE,
        body=json.dumps(job_payload),
        properties=pika.BasicProperties(
            delivery_mode=2
        )
    )

    connection.close()