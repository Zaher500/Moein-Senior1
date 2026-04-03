class PromptBuilder:
    SYSTEM_PROMPT = (
        "You are Moein, an AI academic student assistant. "
        "Help students understand topics clearly and accurately. "
        "Give concise, educational, and well-structured answers. "
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
                "content": f"Use this retrieved context when relevant:\n\n{context_text}"
            })

        if chat_history:
            messages.extend(chat_history)

        messages.append({"role": "user", "content": user_message})

        return messages