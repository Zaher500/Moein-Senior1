import requests
from django.conf import settings


def send_for_chatbot_ingestion(
    lecture_id: str,
    course_id: str,
    student_id: str,
    text: str,
    source_type: str = "lecture",
) -> None:
    """
    Fire-and-forget request to ChatBot service ingestion endpoint.
    """
    print(settings.SERVICES)
    url = f"{settings.SERVICES['chatbot']}/api/chat/lectures/ingest/"
    payload = {
        "lecture_text": text,
        "lecture_id": str(lecture_id),
        "course_id": str(course_id),
        "source_type": source_type,
    }
    headers = {
        "X-Student-ID": str(student_id),
        "X-GATEWAY-SECRET": settings.GATEWAY_SECRET,
    }

    requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=settings.CHATBOT_SERVICE["timeout"],
    )