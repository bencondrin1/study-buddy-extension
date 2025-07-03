# utils/pdf_utils.py
import requests
from PyPDF2 import PdfReader

from io import BytesIO

def download_pdf(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    with requests.Session() as session:
        response = session.get(url, headers=headers, allow_redirects=True)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()
        if "pdf" not in content_type:
            print("⚠️ Warning: Content may not be PDF (got Content-Type: " + content_type + ")")

        # Heuristic: check if the response is probably a valid PDF
        if not response.content.startswith(b'%PDF'):
            raise ValueError("Downloaded content does not appear to be a valid PDF")

        return BytesIO(response.content)


def extract_text_from_pdf(pdf_io):
    try:
        reader = PdfReader(pdf_io)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"❌ PDF parsing failed: {e}")
        return ""
