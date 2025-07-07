# utils/gpt/flashcards.py

import os
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
client = OpenAI(api_key=api_key)


def generate_flashcards(text, level="Basic"):
    """
    Uses GPT to generate raw flashcard text in Q/A format.
    """
    level = level.lower()
    
    if level == "basic":
        prompt = (
            f"Generate a set of basic conceptual flashcards based on the following content.\n\n"
            f"Focus ONLY on:\n"
            f"- The most essential definitions and concepts\n"
            f"- Fundamental principles\n"
            f"- Basic terminology\n"
            f"- Simple, high-level understanding\n\n"
            f"Do NOT include detailed examples, advanced applications, or step-by-step solutions.\n"
            f"Imagine this is for a test that only covers the basic overview of the material.\n\n"
            f"Format each flashcard as:\n"
            f"Q: <question>\nA: <answer>\n\n"
            f"Text:\n{text}"
        )
    else:  # In-depth
        prompt = (
            f"Generate a comprehensive, exhaustive set of in-depth flashcards based on the following content.\n\n"
            f"Your goal is to cover EVERYTHING that could reasonably appear on a thorough test of these notes.\n"
            f"You MUST generate at least 2-4x as many flashcards as you would for a basic set.\n"
            f"Be exhaustive: include every important concept, definition, principle, example, application, problem type, step-by-step solution, derivation, proof, formula, common mistake, misconception, subtle point, connection, and real-world application.\n"
            f"If in doubt, add more cards. Err on the side of being too comprehensive.\n"
            f"Imagine you are preparing someone for a comprehensive exam on this material.\n"
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
        content = response.choices[0].message.content
        return content.strip() if content else ""

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
