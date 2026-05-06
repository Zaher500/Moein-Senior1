import pika
import json

AMQP_URL = "amqps://sehjexip:suVDDD2vRqF_Ki9NL4ommVtLGgSI5LSe@cow.rmq2.cloudamqp.com/sehjexip"
QUEUE_NAME = "notifications_queue"


def send_notification(user_id, message, notif_type):
    try:
        params = pika.URLParameters(AMQP_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.queue_declare(queue=QUEUE_NAME, durable=False)

        payload = {
            "user_id": user_id,
            "message": message,
            "type": notif_type
        }

        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        connection.close()

        print("Notification sent:", payload)

    except Exception as e:
        print("Notification error:", str(e))