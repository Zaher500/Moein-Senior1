import os
import requests
from io import BytesIO


def fetch_lecture_file(request, lecture_id):
    course_service_url = os.getenv('COURSE_SERVICE_URL', 'http://localhost:8002')
    url = f"{course_service_url}/api/lectures/{lecture_id}/file/"

    headers = {}

    auth_header = request.headers.get('Authorization')
    student_id = request.headers.get('X-Student-ID')

    if auth_header:
        headers['Authorization'] = auth_header

    if student_id:
        headers['X-Student-ID'] = student_id

    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        content_disposition = response.headers.get('content-disposition', '')
        filename = f"lecture_{lecture_id}.pdf"

        if "filename=" in content_disposition:
            filename = content_disposition.split("filename=")[1].strip('"\' ')

        file_obj = BytesIO(response.content)
        file_obj.name = filename

        return file_obj, filename

    except requests.RequestException as e:
        raise Exception(f"Failed to fetch lecture file from Course Service: {str(e)}")