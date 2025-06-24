from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.pdf_utils import extract_text_from_pdf, download_pdf
from utils.ocr_utils import extract_text_with_vision
from utils.gpt_utils import generate_study_materials

app = Flask(__name__)

# CORS CONFIG: Allow your Chrome Extension to access Flask
CORS(app, origins=["chrome-extension://ehmbcgoamlbnggoeapgglllpahhlhbha"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"])

# Manually add CORS headers to every response
@app.after_request
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "chrome-extension://ehmbcgoamlbnggoeapgglllpahhlhbha")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

@app.route('/generate', methods=['OPTIONS', 'POST'])
def generate():
    # CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'message': 'CORS preflight'}), 200

    data = request.get_json()
    pdf_urls = data.get('pdf_urls')
    level = data.get('level', 'Intermediate')
    output_type = data.get('output_type', 'Study Guide')

    if not pdf_urls or not isinstance(pdf_urls, list):
        return jsonify({"error": "No pdf_urls array provided"}), 400

    combined_text = ""
    for idx, url in enumerate(pdf_urls):
        try:
            pdf_bytes_io = download_pdf(url)
            text = extract_text_from_pdf(pdf_bytes_io)
            if not text.strip():
                pdf_bytes_io.seek(0)
                text = extract_text_with_vision(pdf_bytes_io.read())
            combined_text += text + "\n"
        except Exception as e:
            return jsonify({"error": f"Failed to process PDF URL index {idx}: {str(e)}"}), 500

    if not combined_text.strip():
        return jsonify({"error": "No text extracted from provided PDFs"}), 400

    result = generate_study_materials(combined_text, level, output_type)
    return jsonify({"message": result})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
