# utils/flashcard_utils.py

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

def export_flashcards_to_apkg(flashcards, deck_name="Study Buddy Deck"):
    """
    Accepts a list of (question, answer) tuples and returns a .apkg buffer using genanki.
    """
    deck_id = int(uuid.uuid4()) >> 64
    model = genanki.Model(
        1607392319,
        'Basic Model',
        fields=[{"name": "Question"}, {"name": "Answer"}],
        templates=[{
            "name": "Card 1",
            "qfmt": "{{Question}}",
            "afmt": "{{FrontSide}}<hr id='answer'>{{Answer}}",
        }]
    )

    deck = genanki.Deck(deck_id, deck_name)

    for question, answer in flashcards:
        note = genanki.Note(model=model, fields=[question, answer])
        deck.add_note(note)

    tmp_path = tempfile.NamedTemporaryFile(suffix=".apkg", delete=False).name
    genanki.Package(deck).write_to_file(tmp_path)

    with open(tmp_path, "rb") as f:
        output = BytesIO(f.read())
    output.seek(0)
    return output
