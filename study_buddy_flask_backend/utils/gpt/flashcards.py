# utils/gpt/flashcards.py

import os
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_flashcards(text, level="Basic"):
    """
    Uses GPT to generate raw flashcard text in Q/A format.
    """
    level = level.lower()
    
    if level == "basic":
        prompt = (
            f"Generate 10-25 basic conceptual flashcards based on the following content.\n\n"
            f"Focus on:\n"
            f"- Key definitions and concepts\n"
            f"- Fundamental principles\n"
            f"- Basic terminology\n"
            f"- Simple conceptual understanding\n\n"
            f"AVOID:\n"
            f"- Complex calculations\n"
            f"- Detailed derivations\n"
            f"- Advanced applications\n"
            f"- Step-by-step problem solving\n\n"
            f"Format each flashcard as:\n"
            f"Q: <question>\nA: <answer>\n\n"
            f"Text:\n{text}"
        )
    else:  # In-depth
        prompt = (
            f"Generate comprehensive flashcards at an advanced level based on the following content. Create as many cards as needed to thoroughly cover all important concepts, examples, and applications.\n\n"
            f"Include:\n"
            f"- Detailed conceptual questions\n"
            f"- Step-by-step problem solving\n"
            f"- Mathematical derivations and proofs\n"
            f"- Advanced applications and examples\n"
            f"- Critical thinking questions\n"
            f"- Connections between different concepts\n"
            f"- Common mistakes and misconceptions\n"
            f"- Real-world applications\n"
            f"- All significant theorems, formulas, and methods\n\n"
            f"Use LaTeX for mathematical expressions: $x^2$ for inline, $$\\int_0^1 x^2 dx$$ for display.\n\n"
            f"Format each flashcard as:\n"
            f"Q: <question>\nA: <answer>\n\n"
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
        return ""
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return ""


def parse_flashcards(raw_text):
    """
    Parses GPT-generated flashcard text into a list of (question, answer) tuples.
    Handles multi-line questions and answers with LaTeX math.
    """
    flashcards = []
    current_q = None
    current_a = None
    in_question = False
    in_answer = False

    for line in raw_text.splitlines():
        line = line.strip()
        
        if line.startswith("Q:"):
            # Save previous flashcard if complete
            if current_q and current_a:
                flashcards.append((current_q.strip(), current_a.strip()))
            
            # Start new question
            current_q = line[2:].strip()
            current_a = ""
            in_question = True
            in_answer = False
            
        elif line.startswith("A:"):
            # Switch to answer mode
            in_question = False
            in_answer = True
            current_a = line[2:].strip()
            
        elif line and in_question:
            # Continue building question (for multi-line questions)
            current_q += " " + line
            
        elif line and in_answer:
            # Continue building answer (for multi-line answers)
            current_a += " " + line
    
    # Add the last flashcard if complete
    if current_q and current_a:
        flashcards.append((current_q.strip(), current_a.strip()))

    return flashcards
