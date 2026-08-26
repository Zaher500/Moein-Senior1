from groq import Groq
from django.conf import settings


class LLMClient:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL

        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not set in environment variables")

        self.client = Groq(
            api_key=self.api_key,
        )

    def chat_completion(self, messages, temperature=None, max_tokens=None):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or settings.LLM_TEMPERATURE,
            max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
        )

        return response.choices[0].message.content