from datetime import datetime, timezone

from django.conf import settings
from pymongo import MongoClient


client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]
collection = db[settings.MONGO_STT_COLLECTION]


def utc_now():
    return datetime.now(timezone.utc)


def create_stt_job(job_id, student_id, user_id, original_file_name, local_file_path):
    doc = {
        "job_id": job_id,
        "student_id": student_id,
        "user_id": user_id,
        "original_file_name": original_file_name,
        "local_file_path": local_file_path,
        "status": "queued",
        "raw_transcript": "",
        "cleaned_transcript": "",
        "error_message": "",
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }
    collection.insert_one(doc)


def update_job_status(job_id: str, status: str, error_message: str = ""):
    collection.update_one(
        {"job_id": job_id},
        {
            "$set": {
                "status": status,
                "error_message": error_message,
                "updated_at": utc_now(),
            }
        },
    )


def save_job_result(job_id: str, raw_transcript: str, cleaned_transcript: str):
    collection.update_one(
        {"job_id": job_id},
        {
            "$set": {
                "status": "completed",
                "raw_transcript": raw_transcript,
                "cleaned_transcript": cleaned_transcript,
                "error_message": "",
                "updated_at": utc_now(),
            }
        },
    )


def mark_job_failed(job_id: str, error_message: str):
    collection.update_one(
        {"job_id": job_id},
        {
            "$set": {
                "status": "failed",
                "error_message": error_message,
                "updated_at": utc_now(),
            }
        },
    )


def get_job_by_id(job_id: str, student_id: str):
    return collection.find_one(
        {"job_id": job_id, "student_id": student_id},
        {"_id": 0}
    )