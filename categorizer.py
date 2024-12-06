import os
import logging
from text_extractor import TextExtractor

class Categorizer:
    def __init__(self, config, inference, text_extractor):
        self.config = config
        self.inference = inference
        self.text_extractor = text_extractor

    def categorize_books(self, renamed_path):
        """
        After all books are renamed, gather their titles and infer big subjects.
        Then categorize each book into one of these subjects. 
        For books that are 'Uncategorized', read text and try to fit or create new categories.
        """

        # Gather all renamed books
        renamed_books = [
            f for f in os.listdir(renamed_path) 
            if os.path.isfile(os.path.join(renamed_path, f)) and f.lower().endswith(('.pdf', '.epub'))
        ]

        if not renamed_books:
            logging.info("No renamed books found to categorize.")
            return

        # Extract titles from filenames (assuming the title is the filename without extension)
        titles = [os.path.splitext(book)[0] for book in renamed_books]

        # Infer broad categories from all titles
        broad_categories = self.inference.infer_subjects_from_titles(titles)

        # Create category folders
        for cat in broad_categories:
            cat_path = os.path.join(renamed_path, cat)
            os.makedirs(cat_path, exist_ok=True)

        uncategorized = []
        # First pass: assign books to categories based on title alone
        for book in renamed_books:
            title = os.path.splitext(book)[0]
            category = self.inference.infer_category_for_title(title, broad_categories)
            if category == "Uncategorized":
                uncategorized.append(book)
            else:
                self.move_book_to_category(renamed_path, book, category)

        # For uncategorized, try reading text and refining category
        if uncategorized:
            # Make a set so we can add new categories if discovered
            categories_set = set(broad_categories)
            for book in uncategorized:
                file_path = os.path.join(renamed_path, book)
                text = ""
                if book.lower().endswith(".pdf"):
                    text = self.text_extractor.extract_text_from_pdf(file_path)
                elif book.lower().endswith(".epub"):
                    text = self.text_extractor.extract_text_from_epub(file_path)

                category = self.inference.refine_category_using_text(text, list(categories_set))
                if category not in categories_set:
                    # Create a new category folder
                    categories_set.add(category)
                    cat_path = os.path.join(renamed_path, category)
                    os.makedirs(cat_path, exist_ok=True)
                self.move_book_to_category(renamed_path, book, category)

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
