import uuid
import os

from pymongo import MongoClient
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Quiz, Question, QuizAttempt, Answer
from .serializers import QuizSerializer
from .services.file_extractor import extract_text_from_file
from .services.course_client import fetch_lecture_file
from .services.quiz_generator import generate_quiz
from .services.mongo_store import store_llm_response



def build_response(success, message, data=None, status_code=200):
    return Response({
        "success": success,
        "message": message,
        "data": data or {}
    }, status=status_code)


def _validate_num_questions(num_questions):
    try:
        num_questions = int(num_questions)
        if num_questions <= 0:
            raise ValueError
        return num_questions, None
    except (TypeError, ValueError):
        return None, build_response(False, 'num_questions must be a positive integer', status_code=400)


def _validate_uuid(value, field_name):
    try:
        uuid.UUID(str(value))
        return None
    except (ValueError, TypeError):
        return build_response(False, f'{field_name} must be a valid UUID', status_code=400)


def _validate_file(file_obj):
    if not file_obj:
        return build_response(False, 'File is required', status_code=400)

    allowed_extensions = ['.pdf', '.docx']
    filename = file_obj.name.lower()

    if not any(filename.endswith(ext) for ext in allowed_extensions):
        return build_response(False, 'Only PDF and DOCX files are allowed', status_code=400)

    if file_obj.size == 0:
        return build_response(False, 'Uploaded file is empty', status_code=400)

    return None


def _process_quiz_generation(request, source_type, text, num_questions, lecture_id, course_id, title, scope=None):
    student_id = request.headers.get('X-Student-ID')
    if not student_id:
        return build_response(False, 'X-Student-ID header is missing', status_code=400)

    quiz = Quiz.objects.create(
        lecture_id=lecture_id,
        course_id=course_id,
        student_id=student_id,
        title=title,
        source=source_type,
        status='PROCESSING',
        num_questions=num_questions
    )

    try:
        raw_response, valid_questions = generate_quiz(text, num_questions, scope)

        with transaction.atomic():
            for i, q_data in enumerate(valid_questions, start=1):
                Question.objects.create(
                    quiz=quiz,
                    question_type=q_data.get('question_type'),
                    question_text=q_data.get('question_text'),
                    options=q_data.get('options', []),
                    correct_answer=q_data.get('correct_answer'),
                    explanation=q_data.get('explanation', ''),
                    order=i
                )

            if valid_questions:
                quiz.status = 'READY'
                quiz.error = None
            else:
                quiz.status = 'FAILED'
                quiz.error = "LLM failed to generate valid questions matching the requested schema."

            quiz.save()

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

        return build_response(
            True,
            "Quiz generated successfully",
            {
                "quiz_id": quiz.quiz_id,
                "status": quiz.status,
                "generated_count": len(valid_questions)
            },
            status_code=201
        )

    except Exception as e:
        quiz.status = 'FAILED'
        quiz.error = str(e)
        quiz.save()

        return build_response(
            False,
            "Quiz generation failed",
            {"error": str(e)},
            status_code=500
        )


@api_view(['POST'])
def generate_from_file_view(request):
    file_obj = request.FILES.get('file')
    lecture_id = request.data.get('lecture_id')
    course_id = request.data.get('course_id')
    num_questions = request.data.get('num_questions', 5)
    title = request.data.get('title', 'Generated Quiz')

    if not all([file_obj, lecture_id, course_id]):
        return build_response(False, 'file, lecture_id, and course_id are required fields', status_code=400)

    error = _validate_uuid(lecture_id, 'lecture_id')
    if error:
        return error

    error = _validate_uuid(course_id, 'course_id')
    if error:
        return error

    file_error = _validate_file(file_obj)
    if file_error:
        return file_error

    num_questions, error_response = _validate_num_questions(num_questions)
    if error_response:
        return error_response

    try:
        text = extract_text_from_file(file_obj, file_obj.name)
    except Exception as e:
        return build_response(False, f'File extraction failed: {str(e)}', status_code=500)

    return _process_quiz_generation(
        request, 'FILE', text, num_questions, lecture_id, course_id, title
    )


@api_view(['POST'])
def generate_from_existing_view(request):
    lecture_id = request.data.get('lecture_id')
    course_id = request.data.get('course_id')
    num_questions = request.data.get('num_questions', 5)
    title = request.data.get('title', 'Generated Quiz')

    if not all([lecture_id, course_id]):
        return build_response(False, 'lecture_id and course_id are required fields', status_code=400)

    error = _validate_uuid(lecture_id, 'lecture_id')
    if error:
        return error

    error = _validate_uuid(course_id, 'course_id')
    if error:
        return error

    num_questions, error_response = _validate_num_questions(num_questions)
    if error_response:
        return error_response

    try:
        file_obj, filename = fetch_lecture_file(lecture_id)
        text = extract_text_from_file(file_obj, filename)
    except Exception as e:
        return build_response(False, str(e), status_code=500)

    return _process_quiz_generation(
        request, 'EXISTING', text, num_questions, lecture_id, course_id, title
    )


@api_view(['POST'])
def generate_from_scope_view(request):
    lecture_id = request.data.get('lecture_id')
    course_id = request.data.get('course_id')
    num_questions = request.data.get('num_questions', 5)
    title = request.data.get('title', 'Generated Quiz')
    scope = request.data.get('scope')

    if not all([lecture_id, course_id, scope]):
        return build_response(
            False,
            'lecture_id, course_id, and scope are required fields',
            status_code=400
        )

    error = _validate_uuid(lecture_id, 'lecture_id')
    if error:
        return error

    error = _validate_uuid(course_id, 'course_id')
    if error:
        return error

    num_questions, error_response = _validate_num_questions(num_questions)
    if error_response:
        return error_response

    try:
        file_obj, filename = fetch_lecture_file(lecture_id)
    except Exception as e:
        return build_response(
            False,
            f'Failed to fetch lecture file: {str(e)}',
            status_code=500
        )

    if not file_obj:
        return build_response(
            False,
            'Lecture file not found',
            status_code=404
        )

    try:
        file_obj.seek(0)  # 🔥 مهم جداً
        text = extract_text_from_file(file_obj, filename)
    except Exception as e:
        return build_response(
            False,
            f'File extraction failed: {str(e)}',
            status_code=500
        )

    return _process_quiz_generation(
        request,
        'SCOPE',
        text,
        num_questions,
        lecture_id,
        course_id,
        title,
        scope=scope
    )

@api_view(['GET', 'DELETE'])
def quiz_detail_view(request, quiz_id):
    error = _validate_uuid(quiz_id, 'quiz_id')
    if error:
        return error

    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)

    if request.method == 'GET':
        serializer = QuizSerializer(quiz)
        return build_response(True, "Quiz fetched successfully", serializer.data, status_code=200)

    try:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        mongo_db_name = os.getenv('MONGO_DB', 'quiz_results')
        client = MongoClient(mongo_uri)
        db = client[mongo_db_name]
        db['llm_generation_logs'].delete_one({"quiz_id": str(quiz_id)})
        client.close()
    except Exception:
        pass

    quiz.delete()
    return build_response(True, "Quiz deleted successfully", status_code=204)


@api_view(['GET'])
def quiz_status_view(request, quiz_id):
    error = _validate_uuid(quiz_id, 'quiz_id')
    if error:
        return error

    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)

    return build_response(
        True,
        "Quiz status fetched",
        {
            "quiz_id": quiz.quiz_id,
            "status": quiz.status,
            "error": quiz.error
        },
        status_code=200
    )


@api_view(['GET'])
def quiz_by_lecture_view(request, lecture_id):
    error = _validate_uuid(lecture_id, 'lecture_id')
    if error:
        return error

    quizzes = Quiz.objects.filter(lecture_id=lecture_id)
    serializer = QuizSerializer(quizzes, many=True)

    return build_response(
        True,
        "Lecture quizzes fetched successfully",
        serializer.data,
        status_code=200
    )


@api_view(['POST'])
def quiz_submit_view(request, quiz_id):
    error = _validate_uuid(quiz_id, 'quiz_id')
    if error:
        return error

    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    student_id = request.headers.get('X-Student-ID')

    if not student_id:
        return build_response(False, 'X-Student-ID header is missing', status_code=400)

    answers_data = request.data.get('answers', [])
    if not isinstance(answers_data, list):
        return build_response(False, 'answers must be a JSON array', status_code=400)

    if not answers_data:
        return build_response(False, 'answers list cannot be empty', status_code=400)

    for ans in answers_data:
        if 'question_id' not in ans or 'selected_answer' not in ans:
            return build_response(False, 'Each answer must contain question_id and selected_answer', status_code=400)

        question_id_error = _validate_uuid(ans.get('question_id'), 'question_id')
        if question_id_error:
            return question_id_error

    total_questions = quiz.questions.count()
    if total_questions == 0:
        return build_response(False, 'This quiz has no valid questions to score.', status_code=400)

    score = 0
    results = []

    with transaction.atomic():
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student_id=student_id,
            score=0.0,
            total=total_questions
        )

        for ans_data in answers_data:
            q_id = str(ans_data.get('question_id')).strip()
            selected_answer = str(ans_data.get('selected_answer', '')).strip()

            question = quiz.questions.filter(question_id=q_id).first()
            if not question:
                continue


            is_correct = selected_answer.lower() == str(question.correct_answer).strip().lower()

            if is_correct:
                score += 1

            Answer.objects.create(
                attempt=attempt,
                question=question,
                selected_answer=selected_answer,
                is_correct=is_correct
            )

            results.append({
                "question_id": question.question_id,
                "question_text": question.question_text,
                "selected_answer": selected_answer,
                "correct_answer": question.correct_answer,
                "is_correct": is_correct,
                "explanation": question.explanation
            })

        percentage = (score / total_questions) * 100.0
        attempt.score = score
        attempt.save()

    return build_response(
        True,
        "Quiz submitted successfully",
        {
            "attempt_id": attempt.attempt_id,
            "score": score,
            "total": total_questions,
            "percentage": round(percentage, 2),
            "results": results
        },
        status_code=201
    )
