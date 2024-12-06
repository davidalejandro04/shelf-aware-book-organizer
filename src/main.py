import warnings
warnings.filterwarnings("ignore")


import os
import argparse
import logging
from config import Config
from logger import setup_logging
from model_loader import ModelLoader
from text_extractor import TextExtractor
from inference import Inference
from renamer import Renamer
from categorizer import Categorizer

def main():
    parser = argparse.ArgumentParser(description='Rename and categorize books based on metadata or text.')
    parser.add_argument('folder', nargs='?', default='.', help='Folder path containing the files (default: current directory)')
    parser.add_argument('--model', default='llama3.2', help='Ollama model to use (default: llama3.2)')
    parser.add_argument('--log', default='INFO', help='Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--pages', type=int, default=15, help='Number of pages to read from PDFs (default: 15)')
    parser.add_argument('--ocr_pages', type=int, default=5, help='Number of pages to read using OCR (default: 5)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--max_categories', type=int, default=7, help='Maximum number of categories (default: 7)')
    parser.add_argument('--skip_categories', action='store_true', help='Skip category creation and assign to predefined categories only')
    args = parser.parse_args()
    folder_path = args.folder

    if not os.path.isdir(folder_path):
        print("Invalid folder path.")
        return

    config = Config()
    config.model_name = args.model
    config.log_level = getattr(logging, args.log.upper(), logging.INFO)
    config.pages_to_read_pdf = args.pages
    config.pages_to_read_ocr = args.ocr_pages
    config.verbose = args.verbose
    config.max_categories = args.max_categories
    config.skip_categories = args.skip_categories

    if config.verbose:
        config.log_level = logging.DEBUG

    setup_logging(config.log_level)

    # Load model once
    model_loader = ModelLoader(config.model_name)
    model = model_loader.load_model()

    text_extractor = TextExtractor(config)
    inference = Inference(config, model)
    renamer = Renamer(config, inference, text_extractor)

    # Step 1: Rename all books
    renamer.rename_files_in_folder(folder_path)

    # Step 2: Categorize renamed books based on inferred categories
    renamed_path = os.path.join(folder_path, "Renamed")
    categorizer = Categorizer(config, inference, text_extractor)
    categorizer.categorize_books(renamed_path)

if __name__ == "__main__":
    main()
