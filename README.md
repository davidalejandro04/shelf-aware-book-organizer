# Book Renamer and Organizer

This project is a Python-based tool designed to process and organize digital books (PDF and EPUB formats). It uses advanced AI models to infer book titles and subjects based on their content and organizes them into structured directories. The tool supports Optical Character Recognition (OCR) for PDFs without embedded text and handles metadata extraction for EPUB files.

---

## Features

- **Title Inference**: Automatically extracts or infers the title of books using AI models (e.g., Ollama).
- **Subject Categorization**: Classifies books into predefined subjects like Physics, Math, Computer Science, etc.
- **PDF Text Extraction**: Uses PyMuPDF for extracting text directly from PDFs.
- **OCR Support**: Processes scanned PDFs with Tesseract OCR.
- **EPUB Text Extraction**: Reads and extracts text from EPUB documents.
- **File Organization**: Renames books based on inferred titles and categorizes them into subject-specific folders.
- **Conflict Handling**: Ensures files with duplicate titles are uniquely named.
- **Parallel Processing**: Speeds up processing by using multiprocessing for large datasets.
- **Error Handling**: Logs detailed errors for debugging and moves problematic files to a `Not renamed` folder.

---

## Requirements

### Python Version

- Python 3.7 or newer

### Python Libraries

Install the required libraries using pip:

```bash
pip install -r requirements.txt
```


requirements.txt:

pymupdf
ebooklib
pytesseract
pillow
ollama
tqdm

External Tools

    Tesseract OCR (Required for OCR on scanned PDFs):
        Install from Tesseract GitHub and ensure it is added to your system PATH.

    Ghostscript (Optional for additional PDF processing):
        Install via your package manager (brew install ghostscript on macOS or sudo apt install ghostscript on Linux).

Installation

    Clone the Repository:

git clone https://github.com/yourusername/book-renamer.git
cd book-renamer

Install Dependencies:

pip install -r requirements.txt

Verify Tesseract Installation:

Ensure Tesseract is installed and accessible from the command line:

    tesseract --version

Usage

Run the script from the command line with the following command:

python renamebooks.py /path/to/books

Optional Arguments

    --model: Specify the AI model to use (default: llama3.2).
    --log: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default is INFO.
    --pages: Number of pages to read from PDFs for text extraction. Default is 15.
    --ocr_pages: Number of pages to process with OCR. Default is 5.

Example:

python renamebooks.py /path/to/books --model llama4.0 --log DEBUG --pages 20

Folder Structure

    Input Folder: Specify a folder containing PDFs and EPUBs to process.
    Output Folders:
        Renamed/: Contains renamed files organized into subject-specific folders.
        Not renamed/: Contains files that couldn't be processed or renamed.

Features in Detail

    Title Inference:
        Extracts titles from document metadata or generates them using AI.
        Handles edge cases where explicit titles are not present.

    Subject Categorization:
        Assigns each book to a subject like Physics, Math, History, etc.
        Uses AI reasoning to classify based on content.

    Conflict Resolution:
        Ensures unique filenames by appending counters for duplicates.

    Error Handling:
        Moves unprocessable files to a Not renamed folder for review.

Contributing

Contributions are welcome! To contribute:

    Fork the repository.

    Create a feature branch:

git checkout -b feature-name

Commit changes and push:

    git add .
    git commit -m "Add feature description"
    git push origin feature-name

    Open a pull request.

License

This project is licensed under the MIT License. See the LICENSE file for details.
