import requests
from django.conf import settings


def send_for_summarization(lecture_id: str, text: str, request) -> None:
    url = f"{settings.SERVICES['summarizer']}/api/lecture-text/"

    payload = {
        "lecture_id": str(lecture_id),
        "text": text,
    }

    headers = {
    "Authorization": request.headers.get("Authorization"),
    "X-Student-ID": request.headers.get("X-Student-ID"),
    "X-User-ID": request.headers.get("X-User-ID"),
    "Content-Type": "application/json",
}

    print("OUTGOING HEADERS:", headers)

    response = requests.post(
        url,
        json=payload,
        headers=headers,   
        timeout=settings.SUMMARIZATION_SERVICE["timeout"]
    )

    print("STATUS:", response.status_code, response.text)
    response.raise_for_status()
    

def is_summary_ready(lecture_id: str) -> bool:
    """
    Ask summarization service if summary is ready.

    """

    url = f"{settings.SUMMARIZATION_SERVICE['base_url']}/api/summary/status/{lecture_id}/"

    response = requests.get(
        url,
        timeout=settings.SUMMARIZATION_SERVICE['timeout']
    )

    print("STATUS:", response.status_code, response.text)
    response.raise_for_status()

    data = response.json()
    return data.get('ready', False)

def get_summary(lecture_id: str) -> dict:
    """
    Fetch summary from summarization service.
    """
    url = f"{settings.SUMMARIZATION_SERVICE['base_url']}/api/summary/{lecture_id}/"

    response = requests.get(
        url,
        timeout=settings.SUMMARIZATION_SERVICE['timeout']
    )

    response.raise_for_status()
    return response.json()

