class PromptBuilder:
    SYSTEM_PROMPT = (
        "You are Moein, an AI academic student assistant. "
        "Help students understand topics clearly and accurately. "
        "Give concise, educational, and well-structured answers. "
        "Keep responses brief by default unless the user asks for more detail. "
        "Prefer a short paragraph or a few bullet points instead of long explanations."
        "If you are not sure or the information is not available, say that clearly. "
        "Do not invent facts or make unsupported claims."
    )

    def build_messages(self, user_message, chat_history=None, retrieved_context=None):
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]

        if retrieved_context:
            context_text = "\n\n".join(retrieved_context)
            messages.append({
                "role": "system",
                "content": (
                    "Use the following retrieved lecture context as the primary source for your answer. "
                    "If the answer is available in the context, base your response on it. "
                    "If the context is insufficient, say that clearly and then provide only a limited general explanation. "
                    "Do not invent lecture-specific details that are not supported by the retrieved context.\n\n"
                    f"{context_text}"
                )
            })

        if chat_history:
            messages.extend(chat_history)

        messages.append({"role": "user", "content": user_message})

        return messages