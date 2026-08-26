from huggingface_hub import InferenceClient
import os


# =========================================================
# Hugging Face Client
# =========================================================

HF_API_KEY = os.getenv("HF_API_KEY")

if not HF_API_KEY:
    raise RuntimeError("HF_API_KEY is not set in environment variables")

client = InferenceClient(
    model="Qwen/Qwen3-30B-A3B-Instruct-2507",
    token=HF_API_KEY
)


# =========================================================
# Prompt Template
# =========================================================

PROMPT_TEMPLATE = """
You are an expert academic assistant.

Summarize the following lecture text clearly and accurately.

Rules:
- Detect the dominant language of the lecture text.
- Write the summary in the dominant language.
- Preserve proper nouns, names, and institutions in their original language
  (for example: university names, system names, technical terms).
- If the text contains both Arabic and English:
  - Do NOT translate proper nouns.
  - Do NOT switch languages unless the content itself requires it.
- Do not invent information.
- Be concise and well-structured.
- Do not omit examples, steps, or workshop instructions.
Lecture text:
\"\"\"
{TEXT}
\"\"\"
"""


# =========================================================
# Summarization Function (CHAT API)
# =========================================================

def summarize_text(text: str, max_new_tokens: int = 450) -> str:
    """
    Summarize a chunk of lecture text using Hugging Face Inference API
    (Conversational / Chat-based model).

    Args:
        text (str): Lecture text chunk
        max_new_tokens (int): Maximum tokens for generated summary

    Returns:
        str: Summary text
    """

    text = text.strip()

    if not text:
        return ""

    prompt = PROMPT_TEMPLATE.replace("{TEXT}", text)

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert academic assistant. "
                        "Summarize lecture text accurately and concisely."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=max_new_tokens,
            temperature=0.3,
            top_p=0.9,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        # Important: do NOT crash the consumer
        print("❌ Hugging Face summarization error:", str(e))
        return ""