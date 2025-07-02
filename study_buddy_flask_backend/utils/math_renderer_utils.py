# utils/math_renderer_utils.py

import subprocess

def render_math_with_katex(latex_code: str, display_mode=False) -> str:
    try:
        if display_mode:
            latex_code = f"\\displaystyle {latex_code}"
        result = subprocess.run(
            ["node", "katex_renderer.js"],
            input=latex_code,
            text=True,
            capture_output=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ KaTeX render failed: {e.stderr}")
        return f"<code>{latex_code}</code>"
