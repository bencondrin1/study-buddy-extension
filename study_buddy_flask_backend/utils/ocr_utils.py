# utils/ocr_utils.py

import os
from dotenv import load_dotenv
from google.cloud import vision
from google.api_core.exceptions import GoogleAPIError
from PIL import Image
import io
import tempfile
import fitz  # type: ignore  # PyMuPDF for PDF image extraction
import requests
import base64

# Load .env from the gpt folder
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'utils', '.env'))

# Load .env from the gpt folder (for MathPix keys too)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'gpt', '.env'))

# Set credentials if using service account JSON
creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if creds_path is not None:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path

# Initialize Vision client
try:
    vision_client = vision.ImageAnnotatorClient()
except Exception as e:
    vision_client = None
    print(f"[OCR] Google Vision client not initialized: {e}")

def ocr_image(image_bytes):
    """Run OCR on a single image (bytes) using Google Cloud Vision."""
    if not vision_client:
        return "[OCR fallback: Vision client not available]"
    try:
        image = vision.Image(content=image_bytes)
        # The linter may not recognize document_text_detection, but it is correct for Google Vision
        response = vision_client.document_text_detection(image=image)  # type: ignore[attr-defined]
        if response.error.message:
            return f"[OCR error: {response.error.message}]"
        return response.full_text_annotation.text.strip()
    except GoogleAPIError as e:
        return f"[OCR API error: {e}]"
    except Exception as e:
        return f"[OCR error: {e}]"

def extract_text_with_vision(pdf_bytes):
    """Extract text from a PDF (bytes) using Google Vision OCR on each page image."""
    if not vision_client:
        return "[OCR fallback: Vision client not available]"
    try:
        # Save PDF to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            tmp_pdf_path = tmp_pdf.name
        doc = fitz.open(tmp_pdf_path)
        all_text = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            text = ocr_image(img_bytes)
            all_text.append(f"[Page {page_num+1}]\n{text}")
        doc.close()
        os.remove(tmp_pdf_path)
        return '\n\n'.join(all_text)
    except Exception as e:
        return f"[OCR error: {e}]"

# MathPix OCR for handwritten math
# Usage: latex = mathpix_ocr('path/to/image.png')
def mathpix_ocr(image_path):
    """
    Use MathPix API to extract LaTeX from a handwritten math image.
    Returns the LaTeX string or an error message.
    """
    app_id = os.getenv("MATHPIX_APP_ID")
    app_key = os.getenv("MATHPIX_APP_KEY")
    if not app_id or not app_key:
        return "[MathPix credentials not set in .env]"
    with open(image_path, "rb") as image_file:
        img_base64 = base64.b64encode(image_file.read()).decode()
    headers = {
        "app_id": app_id,
        "app_key": app_key,
        "Content-type": "application/json"
    }
    data = {
        "src": f"data:image/png;base64,{img_base64}",
        "formats": ["latex_styled"],
        "ocr": ["math", "text"]
    }
    response = requests.post("https://api.mathpix.com/v3/text", json=data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return result.get("latex_styled", "[No LaTeX found]")
    else:
        return f"[MathPix error: {response.status_code} {response.text}]"
