from ChatBot.selectors.chat_session_selector import get_student_session_or_404
from ChatBot.services.chat_message_service import ChatMessageService
from ChatBot.services.rag_service import RAGService
# This orchestrator will handle the entire flow of sending a message, including:
    # 1. validate session
    # 2. save user message
    # 3. get history
    # 4. retrieve context (RAG)
    # 5. build prompt
    # 6. call LLM
    # 7. save assistant message
    # 8. return result

class ChatOrchestrator:
    @staticmethod
    def send_message(student_id, session_id, message_text):
        session = get_student_session_or_404(session_id, student_id)

        user_message = ChatMessageService.create_user_message(
            session=session,
            content=message_text
        )

        rag_result = RAGService.retrieve_context(
            student_id=student_id,
            query=message_text,
            session=session
        )

        assistant_text = "This is a placeholder response until RAG + LLM are connected."

        assistant_message = ChatMessageService.create_assistant_message(
            session=session,
            content=assistant_text
        )

        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
            "rag_result": rag_result,
        }