from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.pdf_utils import extract_text_from_pdf, download_pdf
from utils.ocr_utils import extract_text_with_vision
from utils.gpt_utils import generate_study_materials

app = Flask(__name__)

# Allow Chrome extension access
CORS(app, origins=["chrome-extension://ehmbcgoamlbnggoeapgglllpahhlhbha"],
     supports_credentials=True)

@app.after_request
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "chrome-extension://ehmbcgoamlbnggoeapgglllpahhlhbha")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

@app.route('/generate', methods=['OPTIONS', 'POST'])
def generate():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'CORS preflight'}), 200

    try:
        data = request.get_json()
        pdf_urls = data.get('pdf_urls')
        level = data.get('level', 'Intermediate')
        output_type = data.get('output_type', 'Study Guide')

        if not pdf_urls or not isinstance(pdf_urls, list):
            return jsonify({"error": "No valid pdf_urls array provided"}), 400

        combined_text = ""
        for idx, url in enumerate(pdf_urls):
            try:
                print(f"📥 Downloading PDF index {idx}: {url}")
                pdf_bytes_io = download_pdf(url)

                print(f"📖 Extracting text from PDF index {idx}")
                text = extract_text_from_pdf(pdf_bytes_io)

                if not text.strip():
                    print(f"🔍 No extractable text, falling back to OCR for PDF index {idx}")
                    pdf_bytes_io.seek(0)
                    text = extract_text_with_vision(pdf_bytes_io.read())

                combined_text += text + "\n"

            except Exception as e:
                print(f"❌ Failed to process PDF index {idx}: {e}")
                return jsonify({"error": f"Failed to process PDF index {idx}: {e}"}), 500

        if not combined_text.strip():
            return jsonify({"error": "No text extracted from any provided PDFs"}), 400

        print(f"🤖 Sending extracted text to GPT for generation...")
        result = generate_study_materials(combined_text, level, output_type)
        return jsonify({"message": result})

    except Exception as e:
        print(f"❌ General backend error: {e}")
        return jsonify({"error": f"Internal server error: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)