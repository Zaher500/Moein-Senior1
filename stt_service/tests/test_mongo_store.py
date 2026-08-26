from unittest.mock import patch

from stt.mongo_store import (
    create_stt_job,
    get_job_by_id,
    mark_job_failed,
    save_job_result,
    update_job_status,
)


@patch("stt.mongo_store.collection")
def test_create_stt_job_inserts_expected_document(mock_collection):
    create_stt_job(
        job_id="job-123",
        student_id="student-123",
        user_id="user-123",
        original_file_name="lecture.wav",
        local_file_path="/tmp/uploads/job-123.wav",
    )

    mock_collection.insert_one.assert_called_once()
    inserted_doc = mock_collection.insert_one.call_args.args[0]

    assert inserted_doc["job_id"] == "job-123"
    assert inserted_doc["student_id"] == "student-123"
    assert inserted_doc["user_id"] == "user-123"
    assert inserted_doc["original_file_name"] == "lecture.wav"
    assert inserted_doc["local_file_path"] == "/tmp/uploads/job-123.wav"
    assert inserted_doc["status"] == "queued"
    assert inserted_doc["raw_transcript"] == ""
    assert inserted_doc["cleaned_transcript"] == ""
    assert inserted_doc["error_message"] == ""
    assert "created_at" in inserted_doc
    assert "updated_at" in inserted_doc


@patch("stt.mongo_store.collection")
def test_update_job_status_updates_status_and_error_message(mock_collection):
    update_job_status("job-456", "processing", "some warning")

    mock_collection.update_one.assert_called_once()
    filter_arg = mock_collection.update_one.call_args.args[0]
    update_arg = mock_collection.update_one.call_args.args[1]

    assert filter_arg == {"job_id": "job-456"}
    assert update_arg["$set"]["status"] == "processing"
    assert update_arg["$set"]["error_message"] == "some warning"
    assert "updated_at" in update_arg["$set"]


@patch("stt.mongo_store.collection")
def test_update_job_status_defaults_error_message_to_empty_string(mock_collection):
    update_job_status("job-789", "queued")

    mock_collection.update_one.assert_called_once()
    update_arg = mock_collection.update_one.call_args.args[1]

    assert update_arg["$set"]["status"] == "queued"
    assert update_arg["$set"]["error_message"] == ""
    assert "updated_at" in update_arg["$set"]


@patch("stt.mongo_store.collection")
def test_save_job_result_sets_completed_status_and_transcripts(mock_collection):
    save_job_result(
        job_id="job-999",
        raw_transcript="raw text",
        cleaned_transcript="cleaned text",
    )

    mock_collection.update_one.assert_called_once()
    filter_arg = mock_collection.update_one.call_args.args[0]
    update_arg = mock_collection.update_one.call_args.args[1]

    assert filter_arg == {"job_id": "job-999"}
    assert update_arg["$set"]["status"] == "completed"
    assert update_arg["$set"]["raw_transcript"] == "raw text"
    assert update_arg["$set"]["cleaned_transcript"] == "cleaned text"
    assert update_arg["$set"]["error_message"] == ""
    assert "updated_at" in update_arg["$set"]


@patch("stt.mongo_store.collection")
def test_mark_job_failed_sets_failed_status_and_error_message(mock_collection):
    mark_job_failed("job-500", "Something went wrong")

    mock_collection.update_one.assert_called_once()
    filter_arg = mock_collection.update_one.call_args.args[0]
    update_arg = mock_collection.update_one.call_args.args[1]

    assert filter_arg == {"job_id": "job-500"}
    assert update_arg["$set"]["status"] == "failed"
    assert update_arg["$set"]["error_message"] == "Something went wrong"
    assert "updated_at" in update_arg["$set"]


@patch("stt.mongo_store.collection")
def test_get_job_by_id_returns_document_without_id(mock_collection):
    mock_collection.find_one.return_value = {
        "job_id": "job-321",
        "student_id": "student-123",
        "status": "completed",
        "raw_transcript": "raw",
        "cleaned_transcript": "clean",
    }

    result = get_job_by_id("job-321", "student-123")

    mock_collection.find_one.assert_called_once_with(
        {"job_id": "job-321", "student_id": "student-123"},
        {"_id": 0},
    )
    assert result["job_id"] == "job-321"
    assert result["status"] == "completed"


@patch("stt.mongo_store.collection")
def test_get_job_by_id_returns_none_when_job_not_found(mock_collection):
    mock_collection.find_one.return_value = None

    result = get_job_by_id("missing-job", "student-123")

    mock_collection.find_one.assert_called_once_with(
        {"job_id": "missing-job", "student_id": "student-123"},
        {"_id": 0},
    )
    assert result is None