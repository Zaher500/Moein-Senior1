from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def audio_file():
    return SimpleUploadedFile(
        "lecture.wav",
        b"fake-audio-content",
        content_type="audio/wav",
    )


@patch("stt.views.get_user_from_headers")
@patch("stt.views.send_job_to_queue")
@patch("stt.views.create_stt_job")
def test_upload_then_check_status_flow(
    mock_create_job,
    mock_send_job,
    mock_get_user_from_headers,
    client,
    audio_file,
):
    mock_get_user_from_headers.return_value = {
        "student_id": "student-123",
        "user_id": "user-123",
    }

    # Step 1: Upload audio
    upload_response = client.post(
        "/stt/upload/",
        data={"audio": audio_file},
    )

    assert upload_response.status_code == 202

    job_id = upload_response.json()["job_id"]

    # Step 2: mock DB response
    with patch("stt.views.get_job_by_id") as mock_get_job:
        mock_get_job.return_value = {
            "job_id": job_id,
            "student_id": "student-123",
            "user_id": "user-123",
            "status": "completed",
            "raw_transcript": "raw text",
            "cleaned_transcript": "clean text",
        }

        # Step 3: call status endpoint
        status_response = client.get(f"/stt/stt-status/{job_id}/")

        assert status_response.status_code == 200
        data = status_response.json()

        assert data["job_id"] == job_id
        assert data["status"] == "completed"
        assert data["raw_transcript"] == "raw text"
        assert data["cleaned_transcript"] == "clean text"

        mock_get_job.assert_called_once_with(job_id, "student-123")