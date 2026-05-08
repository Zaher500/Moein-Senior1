import re
import json
import logging
from .llm_client import call_hf_llm
import random

logger = logging.getLogger(__name__)


def generate_quiz(text, num_questions, scope=None, question_mode='mixed'):
    # Determine how many MCQ vs True/False questions to generate
    if question_mode == "mcq":
        mcq_count = num_questions
        tf_count = 0
    elif question_mode == "true_false":
        mcq_count = 0
        tf_count = num_questions
    else:  # mixed mode
        # ensure at least 1 question of each type if possible
        if num_questions >= 2:
            mcq_count = random.randint(1, num_questions - 1)
        else:
            mcq_count = 1
        tf_count = num_questions - mcq_count

    # Build the prompt based on question mode
    if question_mode == "mcq":
        prompt = (
            f"Generate {num_questions} Multiple Choice questions only "
            f"based on the provided text.\n\n"
        )
    elif question_mode == "true_false":
        prompt = (
            f"Generate {num_questions} True/False questions only "
            f"based on the provided text.\n\n"
        )
    else:  # mixed mode
        prompt = (
            f"Generate {num_questions} questions "
            f"({mcq_count} Multiple Choice and {tf_count} True/False) "
            f"based on the provided text.\n\n"
        )

    # Add question type restrictions
    if question_mode == "mcq":
        prompt += (
            "IMPORTANT:\n"
            "- Generate only MCQ questions.\n"
            "- Do NOT generate TRUE_FALSE questions.\n\n"
        )
    elif question_mode == "true_false":
        prompt += (
            "IMPORTANT:\n"
            "- Generate only TRUE_FALSE questions.\n"
            "- Do NOT generate MCQ questions.\n\n"
        )
    else:  # mixed mode
        prompt += (
            "IMPORTANT:\n"
            f"- Generate exactly {mcq_count} MCQ questions.\n"
            f"- Generate exactly {tf_count} TRUE_FALSE questions.\n\n"
        )

    # Add scope restriction if provided
    if scope:
        prompt += (
            "IMPORTANT SCOPE RESTRICTION:\n"
            f'- The requested scope is: "{scope}".\n'
            "- Generate questions ONLY from information explicitly present in the provided text that matches this scope.\n"
            "- Do NOT use any external knowledge.\n"
            "- Do NOT invent facts or concepts not mentioned in the text.\n"
            "- If the requested scope is not covered in the text, return an empty JSON array [].\n"
            "- If the scope is only partially covered, generate questions only from the covered parts.\n\n"
        )

    # Add MCQ format instructions
    if question_mode == "mcq":
        prompt += (
            "IMPORTANT MCQ FORMAT:\n"
            "- Each MCQ must have exactly 4 meaningful full-text answer options.\n"
            "- Do NOT use placeholder options like A, B, C, D.\n"
            "- Do NOT make correct_answer a letter.\n"
            "- correct_answer must exactly equal one full option text.\n\n"
        )
    elif question_mode == "mixed":
        prompt += (
            "IMPORTANT MCQ FORMAT:\n"
            "- For every MCQ question, provide exactly 4 meaningful full-text answer options.\n"
            "- Do NOT use placeholder options like A, B, C, D.\n"
            "- For MCQ, correct_answer must exactly equal one full option text.\n\n"
        )

    prompt += f"Text:\n{text}\n\n"

    prompt += (
        "Output MUST be exactly a JSON array of objects with the following schema. "
        "Do NOT wrap it in markdown block quotes (like ```json).\n"
        "[\n"
        "  {\n"
        '    "question_type": "MCQ" or "TRUE_FALSE",\n'
        '    "question_text": "...",\n'
        '    "options": "full option text 1|full option text 2|full option text 3|full option text 4", '
        '(For MCQ, provide exactly 4 full answer options separated by |. Do NOT use only letters like A, B, C, D. Leave as empty string for TRUE_FALSE.),\n'
        '    "correct_answer": "...", '
        '(For MCQ, this must exactly match one full option text, not a letter. For TRUE_FALSE, it must be "True" or "False".),\n'
        '    "explanation": "..."\n'
        "  }\n"
        "]"
    )

    raw_response = call_hf_llm(prompt)

    # Clean up the response
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

                # Skip if options are just placeholders
                if all(opt in {"A", "B", "C", "D"} for opt in options):
                    logger.warning(f"Skipping placeholder MCQ options: {item}")
                    continue

                # Validate MCQ has 4 options and correct answer is one of them
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