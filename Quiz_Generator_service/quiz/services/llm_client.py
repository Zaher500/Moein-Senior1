import os
from openai import OpenAI

def call_hf_llm(prompt, temperature=0.9):
    hf_token = os.getenv('HF_TOKEN')
    hf_model = os.getenv('HF_MODEL')
    
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=hf_token
    )
    
    response = client.chat.completions.create(
        model=hf_model,
        messages=[
            {"role": "system", "content": "You are a helpful AI that strictly follows instructions to generate educational quizzes in valid JSON format."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )
    
    return response.choices[0].message.content
