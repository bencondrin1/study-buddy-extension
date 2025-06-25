import os
from io import BytesIO
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from weasyprint import HTML
from markdown import markdown

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_study_materials(text, level, output_type):
    """
    Generate study material text from GPT.
    """
    prompt = (
        f"Generate a well-formatted {output_type} for students at the {level} level "
        f"based on the following course material:\n\n{text}\n\n"
        f"Include headings, bullet points, math where needed, and make it clear and organized."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
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
    Generate a study guide using GPT, convert to styled HTML, and return PDF BytesIO.
    """
    print("🧠 Generating study materials with GPT...")
    html_content = generate_study_materials(text, level, output_type)

    print("🎨 Formatting HTML...")
    html_body = markdown(html_content.replace("\n", "\n\n"))
    title = f"{get_title_from_text(text)} — {output_type} ({level})"

    full_html = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <title>{title}</title>
        <style>
            body {{
                font-family: 'Georgia', serif;
                margin: 2em;
                line-height: 1.6;
                color: #222;
            }}
            h1 {{
                font-size: 24px;
                text-align: center;
                margin-bottom: 0.5em;
            }}
            h2, h3 {{
                margin-top: 1em;
                color: #2a6ebd;
            }}
            ul {{
                margin-left: 1.5em;
                list-style-type: disc;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 4px;
                border-radius: 4px;
                font-family: monospace;
            }}
            pre {{
                background-color: #f9f9f9;
                padding: 1em;
                border-radius: 5px;
                overflow-x: auto;
            }}
            hr {{
                margin: 2em 0;
                border: none;
                border-top: 1px solid #ccc;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        {html_body}
    </body>
    </html>
    """

    print("📄 Rendering PDF...")
    pdf_buffer = BytesIO()
    HTML(string=full_html).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

def get_title_from_text(text):
    """
    Try to extract a short title or first heading from the input text.
    """
    lines = text.strip().splitlines()
    for line in lines:
        if line.strip():
            return line.strip()[:60]
    return "Study Material"
