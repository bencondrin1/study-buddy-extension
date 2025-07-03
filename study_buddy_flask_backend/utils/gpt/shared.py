import os
import re
import subprocess
from dotenv import load_dotenv
from openai import OpenAI
from io import BytesIO


load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
client = OpenAI(api_key=api_key)

def render_latex_with_katex(latex_expr, display_mode=False):
    try:
        if display_mode:
            latex_expr = f"\\displaystyle {latex_expr}"
        
        # Get the directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to the study_buddy_flask_backend directory
        backend_dir = os.path.dirname(os.path.dirname(current_dir))
        katex_path = os.path.join(backend_dir, 'katex_renderer.js')
        
        result = subprocess.run(
            ['node', katex_path],
            input=latex_expr,
            capture_output=True,
            text=True,
            check=True
        )
        stdout = result.stdout
        return stdout.strip() if stdout else ""
    except subprocess.CalledProcessError as e:
        print(f"❌ KaTeX error: {e.stderr}")
        return f"<code>{latex_expr}</code>"

def render_math_in_html(text: str) -> str:
    """
    Finds LaTeX math blocks in text and replaces them with KaTeX-rendered HTML.
    Supports inline \( ... \), display \[ ... \], and $$ ... $$.
    """
    patterns = [
        (r"\\\[(.+?)\\\]", True),
        (r"\\\((.+?)\\\)", False),
        (r"\$\$(.+?)\$\$", True),
        (r"\$([^$\n]+?)\$", False),  # Inline math with single dollar signs
    ]

    for pattern, display_mode in patterns:
        def replacer(match):
            group = match.group(1)
            if group is None:
                return ""
            latex_code = group.strip()
            return render_latex_with_katex(latex_code, display_mode=display_mode)

        text = re.sub(pattern, replacer, text, flags=re.DOTALL)

    return text


def highlight_gpt_insertions(html: str) -> str:
    return re.sub(r"\[\[GPT:(.+?)\]\]", r"<span style='color: red;'>\1</span>", html)

def get_title_from_text(text: str) -> str:
    if not text:
        return "Study Guide"
    text_stripped = text.strip()
    for line in text_stripped.splitlines():
        if line and line.strip():
            return line.strip()[:60]
    return "Study Guide"

def fallback_extract_text(pdf_bytes, extract_pdf_func, ocr_func):
    """
    Tries to extract text from PDF bytes using the standard method.
    If no text or error, falls back to OCR.
    """
    try:
        text = extract_pdf_func(BytesIO(pdf_bytes))
        if text and text.strip():
            return text
        else:
            print("🔍 No extractable text found with PDF parser. Using OCR fallback...")
            return ocr_func(pdf_bytes)
    except Exception as e:
        print(f"❌ Exception in fallback_extract_text: {e}")
        return ocr_func(pdf_bytes)
