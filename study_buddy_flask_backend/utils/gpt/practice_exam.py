# utils/gpt/practice_exam.py

import os
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import json
import re

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils', '.env'))
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
client = OpenAI(api_key=api_key)


def fix_formatting_issues(raw_text):
    """
    Post-processes the GPT output to fix common formatting issues:
    - Ensures proper indentation for multiple choice options
    - Fixes sequential numbering across all question sections
    - Restarts numbering only for answer key
    - Ensures consistent formatting
    """
    if not raw_text:
        return raw_text
    
    lines = raw_text.split('\n')
    fixed_lines = []
    current_section = None
    question_number = 0
    in_multiple_choice = False
    in_answer_key = False
    
    for line in lines:
        original_line = line
        line = line.strip()
        
        # Detect sections
        if "MULTIPLE CHOICE" in line.upper():
            current_section = "multiple_choice"
            in_multiple_choice = True
            in_answer_key = False
            # Don't reset numbering - continue from previous section
            fixed_lines.append(original_line)
            continue
        elif "SHORT ANSWER" in line.upper():
            current_section = "short_answer"
            in_multiple_choice = False
            in_answer_key = False
            # Don't reset numbering - continue from previous section
            fixed_lines.append(original_line)
            continue
        elif "FILL IN THE BLANK" in line.upper():
            current_section = "fill_blank"
            in_multiple_choice = False
            in_answer_key = False
            # Don't reset numbering - continue from previous section
            fixed_lines.append(original_line)
            continue
        elif "ESSAY" in line.upper():
            current_section = "essay"
            in_multiple_choice = False
            in_answer_key = False
            # Don't reset numbering - continue from previous section
            fixed_lines.append(original_line)
            continue
        elif "ANSWER KEY" in line.upper() or "SOLUTIONS" in line.upper():
            current_section = "answer_key"
            in_multiple_choice = False
            in_answer_key = True
            question_number = 0  # Reset numbering for answer key
            fixed_lines.append(original_line)
            continue
        
        # Skip empty lines
        if not line:
            fixed_lines.append(original_line)
            continue
        
        # Handle multiple choice options
        if in_multiple_choice and re.match(r'^[A-D]\)', line):
            # Ensure proper indentation for options
            option_letter = line[0]
            option_text = line[2:].strip()
            fixed_lines.append(f"   {option_letter}) {option_text}")
            continue
        
        # Handle question numbering
        if re.match(r'^\d+\.', line):
            question_number += 1
            # Extract the question text after the number
            question_text = line.split('.', 1)[1].strip() if '.' in line else line
            fixed_lines.append(f"{question_number}. {question_text}")
            continue
        
        # Keep other lines as is
        fixed_lines.append(original_line)
    
    return '\n'.join(fixed_lines)


def generate_practice_exam(text, level="Basic", exam_type="Mixed"):
    """
    Uses GPT to generate a structured practice exam with questions and answers.
    """
    level = level.lower()

    if level == "basic":
        prompt = (
            f"Generate a basic practice exam based on the following content.\n\n"
            f"Requirements:\n"
            f"- ONLY output a comprehensive multiple choice section.\n"
            f"- Do NOT include any other question types.\n"
            f"- Do NOT include any notes, summaries, formulas, or introductory text.\n"
            f"- Each question must be numbered sequentially (1, 2, 3, ...). Do NOT repeat the same number for multiple questions. If you do, your output will be rejected.\n"
            f"- Each question should have 4 options (A, B, C, D) and only one correct answer.\n"
            f"- RANDOMIZE the position of the correct answer (A, B, C, D) to avoid bias.\n"
            f"- Each answer choice (A, B, C, D) must be indented with exactly 3 spaces before the letter. If you do not indent, your output will be rejected.\n"
            f"- Do NOT ask about theorems, formulas, or facts unless you provide all necessary information in the question itself. If you reference a theorem (e.g., 'Theorem 6'), you MUST state the complete theorem in the question. For example, instead of 'What does Theorem 6 provide?', write 'Theorem 6 states: [full theorem statement]. What does this theorem provide?'\n"
            f"- Do NOT create questions that directly state the answer (e.g., 'The capital of France is Paris.'). Instead, ask 'What is the capital of France?'\n"
            f"- Make questions challenging and test actual understanding, not just memorization of obvious facts.\n"
            f"- Format questions in bold and answer options in regular text.\n"
            f"- Include enough questions to cover all fundamental concepts and definitions.\n"
            f"- For each question, provide the correct answer and a brief explanation in the answer key at the end.\n"
            f"- Use LaTeX for any mathematical expressions.\n"
            f"- Use clear, simple language.\n"
            f"- Do NOT invent or pad with irrelevant or generic questions. Only generate questions that are directly supported by the provided text. If there is limited information, generate fewer questions.\n\n"
            f"Format the output as:\n"
            f"MULTIPLE CHOICE QUESTIONS:\n"
            f"1. What is 2+2?\n"
            f"   A) 3\n"
            f"   B) 4\n"
            f"   C) 5\n"
            f"   D) 6\n\n"
            f"2. What is the capital of France?\n"
            f"   A) Berlin\n"
            f"   B) Madrid\n"
            f"   C) Paris\n"
            f"   D) Rome\n\n"
            f"3. Which of the following is a prime number?\n"
            f"   A) 4\n"
            f"   B) 6\n"
            f"   C) 9\n"
            f"   D) 7\n\n"
            f"[Continue with sequential numbering...]\n\n"
            f"--- END OF EXAM ---\n\n"
            f"ANSWER KEY AND SOLUTIONS:\n"
            f"1. B - 4 is the correct answer.\n"
            f"2. C - Paris is the capital of France.\n"
            f"3. D - 7 is a prime number.\n"
            f"[Continue with sequential numbering...]\n\n"
            f"Text:\n{text}"
        )
    else:  # In-depth
        prompt = (
            f"Generate a comprehensive practice exam based on the following content.\n\n"
            f"Requirements:\n"
            f"- Output ALL of the following sections, clearly labeled:\n"
            f"  1. A comprehensive multiple choice section (each question has 4 options, A-D, only one correct answer)\n"
            f"  2. A short answer section\n"
            f"  3. A fill in the blank section\n"
            f"  4. An essay question section\n"
            f"- Do NOT include any notes, summaries, formulas, or introductory text.\n"
            f"- Each question must be numbered sequentially (1, 2, 3, ...) across all sections. Do NOT repeat the same number for multiple questions. If you do, your output will be rejected.\n"
            f"- RANDOMIZE the position of correct answers in multiple choice (A, B, C, D) to avoid bias.\n"
            f"- Each answer choice (A, B, C, D) must be indented with exactly 3 spaces before the letter. If you do not indent, your output will be rejected.\n"
            f"- Do NOT ask about theorems, formulas, or facts unless you provide all necessary information in the question itself. If you reference a theorem (e.g., 'Theorem 6'), you MUST state the complete theorem in the question. For example, instead of 'What does Theorem 6 provide?', write 'Theorem 6 states: [full theorem statement]. What does this theorem provide?'\n"
            f"- Do NOT create questions that directly state the answer (e.g., 'The capital of France is Paris.'). Instead, ask 'What is the capital of France?'\n"
            f"- Make questions challenging and test actual understanding, not just memorization of obvious facts.\n"
            f"- Format questions in bold and answer options in regular text.\n"
            f"- Be exhaustive and comprehensive—include enough questions in each section to fully test understanding of the material.\n"
            f"- For each question, provide the correct answer and a detailed explanation in the answer key at the end.\n"
            f"- Use LaTeX for any mathematical expressions.\n"
            f"- Use clear, precise language.\n"
            f"- Format the output to be as neat and easy to read as possible.\n"
            f"- Use consistent spacing and formatting throughout.\n"
            f"- Make sure each question is clearly separated and easy to follow.\n"
            f"- Ensure proper visual hierarchy with clear section breaks.\n"
            f"- Do NOT invent or pad with irrelevant or generic questions. Only generate questions that are directly supported by the provided text. If there is limited information, generate fewer questions.\n\n"
            f"Format the output as:\n"
            f"MULTIPLE CHOICE QUESTIONS:\n"
            f"1. What is 2+2?\n"
            f"   A) 3\n"
            f"   B) 4\n"
            f"   C) 5\n"
            f"   D) 6\n\n"
            f"2. What is the capital of France?\n"
            f"   A) Berlin\n"
            f"   B) Madrid\n"
            f"   C) Paris\n"
            f"   D) Rome\n\n"
            f"3. Which of the following is a prime number?\n"
            f"   A) 4\n"
            f"   B) 6\n"
            f"   C) 9\n"
            f"   D) 7\n\n"
            f"[Continue with sequential numbering...]\n\n"
            f"SHORT ANSWER QUESTIONS:\n"
            f"1. [Question text]\n\n"
            f"2. [Question text]\n\n"
            f"[Continue with sequential numbering...]\n\n"
            f"FILL IN THE BLANK QUESTIONS:\n"
            f"1. [Question text with a blank: 'The capital of France is _____.']\n\n"
            f"2. [Question text with a blank]\n\n"
            f"[Continue with sequential numbering...]\n\n"
            f"ESSAY QUESTIONS:\n"
            f"1. [Essay prompt]\n\n"
            f"2. [Essay prompt]\n\n"
            f"[Continue with sequential numbering...]\n\n"
            f"--- END OF EXAM ---\n\n"
            f"ANSWER KEY AND SOLUTIONS:\n"
            f"Multiple Choice:\n"
            f"1. B - 4 is the correct answer.\n"
            f"2. C - Paris is the capital of France.\n"
            f"3. D - 7 is a prime number.\n"
            f"[Continue with sequential numbering...]\n\n"
            f"Short Answer:\n"
            f"1. [Model answer with explanation]\n"
            f"2. [Model answer with explanation]\n"
            f"[Continue with sequential numbering...]\n\n"
            f"Fill in the Blank:\n"
            f"1. [Correct word/phrase] - [Explanation]\n"
            f"2. [Correct word/phrase] - [Explanation]\n"
            f"[Continue with sequential numbering...]\n\n"
            f"Essay:\n"
            f"1. [Model essay or key points to include]\n"
            f"2. [Model essay or key points to include]\n"
            f"[Continue with sequential numbering...]\n\n"
            f"Text:\n{text}"
        )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7,
        )
        content = response.choices[0].message.content if response.choices else ""
        raw_output = content.strip() if content else ""
        
        # Apply post-processing to fix formatting issues
        fixed_output = fix_formatting_issues(raw_output)
        
        return fixed_output
    except OpenAIError as e:
        print(f"❌ OpenAI API error: {e}")
        return ""
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return ""


def parse_practice_exam(raw_text):
    """
    Parses GPT-generated practice exam text into a structured format.
    Returns a dictionary with questions and answer key.
    """
    if not raw_text:
        return {}
    
    # Initialize structure
    exam_data = {
        "questions": [],
        "answer_key": {},
        "exam_sections": []
    }
    
    # Split into questions and answers sections
    if "--- END OF EXAM ---" in raw_text:
        parts = raw_text.split("--- END OF EXAM ---")
        questions_text = parts[0].strip()
        answers_text = parts[1].strip() if len(parts) > 1 else ""
    else:
        questions_text = raw_text
        answers_text = ""
    
    # Parse questions section
    current_section = None
    current_question = None
    current_options = []
    question_number = 0
    
    lines = questions_text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Detect sections
        if "MULTIPLE CHOICE" in line.upper():
            current_section = "multiple_choice"
            exam_data["exam_sections"].append("multiple_choice")
            continue
        elif "SHORT ANSWER" in line.upper():
            current_section = "short_answer"
            exam_data["exam_sections"].append("short_answer")
            continue
        elif "PROBLEM SOLVING" in line.upper():
            current_section = "problem_solving"
            exam_data["exam_sections"].append("problem_solving")
            continue
        elif "PRACTICE EXAM QUESTIONS" in line.upper():
            current_section = "questions"
            continue
        
        # Skip empty lines
        if not line:
            continue
        
        # Parse questions
        if current_section:
            # Check if this is a new question (starts with a number)
            if re.match(r'^\d+\.', line):
                # Save previous question if exists
                if current_question:
                    exam_data["questions"].append({
                        "number": question_number,
                        "type": current_section,
                        "question": current_question,
                        "options": current_options if current_options else None
                    })
                
                # Start new question
                question_number += 1
                current_question = line.split('.', 1)[1].strip() if '.' in line else line
                current_options = []
                
            elif current_section == "multiple_choice" and re.match(r'^\s*[A-D]\)', line):
                # This is an option for multiple choice (handle indentation)
                option_letter = line.strip()[0]
                option_text = line.strip()[2:].strip()
                current_options.append({
                    "letter": option_letter,
                    "text": option_text
                })
            elif current_question and line:
                # Continue building the current question
                current_question += " " + line
    
    # Add the last question if exists
    if current_question:
        exam_data["questions"].append({
            "number": question_number,
            "type": current_section,
            "question": current_question,
            "options": current_options if current_options else None
        })
    
    # Parse answer key section
    if answers_text:
        current_section = None
        lines = answers_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Detect answer sections
            if "MULTIPLE CHOICE SOLUTIONS" in line.upper():
                current_section = "multiple_choice"
                continue
            elif "SHORT ANSWER SOLUTIONS" in line.upper():
                current_section = "short_answer"
                continue
            elif "PROBLEM SOLVING SOLUTIONS" in line.upper():
                current_section = "problem_solving"
                continue
            elif "ANSWER KEY AND SOLUTIONS" in line.upper():
                current_section = "general"
                continue
            
            # Skip empty lines
            if not line:
                continue
            
            # Parse answer entries
            if re.match(r'^\d+\.', line):
                # Handle different answer formats
                if ' - ' in line:
                    parts = line.split(' - ', 1)
                    question_num = parts[0].split('.')[0]
                    answer_text = parts[1].strip()
                elif ':' in line:
                    parts = line.split(':', 1)
                    question_num = parts[0].split('.')[0]
                    answer_text = parts[1].strip()
                else:
                    # Handle cases without explanation
                    question_num = line.split('.')[0]
                    answer_text = line.split('.', 1)[1].strip() if '.' in line else line
                
                exam_data["answer_key"][question_num] = {
                    "answer": answer_text,
                    "type": current_section
                }
    
    return exam_data


def export_practice_exam_to_pdf(raw_text, level="Basic", exam_type="Mixed"):
    """
    Exports practice exam data to a PDF format with proper math rendering.
    """
    import os
    import sys
    from io import BytesIO
    from weasyprint import HTML
    import re
    import gc
    
    # Add the parent directory to the Python path so we can import utils
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.dirname(current_dir))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from utils.gpt.shared import render_math_in_html, get_title_from_text
    
    if not raw_text:
        return BytesIO()
    
    try:
        # Detect if math is present to render with KaTeX
        if any(tag in raw_text for tag in ["\\[", "\\(", "$$", "$"]):
            rendered_text = render_math_in_html(raw_text)
        else:
            rendered_text = raw_text

        # Split into answer key and main body
        if 'ANSWER KEY AND SOLUTIONS:' in rendered_text:
            parts = rendered_text.split('ANSWER KEY AND SOLUTIONS:')
            main_body = parts[0]
            answer_key = parts[1] if len(parts) > 1 else ''
            # Highlight ALL answer key lines in red
            answer_key = re.sub(r'(^|<br>)([^<\n][^<\n]*)', lambda m: f"{m.group(1)}<span class='solution-red'>{m.group(2)}</span>", answer_key)
            html_body = main_body + 'ANSWER KEY AND SOLUTIONS:' + answer_key
        else:
            html_body = rendered_text

        # Convert to HTML while preserving exact formatting
        html_body = html_body.replace("\n", "<br>").replace("   ", "&nbsp;&nbsp;&nbsp;")

        title = f"Practice Exam: {get_title_from_text(raw_text)} ({level})"
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
                .solution-red {{
                    color: #b71c1c;
                    font-weight: bold;
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
                .exam-section {{
                    margin-bottom: 2em;
                }}
                .answer-key {{
                    margin-top: 2em;
                    padding-top: 1em;
                    border-top: 2px solid #2a6ebd;
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
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        # Return empty buffer on error
        return BytesIO()
    finally:
        # Force garbage collection
        gc.collect() 