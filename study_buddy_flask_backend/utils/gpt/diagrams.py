# utils/gpt/diagrams.py

import re
import base64
import subprocess
import tempfile
import os
import sys
from io import BytesIO
from weasyprint import HTML
import cairosvg
import random
from PIL import Image  # Added for PNG resizing

# Add the parent directory to the Python path so we can import utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.gpt.shared import client, generate_ai_title

def build_diagram_prompt(level: str, text: str, diagram_type: str = "general") -> str:
    """Build a prompt for generating diagrams from text content."""
    level = level.lower()
    
    intro = "Generate visual diagrams to represent the key concepts and relationships in the following notes.\n\n"
    
    base = (
        "Create clear, educational diagrams that help visualize the concepts.\n"
        "Use Mermaid.js syntax for all diagrams.\n"
        "Focus on creating diagrams that show relationships, processes, hierarchies, or flows.\n"
        "Each diagram should have a clear title and purpose.\n"
        "Create diagrams that help with understanding and memorization.\n"
        "Even simple concepts can benefit from visual representation.\n"
        "Use simple, clean syntax that is compatible with Mermaid.js parser.\n"
        "\n"
        "***IMPORTANT:***\n"
        "- Do NOT use any mathematical symbols, formulas, LaTeX, or special characters in node labels or diagram text.\n"
        "- Use only plain English words and phrases for all node labels and diagram text.\n"
        "- Do NOT use any of the following in node labels: ∫, ∑, ∏, √, ≤, ≥, ±, ×, ÷, ∂, ∇, ∆, ∈, ∉, ∋, ∩, ∪, ⊂, ⊃, ⊆, ⊇, ⊕, ⊗, ∀, ∃, ∄, ∴, ∵, ∝, ∞, θ, α, β, γ, δ, ε, ζ, η, θ, ι, κ, λ, μ, ν, ξ, ο, π, ρ, σ, τ, υ, φ, χ, ψ, ω, ^, _, /, |, <, >, =, +, -, (, ), [, ], {, }, or any LaTeX or math notation.\n"
        "- Do NOT use LaTeX, math notation, or formulas in any part of the diagram.\n"
        "- If you need to refer to a mathematical concept, use a descriptive English phrase (e.g., 'Definite Integral', 'Error Bound', 'Step Size', 'Polynomial Approximation').\n"
        "\n"
        "Examples of GOOD node labels: 'Integration', 'Trapezoidal Rule', 'Simpson Rule', 'Error Term', 'Function', 'Polynomial', 'Step Size', 'Approximation', 'Numerical Method', 'Process', 'Input', 'Output'\n"
        "Examples of BAD node labels: '∫f(x)dx', 'Zbaf(x)dx', 'f(n+1)(ξ)', 'Trapezoidal rule - Precision 1', 'Pn(x)', 'f(x)', 'h = (b-a)/n', 'S = (h/3)[f(x₀) + ...]', '$x^2$', '\\int_a^b f(x)dx', 'Error ≤ (b-a)³M₂/(12n²)'\n"
        "\n"
        "If you are unsure, always use plain English and avoid any math notation.\n"
    )
    
    # Add specific guidance based on diagram type
    if diagram_type == "flowchart":
        base += (
            "Focus on creating flowcharts that show processes, decision flows, and step-by-step procedures.\n"
            "Use flowchart syntax: graph TD for top-down, graph LR for left-right, graph BT for bottom-up.\n"
            "Include decision points with diamond shapes (e.g., B{Decision}), process steps with rectangles (A[Step]), and circles (C((Circle))).\n"
            "Vary node shapes for visual interest.\n"
        )
    elif diagram_type == "mindmap":
        base += (
            "Focus on creating mind maps that organize concepts hierarchically.\n"
            "Use mindmap syntax: mindmap with central concept and branching subtopics.\n"
            "Show relationships between main ideas and supporting concepts.\n"
        )
    elif diagram_type == "sequence":
        base += (
            "Focus on creating sequence diagrams that show interactions and timelines.\n"
            "Use sequence diagram syntax: sequenceDiagram with participants and messages.\n"
            "Show the flow of information or processes over time.\n"
        )
    elif diagram_type == "relationship":
        base += (
            "Focus on creating relationship diagrams that show connections between entities.\n"
            "Use entity relationship or class diagram syntax: erDiagram or classDiagram.\n"
            "Show how different concepts, objects, or entities relate to each other.\n"
            "For class diagrams, use clear, simple syntax and avoid complex annotations.\n"
            "Keep relationships simple and readable.\n"
            "IMPORTANT: Avoid using notes, complex annotations, or special characters in class diagrams.\n"
            "Use only basic class diagram syntax: class definitions, attributes, methods, and simple relationships.\n"
            "Do NOT use notes, complex labels, or mathematical symbols in relationships.\n"
        )
    else:  # general
        base += (
            "Use appropriate diagram types:\n"
            "- flowcharts for processes and decision flows\n"
            "- sequence diagrams for interactions and timelines\n"
            "- class diagrams for relationships and structures\n"
            "- mind maps for concept organization\n"
            "- entity relationship diagrams for data structures\n"
        )
    
    if level == "basic":
        guidance = (
            "Create simple, easy-to-understand diagrams.\n"
            "Focus on the most important concepts only.\n"
            "Use clear, descriptive labels.\n"
            "Limit complexity - aim for 3-5 main elements per diagram.\n"
            "Always use 'graph TD' for a top-down flowchart.\n"
            "Vary node shapes: use rectangles (A[Step]), circles (B((Circle))), and diamonds (C{Decision}).\n"
            "Do NOT use mindmaps or sequence diagrams for basic diagrams.\n"
        )
    else:  # In-Depth
        guidance = (
            "Create comprehensive, detailed diagrams.\n"
            "Include all relevant relationships and connections.\n"
            "Show detailed processes and sub-steps.\n"
            "Include additional context and background information.\n"
            "Use more sophisticated diagram structures when appropriate.\n"
            "Vary node shapes for visual interest.\n"
        )
    
    format_instructions = (
        "\n\nFormat your response as follows:\n"
        "For each diagram, provide:\n"
        "1. A descriptive title\n"
        "2. A brief explanation of what the diagram shows\n"
        "3. The Mermaid.js code block\n\n"
        "Example format:\n"
        "## [Diagram Title]\n"
        "[Brief explanation]\n"
        "```mermaid\n"
        "graph TD\n"
        "A[Start] --> B{Decision}\n"
        "B --> C((Circle))\n"
        "C --> D[End]\n"
        "```\n\n"
        "IMPORTANT: Generate 1-2 diagrams that best represent the key concepts.\n"
        "Focus on creating diagrams that show relationships, processes, or hierarchies.\n"
        "Even simple concepts can benefit from visual representation.\n"
        "If the content is very basic, create a simple flowchart.\n"
        "Each diagram should help with understanding and memorization.\n"
    )
    
    return intro + base + guidance + format_instructions + "\n\nNotes:\n" + text

def generate_diagrams(text: str, level: str, diagram_type: str = "general") -> str:
    """Generate diagrams from text content using GPT."""
    prompt = build_diagram_prompt(level, text, diagram_type)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000,
        temperature=0.7,
    )
    content = response.choices[0].message.content
    result = content.strip() if content else ""
    return result

def clean_mermaid_code(mermaid_code: str) -> str:
    """Clean Mermaid code to remove problematic syntax, aggressively sanitize node labels, and enforce valid structure."""
    # Remove problematic note syntax that causes parsing errors
    mermaid_code = re.sub(r'note\s+(?:right|left|top|bottom)\s+of\s+[^:]+:\s*[^\n]+', '', mermaid_code)
    # Remove complex relationship labels with special characters
    mermaid_code = re.sub(r'"[^"]*[^\w\s][^"]*"\s*--\s*"[^"]*[^\w\s][^"]*"', '', mermaid_code)
    lines = mermaid_code.split('\n')
    cleaned_lines = []
    removed_nodes = set()
    node_counter = 1
    for i, line in enumerate(lines):
        # Aggressively replace node labels with non-alphanumeric chars (except spaces)
        node_label_pattern = re.compile(r'(\w+)\[([^\]]+)\]')
        def replace_label(match):
            label = match.group(2)
            if re.search(r'[^a-zA-Z0-9 ]', label):
                nonlocal node_counter
                new_label = f'Concept {node_counter}'
                node_counter += 1
                return f'{match.group(1)}[{new_label}]'
            return match.group(0)
        line = node_label_pattern.sub(replace_label, line)
        # Remove lines with complex annotations, notes, or special characters
        if any(skip_pattern in line.lower() for skip_pattern in ['note ', 'ξ', '′′', '′′′′', 'f′′', 'f′′′′']):
            node_match = re.search(r'^(\w+)\[', line)
            if node_match:
                removed_nodes.add(node_match.group(1))
            continue
        if re.search(r'[∫∑∏√∞≠≤≥±×÷∂∇∆∈∉∋∌∩∪⊂⊃⊆⊇⊕⊗∀∃∄∴∵∝∞θαβγδεζηθικλμνξοπρστυφχψω]', line):
            node_match = re.search(r'^(\w+)\[', line)
            if node_match:
                removed_nodes.add(node_match.group(1))
            continue
        if re.search(r'f\([^)]*\)[^)]*\([^)]*\)', line) or re.search(r'[a-z]\([^)]*[^a-zA-Z0-9\s][^)]*\)[^)]*\([^)]*\)', line):
            node_match = re.search(r'^(\w+)\[', line)
            if node_match:
                removed_nodes.add(node_match.group(1))
            continue
        cleaned_lines.append(line)
    # Structural validation: only keep valid Mermaid lines
    valid_lines = []
    header_pattern = re.compile(r'^(graph|flowchart)\s+(TD|LR|BT|RL)?', re.IGNORECASE)
    node_pattern = re.compile(r'^[A-Za-z0-9_]+\[[^\]]+\]$')
    edge_pattern = re.compile(r'^[A-Za-z0-9_]+\s*--[->|o]?\s*[A-Za-z0-9_]+(\[[^\]]+\])?$')
    comment_pattern = re.compile(r'^%%')
    for line in cleaned_lines:
        line = line.strip()
        if not line:
            valid_lines.append(line)
            continue
        if header_pattern.match(line):
            valid_lines.append(line)
            continue
        if node_pattern.match(line):
            valid_lines.append(line)
            continue
        if edge_pattern.match(line):
            valid_lines.append(line)
            continue
        if comment_pattern.match(line):
            valid_lines.append(line)
            continue
        # If line does not match any valid pattern, skip it
    cleaned_code = '\n'.join(valid_lines).strip()
    # If cleaning removed too much, fallback to a simple diagram
    if len(cleaned_code.strip()) < 50 or not re.search(r'(graph|flowchart|sequenceDiagram|classDiagram|stateDiagram|erDiagram|journey|gantt|pie|gitgraph|mindmap)', cleaned_code, re.IGNORECASE):
        cleaned_code = """graph TD\n    A[Concept 1] --> B[Concept 2]\n    B --> C[Concept 3]\n    C --> D[Concept 4]"""
    return cleaned_code

def ensure_flowchart_node_labels(mermaid_code: str) -> str:
    import re
    lines = mermaid_code.splitlines()
    if not lines or not lines[0].strip().startswith('flowchart'):
        return mermaid_code
    # Find all node references (A, B, etc.)
    node_refs = set(re.findall(r'([A-Za-z0-9_]+)\s*-->', mermaid_code))
    node_refs.update(re.findall(r'-->([A-Za-z0-9_]+)', mermaid_code))
    # Find all defined nodes (A[Label])
    defined_nodes = set(re.findall(r'([A-Za-z0-9_]+)\[', mermaid_code))
    # For any node referenced but not defined, add a label
    for node in node_refs:
        if node not in defined_nodes:
            mermaid_code += f'\n{node}[{node}]'
    return mermaid_code

def extract_mermaid_diagrams(markdown_content: str) -> list:
    """Extract Mermaid diagrams from markdown content."""
    diagrams = []
    pattern = r'##\s*(.*?)\n(.*?)\n```mermaid\n(.*?)```'
    matches = re.findall(pattern, markdown_content, re.DOTALL)
    for i, (title, description, mermaid_code) in enumerate(matches, 1):
        # Remove surrounding brackets from title if present
        title = title.strip()
        if title.startswith('[') and title.endswith(']'):
            title = title[1:-1].strip()
        description = description.strip()
        original_mermaid_code = mermaid_code.strip()
        mermaid_code = original_mermaid_code
        if not title or not mermaid_code or len(mermaid_code) < 10:
            continue
        valid_diagram_types = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram', 'erDiagram', 'journey', 'gantt', 'pie', 'gitgraph', 'mindmap']
        has_valid_syntax = any(diagram_type in mermaid_code.lower() for diagram_type in valid_diagram_types)
        if not has_valid_syntax:
            continue
        diagrams.append({
            'title': title,
            'description': description,
            'mermaid_code': mermaid_code
        })
    return diagrams

def sanitize_mermaid_code(mermaid_code: str) -> str:
    """Sanitize Mermaid code to avoid parse errors with mmdc and preserve node labels."""
    import re
    try:
        # Replace any node label of the form A(...), A[(...)], A((...)), etc. with A[...]
        mermaid_code = re.sub(r'([A-Za-z0-9_])\(\(*([^\)]+)\)*\)', r'\1[\2]', mermaid_code)
        # Remove any stray parentheses from inside node labels
        mermaid_code = re.sub(r'\[([^\]]+)\]', lambda m: '[' + m.group(1).replace('(', '').replace(')', '') + ']', mermaid_code)
        # Shorten and simplify edge labels (truncate to 30 chars, replace := and =)
        def clean_edge_label(match):
            label = match.group(1)
            label = label.replace(':=', 'is').replace('=', 'is').replace(':', '').strip()
            if len(label) > 30:
                label = label[:27] + '...'
            return f'|{label}|'
        mermaid_code = re.sub(r'\|([^|]*)\|', clean_edge_label, mermaid_code)
        return mermaid_code
    except Exception as e:
        print(f"❌ Error in sanitize_mermaid_code: {e}")
        return mermaid_code

def convert_mermaid_to_svg(mermaid_code: str) -> str:
    """Convert Mermaid code to SVG using mermaid-cli."""
    try:
        mermaid_code = mermaid_code.strip()
        if not mermaid_code or len(mermaid_code) < 10:
            return ""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
            f.write(mermaid_code)
            mermaid_file = f.name
        svg_file = mermaid_file.replace('.mmd', '.svg')
        result = subprocess.run([
            'mmdc', 
            '-i', mermaid_file, 
            '-o', svg_file,
            '-b', 'transparent',
            '-w', '800'
        ], capture_output=True, text=True, timeout=30)
        svg_content = ""
        if result.returncode == 0 and os.path.exists(svg_file):
            with open(svg_file, 'r') as f:
                svg_content = f.read()
        # Clean up temp files
        if os.path.exists(mermaid_file):
            os.remove(mermaid_file)
        if os.path.exists(svg_file):
            os.remove(svg_file)
        return svg_content if '<svg' in svg_content and len(svg_content) > 100 else ""
    except subprocess.TimeoutExpired:
        return ""
    except Exception:
        return ""

def generate_diagrams_as_pdf(text: str, level: str, diagram_type: str = "general") -> BytesIO:
    """Generate diagrams and return as PDF."""
    raw_content = generate_diagrams(text, level, diagram_type)
    diagrams = extract_mermaid_diagrams(raw_content)
    if not diagrams:
        if len(text.strip()) > 50:
            diagrams = [{
                'title': 'Concept Overview',
                'description': 'A basic overview of the main concepts from the provided content',
                'mermaid_code': 'graph TD\n    A[Main Concept] --> B[Sub Concept 1]\n    A --> C[Sub Concept 2]\n    B --> D[Detail 1]\n    C --> E[Detail 2]'
            }]
        else:
            diagrams = []
    title = generate_ai_title(text, "diagram set")
    if not diagrams:
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
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 2em;
                    text-align: center;
                }}
                h1 {{
                    font-size: 28px;
                    color: #2a6ebd;
                    margin-bottom: 1em;
                }}
                .message {{
                    font-size: 18px;
                    color: #666;
                    margin: 2em 0;
                    padding: 2em;
                    background-color: #f9f9f9;
                    border-radius: 8px;
                    border: 1px solid #ddd;
                }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <div class=\"message\">
                <p>No diagrams could be generated from the provided content.</p>
                <p>The content may be too simple, too short, or lack clear relationships that can be visualized.</p>
                <p>Try selecting a different diagram type or using content with more complex concepts and relationships.</p>
            </div>
        </body>
        </html>
        """
        pdf_buffer = BytesIO()
        HTML(string=full_html).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        return pdf_buffer
    diagram_blocks = []
    FONTS = [
        "Arial, sans-serif",
        "Georgia, serif",
        "Courier New, monospace",
        "Verdana, Geneva, sans-serif",
        "Times New Roman, Times, serif"
    ]
    COLORS = [
        {"primaryColor": "#90caf9", "nodeTextColor": "#1a237e", "lineColor": "#1976d2"},
        {"primaryColor": "#f48fb1", "nodeTextColor": "#880e4f", "lineColor": "#ad1457"},
        {"primaryColor": "#a5d6a7", "nodeTextColor": "#1b5e20", "lineColor": "#388e3c"},
        {"primaryColor": "#ffe082", "nodeTextColor": "#ff6f00", "lineColor": "#ffa000"},
        {"primaryColor": "#b0bec5", "nodeTextColor": "#263238", "lineColor": "#455a64"},
    ]
    THEMES = ['default', 'forest', 'dark', 'neutral']
    for i, diagram in enumerate(diagrams, 1):
        mermaid_code = diagram['mermaid_code']
        mermaid_code = clean_mermaid_code(mermaid_code)
        mermaid_code = sanitize_mermaid_code(mermaid_code)
        mermaid_code = ensure_flowchart_node_labels(mermaid_code)
        # Use 'default' theme and force 'graph TD' for basic diagrams
        if level.lower() == 'basic':
            theme = 'default'
            # Ensure the diagram starts with 'graph TD'
            lines = mermaid_code.strip().split('\n')
            if not lines[0].strip().lower().startswith('graph td'):
                # Replace first line with 'graph TD' if it's a graph/flowchart
                if lines[0].strip().lower().startswith(('graph', 'flowchart')):
                    lines[0] = 'graph TD'
                else:
                    lines = ['graph TD'] + lines
            mermaid_code = '\n'.join(lines)
            font = random.choice(FONTS)
        else:
            theme = random.choice(THEMES)
            font = random.choice(FONTS)
        init_block = (
            f"%%{{init: {{'theme': '{theme}', 'themeVariables': {{'fontSize': '20px', 'fontFamily': '{font}', 'nodeSpacing': 40, 'rankSpacing': 40}} }} }}%%\n"
        )
        if not mermaid_code.strip().startswith('%%{init:'):
            mermaid_code = init_block + mermaid_code
        mmd_path = f'diagram_{i}.mmd'
        png_path = f'diagram_{i}.png'
        with open(mmd_path, 'w') as f:
            f.write(mermaid_code)
        # Use mmdc to generate very high-res PNG
        result_png = subprocess.run([
            'mmdc', '-i', mmd_path, '-o', png_path, '-w', '2400', '-H', '1800'
        ], capture_output=True, text=True)
        diagram_img_html = ""
        if result_png.returncode == 0 and os.path.exists(png_path):
            # Downscale the PNG to fit within max PDF dimensions (600x800)
            try:
                with Image.open(png_path) as img:
                    max_width, max_height = 600, 800
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    # Save to a BytesIO buffer
                    buf = BytesIO()
                    img.save(buf, format='PNG')
                    img_data = buf.getvalue()
            except Exception as e:
                # Fallback: use original PNG if resizing fails
                with open(png_path, 'rb') as img_f:
                    img_data = img_f.read()
            img_b64 = base64.b64encode(img_data).decode('utf-8')
            data_uri = f"data:image/png;base64,{img_b64}"
            diagram_img_html = f'<img src="{data_uri}" alt="{diagram["title"]}" style="max-width: 600px; width: 100%; height: auto; display: block; margin: 0 auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(30,60,90,0.13);" />'
            # Clean up PNG and MMD files after use
            try:
                if os.path.exists(mmd_path):
                    os.remove(mmd_path)
                if os.path.exists(png_path):
                    os.remove(png_path)
            except Exception:
                pass
        else:
            print(f"[Diagram Generation Error] Diagram {i} failed to generate PNG. Return code: {result_png.returncode}")
            if result_png.stderr:
                print(f"[mmdc stderr] {result_png.stderr.strip()}")
            diagram_img_html = '<div class="diagram-error">Diagram could not be rendered due to invalid content.</div>'
        container_class = "diagram-container alt" if i % 2 == 1 else "diagram-container"
        block_html = f'''
        <div class="{container_class}">
            <h2>{diagram["title"]}</h2>
            <p class="diagram-description">{diagram["description"]}</p>
            <div class="diagram-svg">{diagram_img_html}</div>
                    </div>
        '''
        diagram_blocks.append(block_html)
    full_html = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <title>{title}</title>
        <script src=\"https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js\"></script>
        <style>
            body {{
                font-family: 'Georgia', serif;
                margin: 2em;
                line-height: 1.6;
                color: #222;
                max-width: 1200px;
                margin: 0 auto;
                padding: 2em;
                background: #f6f8fa;
            }}
            h1 {{
                font-size: 28px;
                text-align: center;
                margin-bottom: 1.5em;
                color: #1a4e8a;
                letter-spacing: 1px;
            }}
            h2 {{
                font-size: 22px;
                color: #197278;
                margin-top: 1.2em;
                margin-bottom: 0.3em;
                border-bottom: 2px solid #197278;
                padding-bottom: 0.2em;
                page-break-after: avoid;
                letter-spacing: 0.5px;
            }}
            .diagram-container, .diagram-container.alt {{
                margin-bottom: 2em;
                page-break-inside: avoid;
                break-inside: avoid;
                padding: 0 0 1.5em 0;
                box-sizing: border-box;
                background: none;
                border: none;
                box-shadow: none;
                transition: none;
            }}
            .diagram-description {{
                font-style: italic;
                color: #5e548e;
                margin-bottom: 0.7em;
                font-size: 16px;
                page-break-after: avoid;
                letter-spacing: 0.2px;
            }}
            .diagram-svg {{
                text-align: center;
                margin: 0.5em 0 0.5em 0;
                padding: 0.5em;
                background-color: #fff;
                border-radius: 10px;
                border: 1px solid #eee;
                page-break-inside: avoid;
                break-inside: avoid;
                box-shadow: 0 2px 12px rgba(30,60,90,0.10);
            }}
            .diagram-svg img {{
                max-width: 600px;
                width: 100%;
                height: auto;
                display: block;
                margin: 0 auto;
                page-break-inside: avoid;
                break-inside: avoid;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(30,60,90,0.13);
            }}
            .diagram-error {{
                color: #b71c1c;
                font-weight: normal;
                font-size: 14px;
                padding: 0.5em 1em;
                background: #fff7f7;
                border: 1px solid #f8bbd0;
                border-radius: 6px;
                margin: 0.5em auto;
                text-align: center;
            }}
            .mermaid-fallback {{
                margin: 1em 0;
                padding: 1em;
                background-color: #f9f9f9;
                border-radius: 8px;
                border: 1px solid #ddd;
            }}
            .mermaid-fallback .mermaid {{
                text-align: center;
                margin: 1em 0;
                padding: 1em;
                background-color: white;
                border-radius: 4px;
                border: 1px solid #ccc;
            }}
            .mermaid-fallback pre {{
                background-color: #f4f4f4;
                padding: 1em;
                border-radius: 4px;
                overflow-x: auto;
                font-size: 12px;
                line-height: 1.4;
                margin-top: 1em;
            }}
            .mermaid-fallback code {{
                font-family: 'Courier New', monospace;
            }}
            @media print {{
                .diagram-container, .diagram-container.alt {{
                    page-break-inside: avoid;
                    break-inside: avoid;
                    margin-bottom: 1.5em;
                    background: none;
                    border: none;
                    box-shadow: none;
                }}
                .diagram-svg {{
                    background-color: white;
                    border: 1px solid #ccc;
                }}
                .mermaid-fallback {{
                    background-color: white;
                    border: 1px solid #ccc;
                }}
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        {''.join(diagram_blocks)}
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'default',
                flowchart: {{
                    useMaxWidth: true,
                    htmlLabels: true
                }},
                sequence: {{
                    useMaxWidth: true
                }},
                gantt: {{
                    useMaxWidth: true
                }}
            }});
        </script>
    </body>
    </html>
    """
    pdf_buffer = BytesIO()
    HTML(string=full_html, base_url=os.path.abspath(os.path.dirname(__file__))).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer 

def generate_diagrams_from_file(file_path, level='In-depth', diagram_type='general', output_pdf_path=None):
    """Read content from a file and generate diagrams as a PDF, saving to study-buddy-extension/ by default."""
    if output_pdf_path is None:
        # Save to the outer study-buddy-extension/ folder by default for debugging
        output_pdf_path = '../diagrams_from_canvas_notes.pdf'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    pdf_buffer = generate_diagrams_as_pdf(content, level, diagram_type)
    with open(output_pdf_path, 'wb') as out_pdf:
        out_pdf.write(pdf_buffer.getbuffer())
    import os
    abs_path = os.path.abspath(output_pdf_path)
    print(f"✅ PDF generated at {abs_path}")

if __name__ == '__main__':
    # Example usage: generate diagrams from a real file (not test content)
    # Replace 'my_canvas_notes.txt' with your actual file path
    input_file = 'my_canvas_notes.txt'
    output_pdf = 'diagrams_from_canvas_notes.pdf'
    generate_diagrams_from_file(input_file, level='In-depth', diagram_type='general', output_pdf_path=output_pdf) 