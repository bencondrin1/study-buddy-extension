# utils/gpt_utils.py
import openai
import os
from dotenv import load_dotenv

# Load environment variables (your OpenAI API key should be in .env as OPENAI_API_KEY)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_study_materials(text, level, output_type):
    # Truncate text to stay within token limits
    truncated = text[:2000]

    prompt = f"""You're an expert tutor. Create a {output_type} at a {level} level for the following text:

{truncated}

Return only the final output, no explanations."""

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    except openai.error.OpenAIError as e:
        print(f"❌ OpenAI API error: {e}")
        return "[Error generating content]"
