from ChatBot.utils.llm_client import LLMClient  #Qween وبيبعتهم لل llm_service بعدين بيستقبل  ال البرومت والنص من  llm_client من خلال  Qween بيعمل اتصال مغ ال
# طبعا البرومت اجا من الاوركساريتر

#  chat_orchestrator رجهتها لل llm_serviceوال  llm_service رجغت الاجابة للllm_client اخر شي بس ال 
#  مشان يخزن الرد بالمايسكchat_message_serviceبيستدعي ال  chat_orchestrator وبعدين ال 
class LLMService:
    def __init__(self):
        self.client = LLMClient()

    def generate_response(self, messages):           #zz12  LLMclient نفس المسج عم يبعتها لل 
        try:
            response = self.client.chat_completion(messages=messages)    # chat_completionهلق رايحين ل 
            return response.strip()                                       # responseفرحنا عملنا الخطوة 13 وحزنا النتيحة بال 
        except Exception as e:                                            #  بسطر 13 عم رجعها لل اوركاستيريتر
            # You can log this later
            raise Exception(f"LLMService error: {str(e)}")