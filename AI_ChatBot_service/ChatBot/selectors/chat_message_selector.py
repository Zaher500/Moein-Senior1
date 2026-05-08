from ChatBot.models import ChatMessage


def get_session_messages(session):
    return ChatMessage.objects.filter(session=session).order_by("created_at")

def get_llm_ready_history(session, limit: int = 10):
    messages = (
        ChatMessage.objects
        .filter(session=session)
        .order_by("-created_at")[:limit]
    )

    # reverse to oldest → newest
    messages = list(messages)[::-1]

    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]