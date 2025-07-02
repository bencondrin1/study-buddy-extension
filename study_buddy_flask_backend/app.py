# app.py

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
import base64
import traceback

from utils.pdf_utils import extract_text_from_pdf
from utils.ocr_utils import extract_text_with_vision
from utils.gpt_utils import generate_flashcards, parse_flashcards
from utils.flashcard_utils import export_flashcards_to_csv, export_flashcards_to_apkg

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/generate_flashcards', methods=['POST'])
def generate_flashcards_endpoint():
    try:
        data = request.get_json()
        pdf_base64 = data.get('pdf_base64')
        level = data.get('level', 'Basic')
        file_type = data.get('file_type', 'csv')

        if not pdf_base64:
            return jsonify({"error": "No PDF data provided"}), 400

        pdf_bytes = base64.b64decode(pdf_base64)
        text = extract_text_from_pdf(BytesIO(pdf_bytes))

        if not text.strip():
            print("🔍 No extractable text found. Trying OCR fallback...")
            text = extract_text_with_vision(pdf_bytes)

        print(f"📚 Generating flashcards ({level}, {file_type})...")
        raw_gpt_output = generate_flashcards(text, level)
        flashcards = parse_flashcards(raw_gpt_output)

        if not flashcards:
            return jsonify({"error": "Failed to parse flashcards"}), 500

        if file_type.lower() == 'csv':
            buffer = export_flashcards_to_csv(flashcards)
            mimetype = 'text/csv'
            filename = 'flashcards.csv'
        elif file_type.lower() == 'apkg':
            buffer = export_flashcards_to_apkg(flashcards)
            mimetype = 'application/octet-stream'
            filename = 'flashcards.apkg'
        else:
            return jsonify({"error": f"Unsupported file type: {file_type}"}), 400

        return send_file(
            buffer,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        print(f"❌ Server error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5050)
