class PromptBuilder:
    SYSTEM_PROMPT = (
        "You are Moein, an AI academic student assistant. "
        "Answer the student's questions ONLY using information supported by the retrieved lecture context. "
        "Do not use your general knowledge to answer academic questions. "
        "If the retrieved context does not contain enough information to answer the question, "
        'respond clearly that the requested information is not available in the provided course content. '
        "Do not guess, infer unsupported facts, or invent information. "
        "Chat history may be used only to understand the conversation, not as a source of factual information. "
        "Give concise, educational, and well-structured answers. "
        "Keep responses brief by default unless the user asks for more detail."
    )

    def build_messages(
        self,
        user_message,
        chat_history=None,
        retrieved_context=None
    ):
        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT
            }
        ]

        if retrieved_context:
            context_text = "\n\n".join(retrieved_context)

            messages.append({
                "role": "system",
                "content": (
                    "The following is the retrieved course content relevant to the student's question. "
                    "Treat it as the only factual source for answering the question. "
                    "Answer only if the information is supported by this context. "
                    "If the context does not contain enough information, state that the information "
                    "is not available in the provided course content.\n\n"
                    "RETRIEVED COURSE CONTENT:\n"
                    f"{context_text}"
                )
            })
        else:
            messages.append({
                "role": "system",
                "content": (
                    "No relevant course content was retrieved for this question. "
                    "Do not answer using general knowledge. "
                    "Tell the student that the requested information is not available "
                    "in the provided course content."
                )
            })

        if chat_history:
            messages.extend(chat_history)

        messages.append({
            "role": "user",
            "content": user_message
        })

        return messages