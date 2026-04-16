import os
from datetime import datetime
from pymongo import MongoClient

def store_llm_response(quiz_id, lecture_id, student_id, raw_response, parsed_questions):
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    mongo_db_name = os.getenv('MONGO_DB', 'quiz_results')
    
    try:
        client = MongoClient(mongo_uri)
        db = client[mongo_db_name]
        collection = db['llm_generation_logs']
        
        log_entry = {
            "quiz_id": str(quiz_id),
            "lecture_id": str(lecture_id) if lecture_id else None,
            "student_id": str(student_id),
            "raw_llm_response": raw_response,
            "parsed_questions": parsed_questions,
            "model_used": os.getenv('HF_MODEL'),
            "generated_at": datetime.utcnow()
        }
        
        collection.insert_one(log_entry)
        client.close()
    except Exception as e:
        print(f"Failed to save record to MongoDB: {str(e)}")
