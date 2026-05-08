from ChatBot.models import ChatSession   # بانشا جلسة


class ChatSessionService:
    @staticmethod
    def create_session(student_id, title: str | None = None) -> ChatSession:
        title = title or "New Chat"
        return ChatSession.objects.create(
            student_id=student_id,
            title=title,
        )