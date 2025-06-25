import os
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_study_materials(text, level, output_type):
    prompt = (
        f"Please generate a {output_type} at {level} level based on the following text:\n\n"
        f"{text}\n\n"
        f"Output only the study material."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-3.5-turbo" if you prefer
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
        )
        # Extract the text content of the first completion choice
        result_text = response.choices[0].message.content.strip()
        return result_text

    except OpenAIError as e:
        print(f"❌ OpenAI API error: {e}")
        return "[Error generating study materials: API call failed]"

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return "[Error generating study materials: unexpected failure]"
