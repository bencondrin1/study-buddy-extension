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

def generate_study_materials(text, level, output_type):
    base_prompt = (
        f"Generate a well-organized, visually clean, and easy-to-read {output_type} "
        f"at the {level} level based on the following course material:\n\n{text}\n\n"
        "Use clear formatting, bullet points, math notation in LaTeX (e.g. \\frac, \\int), and include examples when helpful."
    )

    if level.lower() == "in-depth":
        base_prompt += (
            "\n\nIf you see any unsolved or partial math examples, do your best to solve and complete them."
            " Show your work. Render your answer in LaTeX format and highlight your completions in red."
        )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": base_prompt}],
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

def render_latex_math(latex_expr):
    try:
        result = subprocess.run(
            ['katex', '--no-throw-on-error'],
            input=latex_expr,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ KaTeX error: {e.stderr}")
        return f"<code>{latex_expr}</code>"

def render_math_in_markdown(md_text):
    # Render \[ ... \] block math first
    def block_repl(match):
        latex = match.group(1).strip()
        return f"<div style='margin:1em 0'>{render_latex_math(latex)}</div>"

    # Then render \( ... \) inline math
    def inline_repl(match):
        latex = match.group(1).strip()
        return render_latex_math(latex)

    md_text = re.sub(r'\\\[(.+?)\\\]', block_repl, md_text, flags=re.DOTALL)
    md_text = re.sub(r'\\\((.+?)\\\)', inline_repl, md_text, flags=re.DOTALL)
    return md_text

def highlight_gpt_completions(html):
    return re.sub(
        r'\[\[GPT:(.+?)\]\]',  # e.g., [[GPT:completion]]
        r'<span style="color: red;">\1</span>',
        html
    )

def generate_study_materials_as_pdf(text, level, output_type):
    print("🧠 Generating study materials with GPT...")
    content_md = generate_study_materials(text, level, output_type)

    # Pre-process GPT completions (e.g., added answers marked by [[GPT:...]])
    content_md = content_md.replace("**[GPT]**", "[[GPT:")  # in case GPT uses fallback markers
    content_md = content_md.replace("**[GPT]:**", "[[GPT:")  # normalize
    content_md = content_md.replace("**[GPT Completion]:**", "[[GPT:")
    content_md = content_md.replace("]]", "]]")  # ensure closure

    print("🔬 Rendering math with KaTeX...")
    content_md = render_math_in_markdown(content_md)

    print("🎨 Converting markdown to HTML...")
    html_body = markdown(content_md.replace("\n", "\n\n"))
    html_body = highlight_gpt_completions(html_body)

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

    print("📄 Rendering PDF...")
    pdf_buffer = BytesIO()
    HTML(string=full_html).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

def get_title_from_text(text):
    for line in text.strip().splitlines():
        if line.strip():
            return line.strip()[:60]
    return "Study Material"
