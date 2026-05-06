from uuid import UUID
from django.shortcuts import get_object_or_404
from ChatBot.models import ChatSession


def get_student_sessions(student_id: UUID):
    return ChatSession.objects.filter(student_id=student_id).order_by("-created_at")


def get_student_session_or_404(session_id: UUID, student_id: UUID) -> ChatSession:
    return get_object_or_404(
        ChatSession,
        session_id=session_id,
        student_id=student_id,
    )