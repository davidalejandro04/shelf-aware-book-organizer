import logging

class Config:
    """Configuration parameters for the BookRenamer and Categorizer."""

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
        self.log_level = logging.INFO
        self.verbose = False
