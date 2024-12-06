
# Book Renamer and Organizer

<div style="text-align: center;">
  <img src="https://github.com/user-attachments/assets/977bce92-cbf5-4f86-89f4-ea40fc7b3f08" alt="imagen" width="600">
</div>


This is a just for fun Python-based tool designed to process and organize digital books (PDF and EPUB formats). 
It leverages (Unnecessarily) AI models to infer book titles and subjects based on their content and organizes them into structured directories. The tool supports Optical Character Recognition (OCR) for PDFs without embedded text and handles metadata extraction for EPUB files. It includes mechanisms to ensure stateless AI processing and avoids generic or inappropriate titles during renaming. The perfect example of overengineering. 

---

## Features

- **Title Inference:** Automatically extracts or infers the title of books using AI models (e.g., Ollama) while 
  avoiding generic terms like "Unlocking" or "Introduction."
- **Stateless Processing:** Ensures the AI model operates independently for each request and clears its memory 
  after every operation.
- **Subject Categorization:** Classifies books into predefined subjects such as Physics, Math, Computer Science, 
  etc., with a configurable limit on the number of categories (default: 7).
- **PDF Text Extraction:** Uses PyMuPDF for extracting text directly from PDFs.
- **OCR Support:** Processes scanned PDFs with Tesseract OCR for text extraction.
- **EPUB Text Extraction:** Reads and extracts text from EPUB documents.
- **File Organization:** Renames books based on inferred titles and categorizes them into subject-specific folders.
- **Conflict Handling:** Ensures files with duplicate titles are uniquely named.
- **Parallel Processing:** Speeds up processing by utilizing multiprocessing for large datasets.
- **Error Handling:** Logs detailed errors for debugging and moves problematic files to a `Not renamed` folder.
- **Skip Category Option:** Allows skipping the creation of new categories, assigning books directly to predefined 
  categories.

---

## Requirements

### Python Version

- Python 3.7 or newer

### Python Libraries

Install the required libraries using pip:

```bash
pip install -r requirements.txt
```

**`requirements.txt`:**
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

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/book-renamer.git
   cd book-renamer
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Tesseract Installation:**

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
- **`--max_categories`**: Maximum number of categories for classification. Default is 7.
- **`--skip_categories`**: Skip creating new categories; assign books to predefined ones.

#### Example:

```bash
python renamebooks.py /path/to/books --model llama4.0 --log DEBUG --pages 20 --max_categories 5 --skip_categories
```

---

## Folder Structure

- **Input Folder:** Specify a folder containing PDFs and EPUBs to process.
- **Output Folders:**
  - `Renamed/`: Contains renamed files organized into subject-specific folders.
  - `Not renamed/`: Contains files that couldn't be processed or renamed.

---

## Features in Detail

1. **Title Inference:**
   - Extracts titles from document metadata or generates them using AI.
   - Ensures stateless operation for each request to avoid data retention.
   - Handles edge cases where explicit titles are not present.
   - Avoids generic or inappropriate titles and falls back to "Untitled" or metadata.

2. **Subject Categorization:**
   - Assigns each book to a predefined subject like Physics, Math, History, etc.
   - Uses AI reasoning to classify based on content.
   - Configurable category limits to avoid excessive categorization.

3. **Conflict Resolution:**
   - Ensures unique filenames by appending counters for duplicates.

4. **Error Handling:**
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

## Troubleshooting

1. **Tesseract Not Found:**
   - Ensure Tesseract is installed and added to your system PATH.
   - For Windows, set the path explicitly in the script:

     ```python
     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR	esseract.exe'
     ```

2. **Dependency Issues:**
   - Reinstall dependencies using `pip install -r requirements.txt`.

3. **File Not Renamed:**
   - Check the `Not renamed` folder for problematic files.
   - Verify file permissions and format compatibility.

---

## Future Improvements

- Add support for more file formats (e.g., DJVU).
- Improve speed by indexing files. 
- Add persistence of indexing. 
- Enhance AI reasoning for subject classification.
- Implement a GUI for easier usage.

---
