# utils/gpt_utils.py

import os
from io import BytesIO
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_study_materials(text, level, output_type):
    """
    Call OpenAI to generate study material from extracted PDF text.
    """
    prompt = (
        f"Generate a {output_type} for students at the {level} level "
        f"based on the following course material:\n\n{text}\n\n"
        "Be concise, clear, and helpful. Format well."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # You can upgrade to "gpt-4" if needed
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    except OpenAIError as e:
        print(f"❌ OpenAI API error: {e}")
        return "[Error: OpenAI API call failed]"

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return "[Error: Unexpected failure]"

def generate_study_materials_as_pdf(text, level, output_type):
    """
    Generate a study guide using GPT and convert it to a PDF.
    """
    print("🧠 Generating study materials with GPT...")
    result_text = generate_study_materials(text, level, output_type)

    print("📄 Rendering PDF...")
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40
    lines = result_text.split('\n')

    for line in lines:
        if y < 40:
            c.showPage()
            y = height - 40
        c.drawString(40, y, line[:100])  # Wrap if needed
        y -= 14

    c.save()
    buffer.seek(0)
    return buffer
