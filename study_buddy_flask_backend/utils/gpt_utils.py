# utils/gpt_utils.py
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_study_materials(text, level, output_type):
    truncated = text[:2000]  # Avoid hitting token limits

    prompt = f"""You're an expert tutor. Create a {output_type} at a {level} level for the following text:

    {truncated}

    Return only the final output, no explanations."""

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
