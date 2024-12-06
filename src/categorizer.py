import os
import logging
from text_extractor import TextExtractor
class Categorizer:
    def __init__(self, config, inference, text_extractor):
        self.config = config
        self.inference = inference
        self.text_extractor = text_extractor


    def move_book_to_category(self, renamed_path, book, category):
        src = os.path.join(renamed_path, book)
        dst = os.path.join(renamed_path, category, book)
        # Ensure unique name if collision
        base_name, ext = os.path.splitext(book)
        counter = 1
        while os.path.exists(dst):
            new_name = f"{base_name}_{counter}{ext}"
            dst = os.path.join(renamed_path, category, new_name)
            counter += 1
        os.rename(src, dst)

    def categorize_books(self, renamed_path):
        """
        Categorize renamed books into broad subjects.
        Skip files excluded during the renaming step.
        """
        renamed_books = [
            f for f in os.listdir(renamed_path) 
            if os.path.isfile(os.path.join(renamed_path, f)) and f.lower().endswith(('.pdf', '.epub'))
        ]

        if not renamed_books:
            logging.info("No renamed books found to categorize.")
            return

        titles = [os.path.splitext(book)[0] for book in renamed_books]

        # Infer broad categories
        broad_categories = self.inference.infer_subjects_from_titles(titles)

        if self.config.skip_categories:
            logging.info("Skipping category creation. Assigning books to predefined categories.")
            for book in renamed_books:
                # Check if file was excluded during renaming
                if not self._is_valid_for_sorting(book):
                    logging.info(f"File '{book}' skipped during categorization.")
                    continue

                title = os.path.splitext(book)[0]
                category = self.inference.infer_category_for_title(title, broad_categories)
                self.move_book_to_category(renamed_path, book, category)
            return

        # Create folders and categorize
        for cat in broad_categories:
            cat_path = os.path.join(renamed_path, cat)
            os.makedirs(cat_path, exist_ok=True)

        # Assign books to categories
        for book in renamed_books:
            if not self._is_valid_for_sorting(book):
                logging.info(f"File '{book}' skipped during categorization.")
                continue

            title = os.path.splitext(book)[0]
            category = self.inference.infer_category_for_title(title, broad_categories)
            if category == "Uncategorized":
                # Handle uncategorized logic
                pass
            else:
                self.move_book_to_category(renamed_path, book, category)

    def _is_valid_for_sorting(self, book):
        """
        Check if a book is valid for categorization based on metadata from renaming.
        """
        # Add logic to check exclusion metadata
        # Example: Save a separate JSON or in-memory flag during renaming
        return True  # Replace with actual logic