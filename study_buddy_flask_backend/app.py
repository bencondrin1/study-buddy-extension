from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
import base64
import traceback

# Utilities
from utils.pdf_utils import extract_text_from_pdf
from utils.ocr_utils import extract_text_with_vision
from utils.flashcard_utils import export_flashcards_to_csv, export_flashcards_to_apkg
from utils.gpt.flashcards import generate_flashcards, parse_flashcards
from utils.gpt.study_guide import generate_study_materials_as_pdf

# Flask setup
app = Flask(__name__)
CORS(app, origins=["chrome-extension://ehmbcgoamlbnggoeapgglllpahhlhbha"])

def fallback_extract_text(pdf_bytes):
    text = extract_text_from_pdf(BytesIO(pdf_bytes))
    if not text.strip():
        print("🔍 No extractable text — using OCR fallback...")
        text = extract_text_with_vision(pdf_bytes)
    return text

# ========== Flashcards ==========
@app.route("/generate_flashcards", methods=["POST", "OPTIONS"])
def generate_flashcards_endpoint():
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()
        pdf_base64 = data.get("pdf_base64")
        level = data.get("level", "Basic")
        file_type = data.get("file_type", "csv")

        if not pdf_base64:
            return jsonify({"error": "No PDF data provided"}), 400

        pdf_bytes = base64.b64decode(pdf_base64)
        text = fallback_extract_text(pdf_bytes)

        raw_output = generate_flashcards(text, level)
        flashcards = parse_flashcards(raw_output)

        if not flashcards:
            return jsonify({"error": "No flashcards parsed"}), 500

        if file_type == "csv":
            buffer = export_flashcards_to_csv(flashcards)
            mimetype = "text/csv"
            filename = "flashcards.csv"
        elif file_type == "apkg":
            buffer = export_flashcards_to_apkg(flashcards)
            mimetype = "application/octet-stream"
            filename = "flashcards.apkg"
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        return send_file(buffer, mimetype=mimetype, as_attachment=True, download_name=filename)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ========== Study Guide / Diagram / Exam ==========
@app.route("/generate_blob", methods=["POST", "OPTIONS"])
def generate_blob_endpoint():
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()
        pdf_base64 = data.get("pdf_base64")
        level = data.get("level", "Basic")
        output_type = data.get("output_type", "Study Guide")

        if not pdf_base64:
            return jsonify({"error": "No PDF data provided"}), 400

        pdf_bytes = base64.b64decode(pdf_base64)
        text = fallback_extract_text(pdf_bytes)

        print(f"🧠 Generating {output_type} ({level})...")
        pdf_buffer = generate_study_materials_as_pdf(text, level, output_type)

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="study_materials.pdf",
        )

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ========== Run ==========
if __name__ == "__main__":
    app.run(debug=True, port=5050)
