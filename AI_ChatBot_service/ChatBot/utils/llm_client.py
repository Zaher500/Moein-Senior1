from huggingface_hub import InferenceClient
from django.conf import settings


class LLMClient:
    def __init__(self):
        self.api_key = settings.HF_API_KEY
        self.model = settings.HF_MODEL

        if not self.api_key:
            raise ValueError("HF_API_KEY is not set in environment variables")

        self.client = InferenceClient(
            model=self.model,
            token=self.api_key
        )

    def chat_completion(self, messages, temperature=None, max_tokens=None):  #zz13  لسطر 23 عم يبعت للمودل
        response = self.client.chat.completions.create(
            messages=messages,
            temperature=temperature or settings.LLM_TEMPERATURE,
            max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
        )

        return response.choices[0].message.content    # zz13 يلي عم يجينا من المودل response ال