# utils/gpt/study_guide.py

import os
import sys
from markdown import markdown
from io import BytesIO
from weasyprint import HTML
import re
import subprocess

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
        "Convert all equations and matrices to LaTeX using environments like aligned, bmatrix, or array. Use $...$ for inline math. If the input is messy, do your best to reconstruct the math.\n"
        "Do not use plain text for any math if you can avoid it.\n"
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


def postprocess_matrices(text: str) -> str:
    """Wrap matrix rows in LaTeX environments and remove stray plaintext matrices."""
    lines = text.splitlines()
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect matrix row: at least one & and ends with \\ (or just has & and is followed by another such line)
        if re.match(r"^([\d\w\-+*/^ ]+\s*&\s*)+[\d\w\-+*/^ ]+(\\\\)?$", line.strip()):
            # Start collecting matrix rows
            matrix_rows = []
            while i < len(lines) and re.match(r"^([\d\w\-+*/^ ]+\s*&\s*)+[\d\w\-+*/^ ]+(\\\\)?$", lines[i].strip()):
                matrix_rows.append(lines[i].strip())
                i += 1
            # Wrap in LaTeX environment
            new_lines.append("\\[\n\\begin{bmatrix}")
            new_lines.extend(matrix_rows)
            new_lines.append("\\end{bmatrix}\n\\]")
            # Skip any stray plaintext matrix on the next line (e.g., [102152])
            if i < len(lines) and re.match(r"^\[.*\]$", lines[i].strip()):
                i += 1
            continue
        # Remove stray plaintext matrix after LaTeX
        if re.match(r"^\[.*\]$", line.strip()):
            i += 1
            continue
        new_lines.append(line)
        i += 1
    return "\n".join(new_lines)


def wrap_simple_math(text):
    import re
    # Wrap things like x1 = 3, x2 = -2 in $...$
    # Only wrap if not already inside $...$
    def replacer(match):
        expr = match.group(1)
        # Avoid double-wrapping
        if expr.startswith('$') and expr.endswith('$'):
            return expr
        return f"${expr.strip()}$"
    # This regex matches variable assignments separated by commas or spaces
    pattern = r'((?:[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*-?\d+(?:\.\d+)?(?:,?\s*)?)+)'
    # Only wrap if not already inside $...$
    text = re.sub(pattern, replacer, text)
    return text


def clean_matrices(text):
    import re
    # Remove nested bmatrix environments
    text = re.sub(r'\\end{bmatrix}\s*\\begin{bmatrix}', '', text)
    # Remove stray [ or ] outside LaTeX environments
    text = re.sub(r'(?<!\\)\[', '', text)
    text = re.sub(r'(?<!\\)\]', '', text)
    # Remove double begin/end environments
    text = re.sub(r'(\\begin{bmatrix}\s*)+', r'\\begin{bmatrix}\n', text)
    text = re.sub(r'(\\end{bmatrix}\s*)+', r'\\end{bmatrix}\n', text)
    return text


def preprocess_ocr_text(text: str) -> str:
    import re
    # Remove lines that are mostly non-alphanumeric (garbage)
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        # Remove lines with < 3 alphanumeric chars
        if len(re.findall(r'[a-zA-Z0-9]', line)) < 3:
            continue
        # Remove lines with only symbols or repeated single chars
        if re.fullmatch(r'[^a-zA-Z0-9]+', line):
            continue
        cleaned.append(line)
    # Optionally, collapse multiple blank lines
    text = '\n'.join(cleaned)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def reconstruct_math_latex(ocr_text: str) -> str:
    """
    Use GPT to extract and reconstruct all equations and matrices from messy OCR text as valid LaTeX environments.
    """
    prompt = (
        "The following text contains equations and matrices from handwritten notes, but the math may be in plain text, Unicode, or broken LaTeX.\n"
        "Your task is to extract all mathematical content and rewrite it as valid LaTeX environments (e.g., \\[ ... \\], \\begin{aligned} ... \\end{aligned}, \\begin{bmatrix} ... \\end{bmatrix}).\n"
        "Ignore any broken LaTeX or plain text math and reconstruct the equations as best as possible.\n"
        "Output only the cleaned, valid LaTeX for each equation or matrix, one per block.\n"
        "If you see a system of equations, output it as a single LaTeX block using aligned or array.\n"
        "If you see a matrix, use bmatrix or array.\n"
        "If you see a solution, output it as inline math using $...$.\n"
        "Do not include any text or explanation, only the LaTeX blocks.\n"
        f"\n\nText:\n{ocr_text}"
    )
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip() if response.choices[0].message.content else ""


def generate_study_materials(text: str, level: str, output_type: str, handwritten: bool = False) -> str:
    # Preprocess OCR text before building prompt
    text = preprocess_ocr_text(text)
    print('--- RAW OCR OUTPUT ---')
    print(text)
    # Do NOT call reconstruct_math_latex; just use the original OCR text
    # if handwritten:
    #     text = reconstruct_math_latex(text)
    #     print('--- RECONSTRUCTED LATEX ---')
    #     print(text)
    prompt = build_prompt(level, output_type, text)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # switch to "gpt-3.5-turbo" if you want to save tokens/testing
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.7,
    )
    content = response.choices[0].message.content
    return content.strip() if content else ""


def sanitize_latex(expr: str) -> str:
    # Remove non-ASCII characters (except common math symbols)
    expr = re.sub(r'[^\x00-\x7F]+', '', expr)
    # Remove stray backslashes at the start/end
    expr = re.sub(r'^\\+', '', expr)
    expr = re.sub(r'\\+$', '', expr)
    # Remove double quotes and HTML entities
    expr = expr.replace('&quot;', '').replace('&#x27;', '').replace('"', '').replace("'", '')
    # Remove any leading/trailing whitespace
    expr = expr.strip()
    return expr

def render_latex_with_katex(latex_expr: str, display_mode: bool = False) -> str:
    latex_expr = sanitize_latex(latex_expr)
    if not latex_expr:
        return ""
    try:
        if display_mode:
            latex_expr = f"\\displaystyle {latex_expr}"
        # Path to your katex_renderer.js
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(current_dir))
        katex_path = os.path.join(backend_dir, 'katex_renderer.js')
        result = subprocess.run(
            ['node', katex_path],
            input=latex_expr,
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        stdout = result.stdout
        return stdout.strip() if stdout else ""
    except Exception as e:
        print(f"KaTeX error: {e}")
        return f"<code>{latex_expr}</code>"

def replace_latex_with_svg(html: str) -> str:
    # Replace block math (\[ ... \] or $$ ... $$)
    def block_replacer(match):
        expr = match.group(1) or match.group(2)
        return render_latex_with_katex(expr, display_mode=True)
    html = re.sub(r'\\\[(.*?)\\\]', block_replacer, html, flags=re.DOTALL)
    html = re.sub(r'\$\$(.*?)\$\$', block_replacer, html, flags=re.DOTALL)
    # Replace inline math (\( ... \) or $ ... $)
    def inline_replacer(match):
        expr = match.group(1) or match.group(2)
        return render_latex_with_katex(expr, display_mode=False)
    html = re.sub(r'\\\((.*?)\\\)', inline_replacer, html, flags=re.DOTALL)
    html = re.sub(r'\$(.*?)\$', inline_replacer, html, flags=re.DOTALL)
    return html


def generate_study_materials_as_pdf(text: str, level: str, output_type: str, handwritten: bool = False) -> BytesIO:
    raw_md = generate_study_materials(text, level, output_type, handwritten=handwritten)

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

    # Render LaTeX math to SVG before PDF generation
    html_with_svg = replace_latex_with_svg(full_html)
    pdf_buffer = BytesIO()
    HTML(string=html_with_svg).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer
