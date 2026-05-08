from ChatBot.selectors.chat_session_selector import get_student_session_or_404    #منجي لهون وبتم التحقق اذا هس السشن لهاد الطالب ولا لا بهدين قال لل شاتمسج سيرفس يحفظ الرسالة بال مايسك  view بعد ال 
from ChatBot.selectors.chat_message_selector import get_llm_ready_history  # rag_service بيستدي ال chat_orchestrator بعديم ال 
from ChatBot.services.chat_message_service import ChatMessageService # احفظي السؤال تبع الطالب بال مايسك chat_message_service بقول لل 
from ChatBot.services.rag_service import RAGService       #برجع للرومت لل اوركستريتلا prompt_builder وال prompt_builder بعتهم لل  chat_orchestrator رجع لهون فال rag_service لما ال   
from ChatBot.services.prompt_builder import PromptBuilder #  llm_service هلق الاوركستريتر بيبعت البرومت يلي اسمه ماسج لل 
from ChatBot.services.llm_service import LLMService

# This orchestrator will handle the entire flow of sending a message, including:
    # 1. validate session
    # 2. save user message
    # 3. get history
    # 4. retrieve context (RAG)
    # 5. build prompt
    # 6. call LLM
    # 7. save assistant message in DB
    # 8. return result
class ChatOrchestrator:
    @staticmethod #ZZ2
    def send_message(student_id, session_id, message_text):  # بتأكد اذا الطالب موجود 
        session = get_student_session_or_404(session_id, student_id)

        user_message = ChatMessageService.create_user_message(    # عم انشئ رسالة الطالب 
            session=session,
            content=message_text
        )

        rag_result = RAGService.retrieve_context(              # بعد ماحفظ السؤال بعت للراغ ال 
            student_id=student_id,
            query=message_text,
            session=session
        )
        print("RAG chunks count:", len(rag_result["chunks"]))
        print("RAG context preview:", rag_result["context_text"][:500])
        

        history = get_llm_ready_history(session=session, limit=10)     #zz8    عم نجيب اخر 10 رسائل انبعتوا بالجلسة 

        history_without_current_message = history[:-1] if history else []   

        retrieved_context = [
            chunk["chunk_text"]
            for chunk in rag_result["chunks"]
            if chunk.get("chunk_text")
        ]

        prompt_builder = PromptBuilder()    #zz9  ونبعتله كذااا PromptBuilder عم نتخاطب مع ال 
        messages = prompt_builder.build_messages(  # رايحين لهون
            user_message=message_text,             #prompt_builder يلي اجوني من  messagesبس رجعنا وخلصنا الخطوة 10 فتخزن بهي ال 
            chat_history=history_without_current_message,
            retrieved_context=retrieved_context,
        )
        print("Final messages:", messages)

        llm_service = LLMService()         # zz11   LLMService يدما نبعت لبرومت يلي خزناه بال سطر 47 بدي ابعته لل 
        try:
            assistant_text = llm_service.generate_response(messages=messages)     # generate_responseرايحين ل
        except Exception as e:
            print("LLM ERROR:", str(e))
            assistant_text = f"LLM failed: {str(e)}"

        assistant_message = ChatMessageService.create_assistant_message(          # الاجابو يلي اجت من الخطوة 13 جفظناها هون 
            session=session,
            content=assistant_text
        )

        return {                                         #zz14   Front لل response عم رجع ال 
            "user_message": user_message,
            "assistant_message": assistant_message,
            "rag_result": rag_result,
        }