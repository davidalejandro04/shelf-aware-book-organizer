import logging
from ebooklib import epub
import fitz

def extract_pdf_metadata(file_path):
    """Extract metadata (title) from a PDF file if available."""
    try:
        doc = fitz.open(file_path)
        metadata = doc.metadata
        doc.close()
        if metadata and "title" in metadata and metadata["title"]:
            return metadata["title"].strip()
        return None
    except Exception as e:
        logging.error(f"Error extracting PDF metadata: {file_path}, {e}")
        return None

def extract_epub_metadata(file_path):
    """Extract metadata (title) from an EPUB file if available."""
    try:
        book = epub.read_epub(file_path)
        # The 'title' is usually stored in the metadata
        # Check the book's metadata
        title = book.get_metadata('DC', 'title')
        if title and len(title) > 0 and title[0][0]:
            return title[0][0].strip()
        return None
    except Exception as e:
        logging.error(f"Error extracting EPUB metadata: {file_path}, {e}")
        return None
