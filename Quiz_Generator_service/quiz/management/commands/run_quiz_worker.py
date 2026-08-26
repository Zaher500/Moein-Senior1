import json
import pika

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from quiz.models import Quiz, Question
from quiz.services.quiz_generator import generate_quiz
from quiz.services.mongo_store import store_llm_response


def normalize_options(options):
    if options is None:
        return ""
    if isinstance(options, list):
        return " | ".join(str(opt).strip() for opt in options)
    return str(options)


class Command(BaseCommand):
    help = "Run RabbitMQ worker for quiz generation"

    def handle(self, *args, **options):
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
        channel.basic_qos(prefetch_count=1)

        self.stdout.write(self.style.SUCCESS("Quiz worker is running..."))

        def callback(ch, method, properties, body):
            payload = json.loads(body)

            quiz_id = payload.get("quiz_id")
            lecture_id = payload.get("lecture_id")
            student_id = payload.get("student_id")
            text = payload.get("text")
            num_questions = payload.get("num_questions", 5)
            scope = payload.get("scope")
            question_mode = payload.get("question_mode", "mixed")

            quiz = None

            try:
                quiz = Quiz.objects.get(quiz_id=quiz_id)
                quiz.status = "PROCESSING"
                quiz.error = None
                quiz.save(update_fields=["status", "error"])

                if not text:
                    raise Exception("No text found in RabbitMQ payload")

                raw_response, valid_questions = generate_quiz(
                    text=text,
                    num_questions=num_questions,
                    scope=scope,
                    question_mode=question_mode
                )

                with transaction.atomic():
                    quiz.questions.all().delete()

                    for i, q_data in enumerate(valid_questions, start=1):
                        Question.objects.create(
                            quiz=quiz,
                            question_type=q_data.get("question_type"),
                            question_text=q_data.get("question_text"),
                            options=normalize_options(q_data.get("options")),
                            correct_answer=q_data.get("correct_answer"),
                            explanation=q_data.get("explanation", ""),
                            order=i
                        )

                    if valid_questions:
                        quiz.status = "READY"
                        quiz.error = None
                    else:
                        quiz.status = "FAILED"
                        quiz.error = "LLM failed to generate valid questions matching the requested schema."

                    quiz.save(update_fields=["status", "error"])

                try:
                    store_llm_response(
                        quiz_id=quiz.quiz_id,
                        lecture_id=lecture_id,
                        student_id=student_id,
                        raw_response=raw_response,
                        parsed_questions=valid_questions
                    )
                except Exception:
                    pass

                self.stdout.write(self.style.SUCCESS(f"Quiz {quiz_id} processed successfully"))

            except Exception as e:
                if quiz:
                    quiz.status = "FAILED"
                    quiz.error = str(e)
                    quiz.save(update_fields=["status", "error"])

                self.stdout.write(self.style.ERROR(f"Quiz {quiz_id} failed: {str(e)}"))

            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(
            queue=settings.RABBITMQ_QUEUE,
            on_message_callback=callback
        )

        channel.start_consuming()