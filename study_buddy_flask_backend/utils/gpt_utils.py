import os
import re
import subprocess
from io import BytesIO
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from weasyprint import HTML
from markdown import markdown

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Math rendering ===

def render_latex_with_katex(latex_expr, display_mode=False):
    try:
        if display_mode:
            latex_expr = f"\\displaystyle {latex_expr}"

        result = subprocess.run(
            ['node', 'katex_renderer.js'],
            input=latex_expr,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ KaTeX error: {e.stderr}")
        return f"<code>{latex_expr}</code>"

def render_math_in_html(text):
    """
    Replace LaTeX math expressions in the text with rendered KaTeX HTML.
    Handles both inline \( ... \) and display \[ ... \].
    """

    def replace_block(match):
        latex = match.group(1).strip()
        return f"<div style='margin: 1em 0'>{render_latex_with_katex(latex, display_mode=True)}</div>"

    def replace_inline(match):
        latex = match.group(1).strip()
        return render_latex_with_katex(latex, display_mode=False)

    # Block math first
    text = re.sub(r'\\\[(.+?)\\\]', replace_block, text, flags=re.DOTALL)
    # Then inline math
    text = re.sub(r'\\\((.+?)\\\)', replace_inline, text, flags=re.DOTALL)

    return text

# === OpenAI Completion ===

def generate_study_materials(text, level, output_type):
    prompt = (
        f"Generate a clear, accurate {output_type} at a {level} level using the following notes:\n\n{text}\n\n"
        "Use LaTeX for any math, and format examples. For each example, solve it if not already solved. "
        "Wrap your own completions inside [[GPT:...]] so I can highlight them."
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

def highlight_gpt_insertions(html):
    return re.sub(
        r"\[\[GPT:(.+?)\]\]",
        r"<span style='color: red;'>\1</span>",
        html
    )

# === Final PDF Formatter ===

def get_title_from_text(text):
    for line in text.strip().splitlines():
        if line.strip():
            return line.strip()[:60]
    return "Study Guide"

def generate_study_materials_as_pdf(text, level, output_type):
    print("🧠 Generating GPT content...")
    raw_md = generate_study_materials(text, level, output_type)

    print("🔬 Rendering math to KaTeX...")
    rendered_md = render_math_in_html(raw_md)

    print("🎨 Converting Markdown to HTML...")
    html_body = markdown(rendered_md.replace("\n", "\n\n"))
    html_body = highlight_gpt_insertions(html_body)

    title = f"{get_title_from_text(text)} — {output_type} ({level})"
    full_html = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <title>{title}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
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
                margin-bottom: 1em;
            }}
            h2, h3 {{
                color: #2a6ebd;
                margin-top: 1em;
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
            span.katex {{
                font-size: 1.05em;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        {html_body}
    </body>
    </html>
    """

    print("📄 Writing PDF...")
    pdf_buffer = BytesIO()
    HTML(string=full_html).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

def generate_flashcards(text, level="Basic"):
    """
    Sends a request to OpenAI to generate flashcards from input text.
    """
    prompt = (
        f"Generate flashcards at the {level} level based on the following content.\n\n"
        f"Format the output as Q: <question>\nA: <answer>, one flashcard per block.\n\n"
        f"Text:\n{text}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    except OpenAIError as e:
        print(f"❌ OpenAI API error: {e}")
        return "[Error: OpenAI API call failed]"

def parse_flashcards(raw_text):
    """
    Converts raw GPT response into a list of (question, answer) tuples.
    """
    cards = []
    current_q, current_a = None, None

    for line in raw_text.splitlines():
        line = line.strip()
        if line.startswith("Q:"):
            current_q = line[2:].strip()
        elif line.startswith("A:"):
            current_a = line[2:].strip()
            if current_q and current_a:
                cards.append((current_q, current_a))
                current_q, current_a = None, None

    return cards