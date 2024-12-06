import re
import logging
import ollama

class Inference:
    def __init__(self, config, model):
        self.config = config
        self.model = model

    def improve_title_from_metadata(self, metadata_title, text):
        """
        Improve an existing metadata title by using the model to refine or enhance it.
        """
        prompt = f"""
You are an expert in improving book titles. The original title is "{metadata_title}".
Improve it to be more descriptive and appealing based on the context provided by the text.

Text context:
"{text[:self.config.text_snippet_length]}"

Respond ONLY with the improved title, without quotes.
"""
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": 0.2, "max_tokens": 50}
            )
            title = response["response"].strip()
            return self._sanitize_title(title)
        except Exception as e:
            logging.error(f"Error improving metadata title: {e}")
            return self._sanitize_title(metadata_title)

    def infer_title(self, text):
        """
        Infer the title of a book from its text.
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

Respond ONLY with the inferred title.
"""
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": 0.2, "max_tokens": 50}
            )
            title = response["response"].strip()

            if not title or any(phrase in title.lower() for phrase in [
                "no explicit title", "unable to determine", "cannot find title", "untitled"
            ]):
                logging.info("No explicit title found. Using fallback inference.")
                fallback_prompt = f"""
Based on the text, generate a concise fallback title that reflects the main subject or theme of the text:
"{text[:self.config.text_snippet_length]}"

Ensure the title is concise, descriptive, and avoids generic terms.
"""
                fallback_response = ollama.generate(
                    model=self.model,
                    prompt=fallback_prompt,
                    options={"temperature": 0.2, "max_tokens": 50}
                )
                title = fallback_response["response"].strip()

            return self._sanitize_title(title)
        except Exception as e:
            logging.error(f"Error inferring title: {e}")
            return "Untitled"

    def _sanitize_title(self, title):
        title = re.sub(r'[\\/*?:"<>|]', "", title).replace("\n", " ").strip()
        title = title[:self.config.max_title_length] if title else "Untitled"
        return title

    def infer_subjects_from_titles(self, titles):
        """
        Infer big subjects (broad categories) based on a list of titles.
        Use chain-of-thought to determine a set of categories or top-level subjects.
        """
        prompt = f"""
You are an expert librarian. Given a list of book titles, suggest broad subject categories that encompass them.
These categories should be broad academic or general fields (like Science, Social Sciences, Art, Engineering, etc.).

Titles:
{chr(10).join(titles)}

Steps:
1. Analyze all titles and look for patterns or common fields.
2. Suggest a small set of broad subjects that best classify these titles. 
3. Respond ONLY with a comma-separated list of categories.
"""
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": 0.2, "max_tokens": 100}
            )
            categories_str = response["response"].strip()
            categories = [c.strip() for c in categories_str.split(',') if c.strip()]
            return categories if categories else self.config.default_subjects
        except Exception as e:
            logging.error(f"Error inferring subjects from titles: {e}")
            return self.config.default_subjects

    def infer_category_for_title(self, title, broad_categories):
        """
        Infer which category a single title fits into from a given list of broad categories.
        If it does not fit, respond with 'Uncategorized'.
        """
        prompt = f"""
You are an expert classifier. Given the title: "{title}"
Decide which category from this list best fits the title:
{", ".join(broad_categories)}

If none match, respond with "Uncategorized".
Respond ONLY with the chosen category name.
"""
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": 0.1, "max_tokens": 20}
            )
            category = response["response"].strip()
            if category not in broad_categories and category.lower() != "uncategorized":
                category = "Uncategorized"
            return category
        except Exception as e:
            logging.error(f"Error inferring category for title: {e}")
            return "Uncategorized"

    def refine_category_using_text(self, text, existing_categories):
        """
        If a book didn't fit any previously inferred category, analyze its text to assign it
        to either one of the existing categories or propose a new one.
        """
        prompt = f"""
You are an expert classifier. The following categories exist:
{", ".join(existing_categories)}

Given this book text:
"{text[:self.config.text_snippet_length]}"

1. If it fits into one of these categories, choose it.
2. Otherwise, propose a new suitable category name.

Respond ONLY with the chosen or new category name.
"""
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": 0.2, "max_tokens": 50}
            )
            category = response["response"].strip()
            return category
        except Exception as e:
            logging.error(f"Error refining category using text: {e}")
            return "Other"
