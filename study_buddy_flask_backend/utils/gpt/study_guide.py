# utils/gpt/study_guide.py

import os
import sys
from markdown import markdown
from io import BytesIO
from weasyprint import HTML

# Add the parent directory to the Python path so we can import utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.gpt.shared import client, render_math_in_html, highlight_gpt_insertions, get_title_from_text

def build_prompt(level: str, output_type: str, text: str) -> str:
    level = level.lower()
    intro = f"Generate a comprehensive {output_type.lower()} using the following notes.\n\n"

    base = (
        "Use LaTeX for all math equations.\n"
        "Clearly identify key concepts and structure the content with headers.\n"
        "IMPORTANT: When you encounter examples or problems, you MUST solve them completely step-by-step. Do NOT write placeholder text like 'Detailed solution here' or 'Solve this problem'. Actually work through the entire solution.\n"
        "For any content you generate (explanations, solutions, examples), mark it with [[GPT:...]] so it can be highlighted.\n"
    )

    if level == "basic":
        guidance = (
            "Explain concepts simply and briefly. Avoid jargon.\n"
            "Do NOT include detailed example solutions; only provide high-level summaries.\n"
        )
    else:  # In-Depth
        guidance = (
            "You MUST provide complete, detailed solutions for ALL examples and problems.\n"
            "Show every step of calculations, derivations, and reasoning.\n"
            "Include step-by-step explanations for how you arrive at each answer.\n"
            "Do NOT skip steps or write placeholder text - provide the full working solution.\n"
            "Include additional related concepts or background if helpful.\n"
            "Ensure everything is clearly structured and math is in LaTeX.\n"
        )

    return intro + base + guidance + "\n\nNotes:\n" + text


def generate_study_materials(text: str, level: str, output_type: str) -> str:
    prompt = build_prompt(level, output_type, text)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # switch to "gpt-3.5-turbo" if you want to save tokens/testing
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.7,
    )
    content = response.choices[0].message.content
    return content.strip() if content else ""


def generate_study_materials_as_pdf(text: str, level: str, output_type: str) -> BytesIO:
    raw_md = generate_study_materials(text, level, output_type)

    # Detect if math is present to render with KaTeX
    if any(tag in raw_md for tag in ["\\[", "\\(", "$$"]):
        rendered_md = render_math_in_html(raw_md)
    else:
        rendered_md = raw_md

    # Markdown to HTML conversion with double line breaks for better spacing
    html_body = markdown(rendered_md.replace("\n", "\n\n"))

    # Highlight GPT completions
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
            /* Highlight GPT insertions in red */
            span.gpt-insertion {{
                color: red;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        {html_body}
    </body>
    </html>
    """

    pdf_buffer = BytesIO()
    HTML(string=full_html).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer
