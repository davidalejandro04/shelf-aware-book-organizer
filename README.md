
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

**`requirements.txt`**:

```plaintext
pymupdf
ebooklib
pytesseract
pillow
ollama
tqdm
```

### External Tools

1. **Tesseract OCR** (Required for OCR on scanned PDFs):
   - Install from [Tesseract GitHub](https://github.com/tesseract-ocr/tesseract) and ensure it is added to your system PATH.

2. **Ghostscript** (Optional for additional PDF processing):
   - Install via your package manager (`brew install ghostscript` on macOS or `sudo apt install ghostscript` on Linux).

---

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/book-renamer.git
   cd book-renamer
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Tesseract Installation**:

   Ensure Tesseract is installed and accessible from the command line:

   ```bash
   tesseract --version
   ```

---

## Usage

Run the script from the command line with the following command:

```bash
python renamebooks.py /path/to/books
```

### Optional Arguments

- **`--model`**: Specify the AI model to use (default: `llama3.2`).
- **`--log`**: Set the logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). Default is `INFO`.
- **`--pages`**: Number of pages to read from PDFs for text extraction. Default is 15.
- **`--ocr_pages`**: Number of pages to process with OCR. Default is 5.

Example:

```bash
python renamebooks.py /path/to/books --model llama4.0 --log DEBUG --pages 20
```

---

## Folder Structure

- **Input Folder**: Specify a folder containing PDFs and EPUBs to process.
- **Output Folders**:
  - `Renamed/`: Contains renamed files organized into subject-specific folders.
  - `Not renamed/`: Contains files that couldn't be processed or renamed.

---

## Features in Detail

1. **Title Inference**:
   - Extracts titles from document metadata or generates them using AI.
   - Handles edge cases where explicit titles are not present.

2. **Subject Categorization**:
   - Assigns each book to a subject like Physics, Math, History, etc.
   - Uses AI reasoning to classify based on content.

3. **Conflict Resolution**:
   - Ensures unique filenames by appending counters for duplicates.

4. **Error Handling**:
   - Moves unprocessable files to a `Not renamed` folder for review.

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch:

   ```bash
   git checkout -b feature-name
   ```

3. Commit changes and push:

   ```bash
   git add .
   git commit -m "Add feature description"
   git push origin feature-name
   ```

4. Open a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Author

- **Your Name**  
- Email: your.email@example.com  
- GitHub: [yourusername](https://github.com/yourusername)

---

## Troubleshooting

1. **Tesseract Not Found**:
   - Ensure Tesseract is installed and added to your system PATH.
   - For Windows, set the path explicitly in the script:

     ```python
     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
     ```

2. **Dependency Issues**:
   - Reinstall dependencies using `pip install -r requirements.txt`.

3. **File Not Renamed**:
   - Check the `Not renamed` folder for problematic files.
   - Verify file permissions and format compatibility.

---

## Future Improvements

- Add support for more file formats (e.g., DJVU).
- Enhance AI reasoning for subject classification.
- Implement a GUI for easier usage.

---
