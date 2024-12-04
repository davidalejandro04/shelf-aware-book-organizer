import os
import re
import argparse
from shutil import move
from tqdm import tqdm
from PIL import Image
import fitz  # PyMuPDF
from ebooklib import epub
import pytesseract
import ollama
import io
import multiprocessing
import logging


class Config:
    """Configuration parameters for the BookRenamer."""

    def __init__(self):
        self.model_name = "llama3.2"
        self.default_subjects = [
            "Physics", "Math", "Computer Science", "Electronic Engineering",
            "History", "Philosophy", "Literature", "Art",
            "Social Sciences", "Sciences", "Other"
        ]
        self.pages_to_read_pdf = 15
        self.pages_to_read_ocr = 5
        self.text_snippet_length = 3000
        self.max_title_length = 100
        self.log_level = logging.INFO  # Set to DEBUG for more detailed logs


class BookRenamer:
    def __init__(self, config):
        """
        Initialize the BookRenamer class with the Ollama model and configuration.
        """
        self.config = config
        self.ollama_model = self.load_model()
        self.setup_logging()

    def setup_logging(self):
        """Configure logging for the application."""
        logging.basicConfig(
            level=self.config.log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def load_model(self):
        """Load the Ollama model. Ensure it is loaded only once."""
        logging.info(f"Loading Ollama model: {self.config.model_name}")
        return self.config.model_name

    def preprocess_text(self, text):
        """Clean up text by removing artifacts, line breaks, and non-ASCII characters."""
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
        """Extract text from the first `pages` pages of a PDF using OCR and PyMuPDF."""
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
        """Extract text from a PDF, falling back to OCR if necessary."""
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
                # Check if the item is a document (typically XHTML/HTML content)
                if item.get_type() == 9:  # 9 corresponds to document type in ebooklib
                    content = item.get_content().decode('utf-8', errors='ignore')
                    text += content
            return self.preprocess_text(text)
        except Exception as e:
            logging.error(f"Error reading EPUB: {file_path}, {e}")
            return ""

    def infer_title(self, text):
        """
        Infer the title of a book using the Ollama model, with chain-of-thought reasoning
        and fallback logic for missing or vague titles.
        """
        prompt = f"""
You are an expert in analyzing text to infer the title of books or documents. Follow these steps carefully:

Steps:
1. Analyze the text to identify key terms, recurring phrases, or headers that could indicate the title.
2. If an explicit title is found, extract it.
3. If no explicit title is mentioned, generate a concise and descriptive title based on the main topic or focus of the text.
4. Ensure the title is informative, avoids generic terms like "Document" or "Untitled," and uses a professional tone.

Text to analyze:
"{text[:self.config.text_snippet_length]}"

Respond ONLY with the inferred title. If it is not possible to determine a title, generate one based on the text's content and focus.
"""
        try:
            response = ollama.generate(
                model=self.ollama_model,
                prompt=prompt,
                options={"temperature": 0.2, "max_tokens": 50}
            )
            title = response["response"].strip()

            # Handle cases where the model indicates no explicit title is available
            if not title or any(phrase in title.lower() for phrase in [
                "no explicit title", "unable to determine", "cannot find title", "untitled"
            ]):
                logging.info("Explicit title not found. Inferring a fallback title based on text content.")
                fallback_prompt = f"""
Based on the text, generate a concise fallback title that reflects the main subject or theme of the text:
"{text[:self.config.text_snippet_length]}"

Ensure the title is concise, descriptive, and appropriate for the content. Avoid generic terms like "Document."
"""
                fallback_response = ollama.generate(
                    model=self.ollama_model,
                    prompt=fallback_prompt,
                    options={"temperature": 0.2, "max_tokens": 50}
                )
                title = fallback_response["response"].strip()

            # Sanitize the title
            title = re.sub(r'[\\/*?:"<>|]', "", title).replace("\n", " ").strip()
            title = title[:self.config.max_title_length] if title else "Untitled"
            return title
        except Exception as e:
            logging.error(f"Error inferring title: {e}")
            return "Untitled"

    def infer_subject(self, text):
        """
        Infer the subject of a book based on its text using chain-of-thought reasoning
        for more robust analysis.
        """
        prompt = f"""
You are an expert in classifying academic and general texts. Follow these steps to classify the text into one of these categories:
- {', '.join(self.config.default_subjects)}

Steps:
1. Analyze the text to identify key concepts, terms, and any recurring themes.
2. Determine the primary focus of the text based on these concepts and themes.
3. Match the focus to the most appropriate category from the list provided. If the focus is unclear or doesn't match, categorize as "Other."

Text to analyze:
"{text[:self.config.text_snippet_length]}"

Respond ONLY with the category name, without any further explanation.
"""
        try:
            response = ollama.generate(
                model=self.ollama_model,
                prompt=prompt,
                options={"temperature": 0.1, "max_tokens": 20}
            )

            subject = response["response"].strip()

            # Validate the response against predefined categories
            if subject in self.config.default_subjects:
                return subject
            else:
                logging.warning(f"Unexpected category detected: {subject}. Defaulting to 'Other'.")
                return "Other"
        except Exception as e:
            logging.error(f"Error inferring subject: {e}")
            return "Other"

    def rename_file(self, args):
        """Process and rename a single file."""
        file_path, renamed_path, not_renamed_path = args
        file_name = os.path.basename(file_path)
        try:
            if os.path.isfile(file_path):
                text = ""
                if file_name.lower().endswith(".pdf"):
                    text = self.extract_text_from_pdf(file_path)
                elif file_name.lower().endswith(".epub"):
                    text = self.extract_text_from_epub(file_path)
                else:
                    return

                if text:
                    new_title = self.infer_title(text)
                    extension = os.path.splitext(file_name)[1]
                    new_file_name = f"{new_title}{extension}"
                    new_file_path = os.path.join(renamed_path, new_file_name)

                    # Ensure unique filename
                    counter = 1
                    original_new_file_name = new_file_name
                    while os.path.exists(new_file_path):
                        new_file_name = f"{new_title}_{counter}{extension}"
                        new_file_path = os.path.join(renamed_path, new_file_name)
                        counter += 1

                    os.rename(file_path, new_file_path)

                    # Categorize the book based on its subject
                    subject = self.infer_subject(text)
                    category_folder = os.path.join(renamed_path, subject)
                    os.makedirs(category_folder, exist_ok=True)

                    final_file_path = os.path.join(category_folder, new_file_name)

                    # Ensure unique filename in category folder
                    counter = 1
                    while os.path.exists(final_file_path):
                        new_file_name = f"{new_title}_{counter}{extension}"
                        final_file_path = os.path.join(category_folder, new_file_name)
                        counter += 1

                    move(new_file_path, final_file_path)
                else:
                    move(file_path, os.path.join(not_renamed_path, file_name))
        except Exception as e:
            logging.error(f"Error processing file '{file_name}': {e}")
            move(file_path, os.path.join(not_renamed_path, file_name))

    def rename_files_in_folder(self, folder_path):
        """
        Rename all supported files in a folder based on their inferred title and
        organize by topics using multiprocessing for efficiency.
        """
        not_renamed_path = os.path.join(folder_path, "Not renamed")
        renamed_path = os.path.join(folder_path, "Renamed")
        os.makedirs(not_renamed_path, exist_ok=True)
        os.makedirs(renamed_path, exist_ok=True)

        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]
        tasks = [
            (file_path, renamed_path, not_renamed_path)
            for file_path in files
            if os.path.isfile(file_path) and file_path.lower().endswith(('.pdf', '.epub'))
        ]

        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            list(tqdm(pool.imap_unordered(self.rename_file, tasks), total=len(tasks), desc="Processing Files"))


def main():
    parser = argparse.ArgumentParser(description='Rename books and categorize them based on their content.')
    parser.add_argument('folder', nargs='?', default='.', help='Folder path containing the files (default: current directory)')
    parser.add_argument('--model', default='llama3.2', help='Ollama model to use (default: llama3.2)')
    parser.add_argument('--log', default='INFO', help='Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--pages', type=int, default=15, help='Number of pages to read from PDFs (default: 15)')
    parser.add_argument('--ocr_pages', type=int, default=5, help='Number of pages to read using OCR (default: 5)')
    args = parser.parse_args()
    folder_path = args.folder

    if os.path.isdir(folder_path):
        config = Config()
        config.model_name = args.model
        config.log_level = getattr(logging, args.log.upper(), logging.INFO)
        config.pages_to_read_pdf = args.pages
        config.pages_to_read_ocr = args.ocr_pages

        renamer = BookRenamer(config)
        renamer.rename_files_in_folder(folder_path)
    else:
        print("Invalid folder path.")


if __name__ == "__main__":
    main()
