from ChatBot.selectors.chat_session_selector import get_student_session_or_404
from ChatBot.selectors.chat_message_selector import get_llm_ready_history
from ChatBot.services.chat_message_service import ChatMessageService
from ChatBot.services.rag_service import RAGService
from ChatBot.services.prompt_builder import PromptBuilder
from ChatBot.services.llm_service import LLMService
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

        # keep RAG placeholder for later
        rag_result = RAGService.retrieve_context(
            student_id=student_id,
            query=message_text,
            session=session
        )

        # get recent history from selector
        history = get_llm_ready_history(session=session, limit=10)

        # remove current user message from history to avoid duplication
        history_without_current_message = history[:-1] if history else []

        # build prompt
        prompt_builder = PromptBuilder()
        messages = prompt_builder.build_messages(
            user_message=message_text,
            chat_history=history_without_current_message,
            retrieved_context=None,   # later: rag_result
        )

        # generate AI response
        llm_service = LLMService()
        try:
            assistant_text = llm_service.generate_response(messages=messages)
        except Exception as e:
            print("LLM ERROR:", str(e))
            assistant_text = f"LLM failed: {str(e)}"

        assistant_message = ChatMessageService.create_assistant_message(
            session=session,
            content=assistant_text
        )

        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
            "rag_result": rag_result,
        }