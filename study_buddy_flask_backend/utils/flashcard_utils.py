import csv
import uuid
import tempfile
from io import BytesIO
import genanki


def export_flashcards_to_csv(flashcards):
    """
    Accepts a list of (question, answer) tuples and returns a CSV buffer.
    """
    output = BytesIO()
    writer = csv.writer(output)
    writer.writerow(["Question", "Answer"])
    for q, a in flashcards:
        writer.writerow([q, a])
    output.seek(0)
    return output


def format_latex(text):
    """
    Formats mathematical text to use display-style LaTeX if it contains common math symbols.
    Escapes backslashes to avoid formatting errors.
    """
    text = text.replace("\\", "\\\\")
    if any(sym in text for sym in ["\\int", "\\frac", "^", "_", "\\sum", "\\lim", "\\sqrt"]):
        return f"\\[{text}\\]"
    return text


def export_flashcards_to_apkg(flashcards, deck_name="Study Buddy Deck"):
    """
    Accepts a list of (question, answer) tuples and returns a .apkg buffer using genanki with LaTeX formatting.
    """
    deck_id = int(uuid.uuid4().int >> 64)  # Ensure it's within SQLite INTEGER range

    model = genanki.Model(
        1607392319,
        'Basic Model',
        fields=[
            {"name": "Question"},
            {"name": "Answer"}
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Question}}",
                "afmt": "{{FrontSide}}<hr id='answer'>{{Answer}}"
            }
        ],
        latex_pre=r"""
\documentclass[12pt]{article}
\usepackage{amsmath}
\usepackage{amssymb}
\pagestyle{empty}
\begin{document}
""",
        latex_post=r"\end{document}"
    )

    deck = genanki.Deck(deck_id, deck_name)

    for question, answer in flashcards:
        try:
            note = genanki.Note(
                model=model,
                fields=[format_latex(question), format_latex(answer)]
            )
            deck.add_note(note)
        except Exception as e:
            print(f"⚠️ Skipping flashcard due to error: {e}")

    tmp_path = tempfile.NamedTemporaryFile(suffix=".apkg", delete=False).name
    genanki.Package(deck).write_to_file(tmp_path)

    with open(tmp_path, "rb") as f:
        output = BytesIO(f.read())
    output.seek(0)
    return output
