from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
import base64
import traceback

from utils.pdf_utils import extract_text_from_pdf
from utils.ocr_utils import extract_text_with_vision
from utils.gpt_utils import generate_study_materials_as_pdf  # <- must return BytesIO

app = Flask(__name__)

# Allow Chrome Extension origin
CORS(app, origins=["chrome-extension://ehmbcgoamlbnggoeapgglllpahhlhbha"], supports_credentials=True)

@app.route('/generate_blob', methods=['POST'])
def generate_blob():
    try:
        data = request.get_json()
        pdf_base64 = data.get('pdf_base64')
        level = data.get('level', 'Intermediate')
        output_type = data.get('output_type', 'Study Guide')

        if not pdf_base64:
            return jsonify({"error": "No PDF data provided"}), 400

        pdf_bytes = base64.b64decode(pdf_base64)
        pdf_io = BytesIO(pdf_bytes)

        print("📖 Extracting text from PDF blob...")
        text = extract_text_from_pdf(pdf_io)

        if not text.strip():
            print("🔍 No extractable text found, using OCR fallback...")
            pdf_io.seek(0)
            text = extract_text_with_vision(pdf_io.read())

        if not text.strip():
            return jsonify({"error": "No text could be extracted from PDF"}), 400

        print("🤖 Sending extracted text to GPT...")
        result_pdf = generate_study_materials_as_pdf(text, level, output_type)

        return send_file(result_pdf, download_name="study_material.pdf", mimetype="application/pdf")

    except Exception as e:
        print(f"❌ Internal server error: {e}")
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5050)
