import pika
import json

url = "amqps://sehjexip:suVDDD2vRqF_Ki9NL4ommVtLGgSI5LSe@cow.rmq2.cloudamqp.com/sehjexip"

params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue='notifications_queue')

message = {
    "user_id": "123",
    "message": "Hello from CLOUD 🚀",
    "type": "transcribe"
}

channel.basic_publish(
    exchange='',
    routing_key='notifications_queue',
    body=json.dumps(message)
)

print("✅ Sent to CloudAMQP")
connection.close()