import pika
import json

from chunking import chunk_text
from summarization import summarize_text
from db.mongo import save_summary



RABBITMQ_HOST = "localhost"
RABBITMQ_QUEUE = "lecture_texts"


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        lecture_id = data.get("lecture_id")
        text = data.get("text")

        if not lecture_id or not text:
            print("Invalid message:", data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print(f" Processing lecture {lecture_id}")

        
        chunks = chunk_text(text)
        print(f"🔹 {len(chunks)} chunks created")

        
        chunk_summaries = []

        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i + 1}/{len(chunks)}")
            summary = summarize_text(chunk)

            if summary:
                chunk_summaries.append(summary)

        if not chunk_summaries:
            print("No summaries generated")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        cleaned_summaries = []

        for summary in chunk_summaries:
            cleaned = summary.replace("**Summary in Arabic:**", "").strip()
            cleaned = cleaned.replace("**Summary in English:**", "").strip()
            cleaned_summaries.append(cleaned)
        final_summary = " ".join(cleaned_summaries)

        save_summary(lecture_id, final_summary)

        print(f"Summary saved for lecture {lecture_id}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("Consumer error:", str(e))


def start_consumer():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=RABBITMQ_QUEUE,
        on_message_callback=callback
    )

    print("Waiting for lecture messages...")
    channel.start_consuming()


if __name__ == "__main__":
    start_consumer()