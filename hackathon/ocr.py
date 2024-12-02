from pytesseract import image_to_string
from pdf2image import convert_from_path

def ocr_answer_sheet(pdf_path):
    # Convert PDF to images and extract text using Tesseract OCR
    images = convert_from_path(pdf_path)
    text = ""
    for img in images:
        text += image_to_string(img)
    return text
