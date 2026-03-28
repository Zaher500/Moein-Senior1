from ChatBot.models import ChatMessage


class ChatMessageService:
    @staticmethod
    def create_user_message(session, content: str) -> ChatMessage:
        return ChatMessage.objects.create(
            session=session,
            role="user",
            content=content,
        )

    @staticmethod
    def create_assistant_message(session, content: str) -> ChatMessage:
        return ChatMessage.objects.create(
            session=session,
            role="assistant",
            content=content,
        )