import os
import re
import subprocess
from typing import Callable
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils', '.env'))
from openai import OpenAI
from io import BytesIO


# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
client = OpenAI(api_key=api_key)

def render_latex_with_katex(latex_expr: str, display_mode: bool = False) -> str:
    if not latex_expr:
        return ""
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
            check=True,
            timeout=10  # Add timeout to prevent hanging
        )
        stdout = result.stdout
        return stdout.strip() if stdout else ""
    except subprocess.CalledProcessError as e:
        print(f"❌ KaTeX error: {e.stderr}")
        return f"<code>{latex_expr}</code>"
    except subprocess.TimeoutExpired:
        print(f"❌ KaTeX timeout for: {latex_expr}")
        return f"<code>{latex_expr}</code>"
    except Exception as e:
        print(f"❌ Unexpected KaTeX error: {e}")
        return f"<code>{latex_expr}</code>"
    finally:
        # Force garbage collection
        import gc
        gc.collect()

def render_math_in_html(text: str) -> str:
    """
    Finds LaTeX math blocks in text and replaces them with KaTeX-rendered HTML.
    Supports inline \\( ... \\), display \\[ ... \\], and $$ ... $$.
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

def generate_ai_title(text: str, content_type: str = "study material") -> str:
    """
    Generates an AI-powered title based on the content.
    """
    if not text or len(text.strip()) < 10:
        return f"{content_type.title()}"
    
    try:
        # Take first 500 characters for context
        context = text[:500].strip()
        
        prompt = f"""Based on the following content, generate a concise, descriptive title (max 60 characters) for a {content_type}.
        
        Content preview:
        {context}
        
        Generate only the title, nothing else. Make it specific and informative."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.3,
        )
        
        title = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
        # Clean up the title
        title = re.sub(r'["\']', '', title)  # Remove quotes
        title = title[:60]  # Limit to 60 characters
        
        return title if title else f"{content_type.title()}"
        
    except Exception as e:
        print(f"❌ Error generating AI title: {e}")
        return get_title_from_text(text)

def get_title_from_text(text: str) -> str:
    """
    Gets a title from text, with AI enhancement when possible.
    """
    if not text:
        return "Study Guide"
    
    # Try AI generation first
    try:
        return generate_ai_title(text, "study material")
    except:
        # Fallback to simple extraction
        text_stripped = text.strip()
        for line in text_stripped.splitlines():
            if line and line.strip():
                return line.strip()[:60]
        return "Study Guide"

def fallback_extract_text(pdf_bytes: bytes, extract_pdf_func: Callable, ocr_func: Callable) -> str:
    """
    Tries to extract text from PDF bytes using the standard method.
    If no text or error, falls back to OCR.
    """
    if not pdf_bytes:
        return ocr_func(pdf_bytes)
    
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
