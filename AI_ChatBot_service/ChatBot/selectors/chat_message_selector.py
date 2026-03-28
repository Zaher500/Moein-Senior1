from ChatBot.models import ChatMessage


def get_session_messages(session):
    return ChatMessage.objects.filter(session=session).order_by("created_at")