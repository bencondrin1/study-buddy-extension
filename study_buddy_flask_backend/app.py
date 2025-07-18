from dotenv import load_dotenv
import os

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils', '.env'))
load_dotenv(dotenv_path=dotenv_path)

# Now import everything else
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
import base64
import traceback
import atexit
import multiprocessing

# Utilities
from utils.pdf_utils import extract_text_from_pdf
from utils.ocr_utils import extract_text_with_vision
from utils.flashcard_utils import export_flashcards_to_pdf, export_flashcards_to_anki_apkg
from utils.gpt.flashcards import generate_flashcards, parse_flashcards
from utils.gpt.study_guide import generate_study_materials_as_pdf
from utils.gpt.practice_exam import generate_practice_exam, parse_practice_exam, export_practice_exam_to_pdf
from utils.gpt.diagrams import generate_diagrams_as_pdf

# Flask setup
app = Flask(__name__)
CORS(app, origins=["chrome-extension://ehmbcgoamlbnggoeapgglllpahhlhbha"])

# Suppress multiprocessing warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="multiprocessing.resource_tracker")

# Cleanup function for multiprocessing resources
def cleanup_resources():
    try:
        # Force garbage collection
        import gc
        gc.collect()
    except:
        pass

# Register cleanup function
atexit.register(cleanup_resources)


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
        file_type = data.get("file_type", "pdf")

        if not pdf_base64:
            return jsonify({"error": "No PDF data provided"}), 400

        pdf_bytes = base64.b64decode(pdf_base64)
        text = fallback_extract_text(pdf_bytes)

        raw_output = generate_flashcards(text, level)
        flashcards = parse_flashcards(raw_output)

        if not flashcards:
            return jsonify({"error": "No flashcards parsed"}), 500

        if file_type == "pdf":
            buffer = export_flashcards_to_pdf(flashcards)
            mimetype = "application/pdf"
            filename = "flashcards.pdf"
        elif file_type == "anki":
            buffer = export_flashcards_to_anki_apkg(flashcards)
            mimetype = "application/x-apkg"
            filename = "flashcards_for_anki.apkg"
        elif file_type == "copy":
            # Return flashcards as JSON for clipboard copying
            return jsonify({
                "flashcards": [{"question": q, "answer": a} for q, a in flashcards],
                "message": "Flashcards ready for clipboard"
            })
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
        diagram_type = data.get("diagram_type", "general")
        handwritten = data.get("handwritten", False)  # <--- NEW

        print(f"[DEBUG] Handwritten flag: {handwritten}")

        if not pdf_base64:
            return jsonify({"error": "No PDF data provided"}), 400

        pdf_bytes = base64.b64decode(pdf_base64)
        text = fallback_extract_text(pdf_bytes)

        print(f"[DEBUG] First 500 chars of OCR output:\n{text[:500]}")

        print(f"🧠 Generating {output_type} ({level})... Handwritten: {handwritten}")
        
        if output_type == "Diagrams":
            pdf_buffer = generate_diagrams_as_pdf(text, level, diagram_type)
            filename = "diagrams.pdf"
        else:
            # Pass handwritten flag to study guide generator
            pdf_buffer = generate_study_materials_as_pdf(text, level, output_type, handwritten=handwritten)
            filename = "study_materials.pdf"

            # Try to print the first 500 chars of the GPT output (study guide)
            try:
                pdf_buffer.seek(0)
                # Not possible to print PDF content directly, but we can print the raw_md if we modify generate_study_materials_as_pdf to return it for debugging
                # For now, just print a placeholder
                print(f"[DEBUG] Study guide PDF generated (cannot print PDF content directly)")
            except Exception as e:
                print(f"[DEBUG] Error printing GPT output: {e}")

        # Save a copy to disk for debugging
        output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', filename))
        with open(output_path, 'wb') as f:
            f.write(pdf_buffer.getbuffer())
        print(f"✅ PDF also saved at {output_path}")

        # Reset buffer position for send_file
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ========== Practice Exam ==========
@app.route("/generate_practice_exam", methods=["POST", "OPTIONS"])
def generate_practice_exam_endpoint():
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()
        pdf_base64 = data.get("pdf_base64")
        level = data.get("level", "Basic")
        exam_type = data.get("exam_type", "Mixed")
        file_type = data.get("file_type", "json")

        if not pdf_base64:
            return jsonify({"error": "No PDF data provided"}), 400

        pdf_bytes = base64.b64decode(pdf_base64)
        text = fallback_extract_text(pdf_bytes)

        print(f"📝 Generating Practice Exam ({level}, {exam_type})...")
        raw_output = generate_practice_exam(text, level, exam_type)
        exam_data = parse_practice_exam(raw_output)

        if not exam_data:
            return jsonify({"error": "No practice exam generated"}), 500

        if file_type == "json":
            # Return structured exam data as JSON
            return jsonify({
                "exam_data": exam_data,
                "level": level,
                "exam_type": exam_type,
                "message": "Practice exam generated successfully"
            })
        elif file_type == "pdf":
            # Generate PDF from raw output
            pdf_buffer = export_practice_exam_to_pdf(raw_output, level, exam_type)
            return send_file(
                pdf_buffer,
                mimetype="application/pdf",
                as_attachment=True,
                download_name="practice_exam.pdf"
            )
        else:
            return jsonify({"error": "Unsupported file type"}), 400

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ========== Run ==========
if __name__ == "__main__":
    app.run(debug=True, port=5050)
