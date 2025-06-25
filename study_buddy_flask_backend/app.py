from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from io import BytesIO
import base64
import traceback

from utils.pdf_utils import extract_text_from_pdf
from utils.ocr_utils import extract_text_with_vision
from utils.gpt_utils import generate_study_materials

app = Flask(__name__)

# Apply CORS globally and ensure it works for all routes
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/generate_blob', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'], methods=['POST', 'OPTIONS'])
def generate_blob():
    if request.method == 'OPTIONS':
        # Manually handle preflight with correct headers
        response = jsonify({'message': 'Preflight OK'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200

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
        result = generate_study_materials(text, level, output_type)

        return jsonify({"message": result}), 200

    except Exception as e:
        print(f"❌ Internal server error: {e}")
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug=True, port=5050)
