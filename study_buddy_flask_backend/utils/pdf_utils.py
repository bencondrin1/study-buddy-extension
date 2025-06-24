# utils/pdf_utils.py
import requests
from PyPDF2 import PdfReader
from io import BytesIO

def download_pdf(url):
    response = requests.get(url)
    response.raise_for_status()

    if "pdf" not in response.headers.get("Content-Type", "").lower():
        print("⚠️ Warning: Content may not be PDF")

    return BytesIO(response.content)

def extract_text_from_pdf(pdf_io):
    reader = PdfReader(pdf_io)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text
