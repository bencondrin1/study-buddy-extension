# utils/gpt/diagrams.py

import re
import base64
import subprocess
import tempfile
import os
import sys
from io import BytesIO
from weasyprint import HTML

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
            "Include decision points with diamond shapes and process steps with rectangles.\n"
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
        )
    else:  # In-Depth
        guidance = (
            "Create comprehensive, detailed diagrams.\n"
            "Include all relevant relationships and connections.\n"
            "Show detailed processes and sub-steps.\n"
            "Include additional context and background information.\n"
            "Use more sophisticated diagram structures when appropriate.\n"
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
        "[mermaid code]\n"
        "```\n\n"
        "IMPORTANT: Generate 1-2 diagrams that best represent the key concepts.\n"
        "Focus on creating diagrams that show relationships, processes, or hierarchies.\n"
        "Even simple concepts can benefit from visual representation.\n"
        "If the content is very basic, create a simple flowchart or mind map.\n"
        "Each diagram should help with understanding and memorization.\n"
    )
    
    return intro + base + guidance + format_instructions + "\n\nNotes:\n" + text

def generate_diagrams(text: str, level: str, diagram_type: str = "general") -> str:
    """Generate diagrams from text content using GPT."""
    print(f"🔍 DEBUG: Starting diagram generation")
    print(f"🔍 DEBUG: Input text length: {len(text)} characters")
    print(f"🔍 DEBUG: Level: {level}, Diagram type: {diagram_type}")
    print(f"🔍 DEBUG: Input text preview: {text[:200]}...")
    
    prompt = build_diagram_prompt(level, text, diagram_type)
    print(f"🔍 DEBUG: Prompt length: {len(prompt)} characters")
    print(f"🔍 DEBUG: Prompt preview: {prompt[:500]}...")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000,
        temperature=0.7,
    )
    content = response.choices[0].message.content
    result = content.strip() if content else ""
    
    print(f"🔍 DEBUG: Raw GPT response length: {len(result)} characters")
    print(f"🔍 DEBUG: Raw GPT response:")
    print("=" * 60)
    print(result)
    print("=" * 60)
    
    return result

def clean_mermaid_code(mermaid_code: str) -> str:
    """Clean Mermaid code to remove problematic syntax."""
    print(f"🔍 DEBUG: Starting Mermaid code cleaning")
    print(f"🔍 DEBUG: Original code length: {len(mermaid_code)}")
    print(f"🔍 DEBUG: Original code:")
    print("-" * 40)
    print(mermaid_code)
    print("-" * 40)
    
    # Remove problematic note syntax that causes parsing errors
    mermaid_code = re.sub(r'note\s+(?:right|left|top|bottom)\s+of\s+[^:]+:\s*[^\n]+', '', mermaid_code)
    
    # Remove complex relationship labels with special characters
    mermaid_code = re.sub(r'"[^"]*[^\w\s][^"]*"\s*--\s*"[^"]*[^\w\s][^"]*"', '', mermaid_code)
    
    # Remove lines with complex annotations or special characters
    lines = mermaid_code.split('\n')
    cleaned_lines = []
    removed_nodes = set()
    
    print(f"🔍 DEBUG: Processing {len(lines)} lines")
    
    for i, line in enumerate(lines):
        print(f"🔍 DEBUG: Processing line {i+1}: '{line.strip()}'")
        
        # Skip lines with complex annotations, notes, or special characters
        if any(skip_pattern in line.lower() for skip_pattern in ['note ', 'ξ', '′′', '′′′′', 'f′′', 'f′′′′']):
            print(f"🔍 DEBUG: Removing line {i+1} (complex annotations): {line.strip()}")
            # Extract node name if this line defines a node
            node_match = re.search(r'^(\w+)\[', line)
            if node_match:
                removed_nodes.add(node_match.group(1))
                print(f"🔍 DEBUG: Added {node_match.group(1)} to removed_nodes")
            continue
        
        # Skip lines with mathematical expressions or special characters
        if re.search(r'[∫∑∏√∞≠≤≥±×÷∂∇∆∈∉∋∌∩∪⊂⊃⊆⊇⊕⊗∀∃∄∴∵∝∞θαβγδεζηθικλμνξοπρστυφχψω]', line):
            print(f"🔍 DEBUG: Removing line {i+1} (math symbols): {line.strip()}")
            # Extract node name if this line defines a node
            node_match = re.search(r'^(\w+)\[', line)
            if node_match:
                removed_nodes.add(node_match.group(1))
                print(f"🔍 DEBUG: Added {node_match.group(1)} to removed_nodes")
            continue
        
        # Skip lines with very complex mathematical expressions (but be more selective)
        # Only remove lines with actual mathematical symbols or very complex formulas
        if re.search(r'[∫∑∏√∞≠≤≥±×÷∂∇∆∈∉∋∌∩∪⊂⊃⊆⊇⊕⊗∀∃∄∴∵∝∞θαβγδεζηθικλμνξοπρστυφχψω]', line):
            print(f"🔍 DEBUG: Removing line {i+1} (math symbols): {line.strip()}")
            # Extract node name if this line defines a node
            node_match = re.search(r'^(\w+)\[', line)
            if node_match:
                removed_nodes.add(node_match.group(1))
                print(f"🔍 DEBUG: Added {node_match.group(1)} to removed_nodes")
            continue
        
        # Only remove lines with very specific problematic patterns, not all function calls
        if re.search(r'f\([^)]*\)[^)]*\([^)]*\)', line) or re.search(r'[a-z]\([^)]*[^a-zA-Z0-9\s][^)]*\)[^)]*\([^)]*\)', line):
            print(f"🔍 DEBUG: Removing line {i+1} (complex expressions): {line.strip()}")
            # Extract node name if this line defines a node
            node_match = re.search(r'^(\w+)\[', line)
            if node_match:
                removed_nodes.add(node_match.group(1))
                print(f"🔍 DEBUG: Added {node_match.group(1)} to removed_nodes")
            continue
        
        print(f"🔍 DEBUG: Keeping line {i+1}: '{line.strip()}'")
        cleaned_lines.append(line)
    
    # Remove references to deleted nodes
    final_lines = []
    print(f"🔍 DEBUG: Removing references to {len(removed_nodes)} deleted nodes: {removed_nodes}")
    
    for line in cleaned_lines:
        # Check if line references a removed node
        if any(f"{node} -->" in line or f"--> {node}" in line for node in removed_nodes):
            print(f"🔍 DEBUG: Removing broken reference: {line.strip()}")
            continue
        # Also check for orphaned references (like "E --> F" where E was removed)
        arrow_match = re.search(r'(\w+)\s*-->\s*(\w+)', line)
        if arrow_match:
            from_node, to_node = arrow_match.groups()
            if from_node in removed_nodes or to_node in removed_nodes:
                print(f"🔍 DEBUG: Removing orphaned reference: {line.strip()}")
                continue
        final_lines.append(line)
    
    cleaned_code = '\n'.join(final_lines).strip()
    
    # Additional cleaning: replace complex node labels with simple ones
    # Only replace labels that contain actual mathematical symbols, not all special characters
    cleaned_code = re.sub(r'\(\([^)]*[∫∑∏√∞≠≤≥±×÷∂∇∆∈∉∋∌∩∪⊂⊃⊆⊇⊕⊗∀∃∄∴∵∝∞θαβγδεζηθικλμνξοπρστυφχψω][^)]*\)\)', '(Simple Node)', cleaned_code)
    cleaned_code = re.sub(r'\[[^\]]*[∫∑∏√∞≠≤≥±×÷∂∇∆∈∉∋∌∩∪⊂⊃⊆⊇⊕⊗∀∃∄∴∵∝∞θαβγδεζηθικλμνξοπρστυφχψω][^\]]*\]', '[Simple Node]', cleaned_code)
    
    # CRITICAL FIX: If we removed too many nodes and left only orphaned arrows, 
    # create a simple fallback diagram instead of returning broken code
    if len(cleaned_code.strip()) < 50 and '-->' in cleaned_code:
        print(f"🔍 DEBUG: Cleaning removed too much content, creating fallback diagram")
        # Check if we have any remaining node definitions
        remaining_nodes = re.findall(r'(\w+)\[', cleaned_code)
        print(f"🔍 DEBUG: Remaining nodes: {remaining_nodes}")
        if len(remaining_nodes) < 2:
            # Create a simple fallback diagram
            cleaned_code = """graph TD
    A[Integration Methods] --> B[Trapezoidal Rule]
    A --> C[Simpson's Rule]
    B --> D[Numerical Approximation]
    C --> D"""
            print(f"🔍 DEBUG: Created fallback diagram")
    
    print(f"🔍 DEBUG: Final cleaned code length: {len(cleaned_code)}")
    print(f"🔍 DEBUG: Final cleaned code:")
    print("-" * 40)
    print(cleaned_code)
    print("-" * 40)
    
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
    print(f"🔍 DEBUG: Starting diagram extraction")
    print(f"🔍 DEBUG: Input markdown length: {len(markdown_content)} characters")
    print(f"🔍 DEBUG: Input markdown preview: {markdown_content[:500]}...")
    
    diagrams = []
    pattern = r'##\s*(.*?)\n(.*?)\n```mermaid\n(.*?)```'
    matches = re.findall(pattern, markdown_content, re.DOTALL)
    
    print(f"🔍 DEBUG: Found {len(matches)} potential diagram matches")
    for i, (title, description, mermaid_code) in enumerate(matches, 1):
        print(f"🔍 DEBUG: Match {i}: '{title.strip()}' (code length: {len(mermaid_code.strip())})")
        print(f"🔍 DEBUG: Match {i} description: {description.strip()}")
        print(f"🔍 DEBUG: Match {i} mermaid code preview: {mermaid_code.strip()[:200]}...")
    
    for i, (title, description, mermaid_code) in enumerate(matches, 1):
        print(f"🔍 DEBUG: Processing match {i}...")
        
        # Clean and validate the extracted content
        title = title.strip()
        description = description.strip()
        original_mermaid_code = mermaid_code.strip()
        # BYPASS CLEANING FUNCTION FOR TESTING
        mermaid_code = original_mermaid_code  # skip cleaning for now
        # mermaid_code = clean_mermaid_code(original_mermaid_code)
        
        print(f"🔍 DEBUG: Match {i} - Original code length: {len(original_mermaid_code)}")
        print(f"🔍 DEBUG: Match {i} - Cleaned code length: {len(mermaid_code)}")
        
        # Skip empty or invalid diagrams
        if not title or not mermaid_code or len(mermaid_code) < 10:
            print(f"🔍 DEBUG: Skipping invalid diagram {i}: '{title}' (code length: {len(mermaid_code)})")
            print(f"🔍 DEBUG: Title empty: {not title}")
            print(f"🔍 DEBUG: Code empty: {not mermaid_code}")
            print(f"🔍 DEBUG: Code too short: {len(mermaid_code) < 10}")
            continue
        
        # Validate that the Mermaid code contains actual diagram syntax
        valid_diagram_types = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram', 'erDiagram', 'journey', 'gantt', 'pie', 'gitgraph', 'mindmap']
        has_valid_syntax = any(diagram_type in mermaid_code.lower() for diagram_type in valid_diagram_types)
        print(f"🔍 DEBUG: Match {i} - Has valid syntax: {has_valid_syntax}")
        
        if not has_valid_syntax:
            print(f"🔍 DEBUG: Skipping diagram {i} with invalid syntax: '{title}'")
            print(f"🔍 DEBUG: Diagram code: {mermaid_code}")
            continue
        
        diagrams.append({
            'title': title,
            'description': description,
            'mermaid_code': mermaid_code
        })
        print(f"🔍 DEBUG: Added diagram {i}: '{title}'")
    
    print(f"🔍 DEBUG: Extracted {len(diagrams)} valid diagrams from GPT response")
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
        # Clean and validate the Mermaid code
        mermaid_code = mermaid_code.strip()
        if not mermaid_code or len(mermaid_code) < 10:
            print("❌ Mermaid code too short or empty")
            return ""
        
        # Create a temporary file for the mermaid code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
            f.write(mermaid_code)
            mermaid_file = f.name
        
        # Create output file
        svg_file = mermaid_file.replace('.mmd', '.svg')
        
        print(f"🔄 Converting Mermaid diagram...")
        print(f"   Input length: {len(mermaid_code)} characters")
        
        # Use mmdc (mermaid-cli) to convert to SVG
        result = subprocess.run([
            'mmdc', 
            '-i', mermaid_file, 
            '-o', svg_file,
            '-b', 'transparent',
            '-w', '800'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(svg_file):
            with open(svg_file, 'r') as f:
                svg_content = f.read()
            
            # Validate SVG content
            if '<svg' in svg_content and len(svg_content) > 100:
                print(f"✅ Successfully converted to SVG ({len(svg_content)} characters)")
                # Clean up temp files
                os.remove(mermaid_file)
                os.remove(svg_file)
                return svg_content
            else:
                print(f"❌ Generated SVG is invalid or too small")
                print(f"   SVG content preview: {svg_content[:200]}...")
        else:
            print(f"❌ Mermaid conversion failed:")
            print(f"   Return code: {result.returncode}")
            print(f"   stderr: {result.stderr}")
            print(f"   stdout: {result.stdout}")
        
        # Clean up temp files
        if os.path.exists(mermaid_file):
            os.remove(mermaid_file)
        if os.path.exists(svg_file):
            os.remove(svg_file)
        return ""
            
    except subprocess.TimeoutExpired:
        print("❌ Mermaid conversion timed out")
        return ""
    except Exception as e:
        print(f"❌ Error converting Mermaid to SVG: {e}")
        return ""

def generate_diagrams_as_pdf(text: str, level: str, diagram_type: str = "general") -> BytesIO:
    """Generate diagrams and return as PDF."""
    print(f"🔍 DEBUG: Starting PDF generation")
    print(f"🔍 DEBUG: Input text length: {len(text)} characters")
    print(f"🔍 DEBUG: Level: {level}, Diagram type: {diagram_type}")
    print(f"🔍 DEBUG: Content preview: {text[:200]}...")
    
    raw_content = generate_diagrams(text, level, diagram_type)
    print(f"🔍 DEBUG: GPT response length: {len(raw_content)} characters")
    print(f"🔍 DEBUG: GPT response preview: {raw_content[:500]}...")
    
    diagrams = extract_mermaid_diagrams(raw_content)
    print(f"🔍 DEBUG: Final diagrams count: {len(diagrams)}")
    
    if not diagrams:
        print("🔍 DEBUG: No valid diagrams generated.")
        print(f"🔍 DEBUG: Content length: {len(text.strip())} characters")
        print(f"🔍 DEBUG: Content preview: {text.strip()[:100]}...")
        
        # Only create fallback if we have some content to work with
        if len(text.strip()) > 50:
            print("🔍 DEBUG: Creating a simple concept overview...")
            diagrams = [{
                'title': 'Concept Overview',
                'description': 'A basic overview of the main concepts from the provided content',
                'mermaid_code': 'graph TD\n    A[Main Concept] --> B[Sub Concept 1]\n    A --> C[Sub Concept 2]\n    B --> D[Detail 1]\n    C --> E[Detail 2]'
            }]
        else:
            print("🔍 DEBUG: Content too short for meaningful diagram generation")
            diagrams = []
    
    # Generate AI title
    title = generate_ai_title(text, "diagram set")
    
    # Handle case where no diagrams were generated
    if not diagrams:
        # Create a simple message instead of diagrams
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
            <div class="message">
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
    
    # Build HTML with embedded diagrams
    diagram_html = ""
    for i, diagram in enumerate(diagrams, 1):
        print(f"🔄 Processing diagram {i}: {diagram['title']}")
        
        # Validate the Mermaid code before conversion
        mermaid_code = diagram['mermaid_code']
        
        # Sanitize Mermaid code to avoid parse errors
        mermaid_code = sanitize_mermaid_code(mermaid_code)
        # Ensure all flowchart nodes have labels
        mermaid_code = ensure_flowchart_node_labels(mermaid_code)
        
        # DEBUG: Print the final Mermaid code before PNG conversion
        print(f"🔍 FINAL Mermaid code for diagram {i}:\n{mermaid_code}\n{'-'*40}")
        
        # Use mmdc to export PNG from Mermaid code
        import os
        import subprocess
        mmd_path = f'diagram_{i}.mmd'
        png_path = f'diagram_{i}.png'
        with open(mmd_path, 'w') as f:
            f.write(mermaid_code)
        result_png = subprocess.run([
            'mmdc', '-i', mmd_path, '-o', png_path, '-w', '800', '-H', '600'
        ], capture_output=True, text=True)
        if result_png.returncode == 0 and os.path.exists(png_path):
            print(f"✅ Diagram {i} converted to PNG with mmdc")
            diagram_abs_path = os.path.abspath(png_path)
            data_uri = f"file://{diagram_abs_path}"
            diagram_html += f"""
            <div class=\"diagram-container\">
                <h2>{diagram['title']}</h2>
                <p class=\"diagram-description\">{diagram['description']}</p>
                <div class=\"diagram-svg\">
                    <img src=\"{data_uri}\" alt=\"{diagram['title']}\" style=\"max-width: 700px; width: 100%; height: auto; display: block; margin: 0 auto;\" />
                </div>
            </div>
            """
        else:
            print(f"❌ mmdc PNG export failed for diagram {i}: {result_png.stderr}")
            # Fallback to SVG embedding
            svg_content = convert_mermaid_to_svg(mermaid_code)
            diagram_html += f"""
            <div class=\"diagram-container\">
                <h2>{diagram['title']}</h2>
                <p class=\"diagram-description\">{diagram['description']}</p>
                <div class=\"diagram-svg\">
                    {svg_content}
                </div>
            </div>
            """
    
    icon_abs_path = None  # No longer needed
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
            }}
            h1 {{
                font-size: 28px;
                text-align: center;
                margin-bottom: 1.5em;
                color: #2a6ebd;
            }}
            h2 {{
                font-size: 22px;
                color: #2a6ebd;
                margin-top: 2em;
                margin-bottom: 0.5em;
                border-bottom: 2px solid #2a6ebd;
                padding-bottom: 0.3em;
            }}
            .diagram-container {{
                margin-bottom: 3em;
                page-break-inside: avoid;
            }}
            .diagram-description {{
                font-style: italic;
                color: #666;
                margin-bottom: 1em;
                font-size: 16px;
            }}
            .diagram-svg {{
                text-align: center;
                margin: 1em 0;
                padding: 1em;
                background-color: #f9f9f9;
                border-radius: 8px;
                border: 1px solid #ddd;
            }}
            .diagram-svg img {{
                max-width: 700px;
                width: 100%;
                height: auto;
                display: block;
                margin: 0 auto;
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
                .diagram-container {{
                    page-break-inside: avoid;
                    margin-bottom: 2em;
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
        {diagram_html}
        
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