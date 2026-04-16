import re
import json
import logging
from .llm_client import call_hf_llm

logger = logging.getLogger(__name__)


def generate_quiz(text, num_questions, scope=None):
    mcq_count = int(num_questions * 0.6)
    tf_count = num_questions - mcq_count

    prompt = (
        f"Generate {num_questions} questions "
        f"({mcq_count} Multiple Choice and {tf_count} True/False) "
        f"based on the provided text.\n\n"
    )

    if scope:
        prompt += (
            "IMPORTANT INSTRUCTION:\n"
            f"- Generate questions ONLY from this scope/topic: {scope}\n"
            "- Do NOT generate questions from unrelated parts of the text\n"
            "- If the scope is partially covered, generate the closest relevant questions only\n\n"
        )

    prompt += f"Text:\n{text}\n\n"

    prompt += (
        "Output MUST be exactly a JSON array of objects with the following schema. "
        "Do NOT wrap it in markdown block quotes (like ```json).\n"
        "[\n"
        "  {\n"
        '    "question_type": "MCQ" or "TRUE_FALSE",\n'
        '    "question_text": "...",\n'
        '    "options": "A|B|C|D", '
        '(Provide exactly 4 pipe-separated options for MCQ. Leave as empty string for TRUE_FALSE.),\n'
        '    "correct_answer": "...", '
        '(Must match one of your options EXACTLY for MCQ, or be "True"/"False" for TRUE_FALSE.),\n'
        '    "explanation": "..."\n'
        "  }\n"
        "]"
    )

    raw_response = call_hf_llm(prompt)

    cleaned_response = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL).strip()

    if cleaned_response.startswith('```json'):
        cleaned_response = cleaned_response[7:]
    if cleaned_response.startswith('```'):
        cleaned_response = cleaned_response[3:]
    if cleaned_response.endswith('```'):
        cleaned_response = cleaned_response[:-3]

    cleaned_response = cleaned_response.strip()

    try:
        parsed_data = json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        return raw_response, []

    valid_questions = []

    for item in parsed_data:
        try:
            q_type = item.get("question_type")

            if q_type == "MCQ":
                options = [opt.strip() for opt in item.get("options", "").split("|")]
                correct_answer = str(item.get("correct_answer", "")).strip()

                if len(options) == 4 and correct_answer in options:
                    item["options"] = "|".join(options)
                    item["correct_answer"] = correct_answer
                    valid_questions.append(item)
                else:
                    logger.warning(f"Skipping malformed MCQ: {item}")

            elif q_type == "TRUE_FALSE":
                ans = str(item.get("correct_answer", "")).strip()
                if ans.lower() in ["true", "false"]:
                    item["correct_answer"] = "True" if ans.lower() == "true" else "False"
                    valid_questions.append(item)
                else:
                    logger.warning(f"Skipping malformed TRUE_FALSE: {item}")

        except Exception as e:
            logger.warning(f"Error validating question: {item}. Error: {e}")

    return raw_response, valid_questions