import re
import logging
import io
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from ebooklib import epub

class TextExtractor:
    def __init__(self, config):
        self.config = config

    def preprocess_text(self, text):
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces or line breaks with a single space
        text = text.strip()  # Trim leading and trailing whitespace
        return text

    def extract_text_with_pymupdf(self, file_path, pages):
        """Extract text from the first `pages` pages of a PDF using PyMuPDF."""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page_num in range(min(pages, len(doc))):
                page = doc[page_num]
                text += page.get_text("text")
            doc.close()
            return self.preprocess_text(text)
        except Exception as e:
            logging.error(f"Error reading PDF with PyMuPDF: {file_path}, {e}")
            return ""

    def extract_text_with_ocr(self, file_path, pages):
        """Extract text from PDF pages using OCR."""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page_num in range(min(pages, len(doc))):
                page = doc[page_num]
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                text += pytesseract.image_to_string(img)
            doc.close()
            return self.preprocess_text(text)
        except Exception as e:
            logging.error(f"Error performing OCR on PDF: {file_path}, {e}")
            return ""

    def extract_text_from_pdf(self, file_path):
        """Extract text from a PDF, fallback to OCR if no text."""
        text = self.extract_text_with_pymupdf(file_path, self.config.pages_to_read_pdf)
        if not text.strip():
            logging.info(f"Falling back to OCR for: {file_path}")
            text = self.extract_text_with_ocr(file_path, self.config.pages_to_read_ocr)
        return text

    def extract_text_from_epub(self, file_path):
        """Extract text from an EPUB file."""
        try:
            book = epub.read_epub(file_path)
            text = ""
            for item in book.get_items():
                if item.get_type() == 9:  # document type
                    content = item.get_content().decode('utf-8', errors='ignore')
                    text += content
            return self.preprocess_text(text)
        except Exception as e:
            logging.error(f"Error reading EPUB: {file_path}, {e}")
            return ""
