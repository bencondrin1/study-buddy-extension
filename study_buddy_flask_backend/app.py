from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
import base64
import traceback

from utils.pdf_utils import extract_text_from_pdf
from utils.ocr_utils import extract_text_with_vision
from utils.gpt_utils import generate_study_materials_as_pdf

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/generate_blob', methods=['POST', 'OPTIONS'])
def generate_blob():
    if request.method == 'OPTIONS':
        # Preflight CORS response
        response = app.make_default_options_response()
        headers = response.headers

        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type'
        headers['Access-Control-Allow-Credentials'] = 'true'
        return response

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

        print("🤖 Generating study material PDF...")
        pdf_buffer = generate_study_materials_as_pdf(text, level, output_type)

        pdf_buffer.seek(0)

        # Sanitize for filename
        safe_output_type = output_type.replace(" ", "_").lower()
        safe_level = level.replace(" ", "_").lower()
        filename = f"{safe_output_type}_{safe_level}.pdf"

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename,
            conditional=False
        )

    except Exception as e:
        print(f"❌ Internal server error: {e}")
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5050)
