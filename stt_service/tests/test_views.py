from pathlib import Path
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings

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


def test_upload_audio_view_rejects_non_post(client):
    response = client.get("/stt/upload/")

    assert response.status_code == 405
    assert response.json() == {"error": "Only POST method allowed"}


@patch("stt.views.get_user_from_headers")
def test_upload_audio_view_returns_400_when_audio_missing(mock_get_user_from_headers, client):
    mock_get_user_from_headers.return_value = {
        "student_id": "student-123",
        "user_id": "user-123",
    }

    response = client.post("/stt/upload/", data={})

    assert response.status_code == 400
    assert response.json() == {"error": "No audio file provided"}


@patch("stt.views.get_user_from_headers")
@patch("stt.views.send_job_to_queue")
@patch("stt.views.create_stt_job")
def test_upload_audio_view_success(
    mock_create_stt_job,
    mock_send_job_to_queue,
    mock_get_user_from_headers,
    client,
    audio_file,
    tmp_path,
):
    mock_get_user_from_headers.return_value = {
        "student_id": "student-123",
        "user_id": "user-123",
    }

    with override_settings(MEDIA_ROOT=tmp_path):
        response = client.post("/stt/upload/", data={"audio": audio_file})

    assert response.status_code == 202

    body = response.json()
    assert body["message"] == "Audio uploaded and job queued successfully"
    assert "job_id" in body
    assert body["student_id"] == "student-123"
    assert body["user_id"] == "user-123"

    job_id = body["job_id"]

    mock_create_stt_job.assert_called_once()
    create_kwargs = mock_create_stt_job.call_args.kwargs

    assert create_kwargs["job_id"] == job_id
    assert create_kwargs["student_id"] == "student-123"
    assert create_kwargs["user_id"] == "user-123"
    assert create_kwargs["original_file_name"] == "lecture.wav"

    local_file_path = create_kwargs["local_file_path"]
    assert local_file_path.endswith(".wav")
    assert job_id in local_file_path

    mock_send_job_to_queue.assert_called_once()
    sent_payload = mock_send_job_to_queue.call_args.args[0]

    assert sent_payload["job_id"] == job_id
    assert sent_payload["student_id"] == "student-123"
    assert sent_payload["user_id"] == "user-123"
    assert sent_payload["original_file_name"] == "lecture.wav"
    assert sent_payload["local_file_path"] == local_file_path

    saved_file = Path(local_file_path)
    assert saved_file.exists()
    assert saved_file.read_bytes() == b"fake-audio-content"
    assert str(saved_file).startswith(str(tmp_path))


def test_get_transcript_status_view_rejects_non_get(client):
    response = client.post("/stt/stt-status/some-job-id/")

    assert response.status_code == 405
    assert response.json() == {"error": "Only GET method allowed"}


@patch("stt.views.get_user_from_headers")
@patch("stt.views.get_job_by_id", return_value=None)
def test_get_transcript_status_view_returns_404_when_job_not_found(
    mock_get_job_by_id,
    mock_get_user_from_headers,
    client,
):
    mock_get_user_from_headers.return_value = {
        "student_id": "student-123",
        "user_id": "user-123",
    }

    response = client.get("/stt/stt-status/missing-job-id/")

    assert response.status_code == 404
    assert response.json() == {"error": "Job not found"}
    mock_get_job_by_id.assert_called_once_with("missing-job-id", "student-123")


@patch("stt.views.get_user_from_headers")
@patch("stt.views.get_job_by_id")
def test_get_transcript_status_view_returns_job_data(
    mock_get_job_by_id,
    mock_get_user_from_headers,
    client,
):
    mock_get_user_from_headers.return_value = {
        "student_id": "student-123",
        "user_id": "user-123",
    }

    mock_get_job_by_id.return_value = {
        "job_id": "job-123",
        "student_id": "student-123",
        "user_id": "user-123",
        "original_file_name": "lecture.wav",
        "local_file_path": "/tmp/uploads/job-123.wav",
        "status": "completed",
        "raw_transcript": "raw text",
        "cleaned_transcript": "cleaned text",
        "error_message": "",
    }

    response = client.get("/stt/stt-status/job-123/")

    assert response.status_code == 200
    assert response.json()["job_id"] == "job-123"
    assert response.json()["status"] == "completed"
    assert response.json()["raw_transcript"] == "raw text"
    assert response.json()["cleaned_transcript"] == "cleaned text"

    mock_get_job_by_id.assert_called_once_with("job-123", "student-123")