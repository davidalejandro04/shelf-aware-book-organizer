import re
import logging
import ollama

class Inference:
    def __init__(self, config, model):
        self.config = config
        self.model = model

    def improve_title_from_metadata(self, metadata_title, text):
        """
        Improve an existing metadata title using the model. If the model returns
        a generic or inability response, fallback to the original metadata title.
        """
        prompt = f"""
You are an expert in improving book titles. Work independently of any prior context.

The original title is "{metadata_title}". Your task is to improve it to be more descriptive
and appealing based on the context provided by the following text. 
DO NOT store or retain any information beyond this task.

Text context:
"{text[:self.config.text_snippet_length]}"

Steps:
1. Analyze the text context independently. Focus only on the provided text.
2. Improve the original title to be concise, descriptive, and professional. Avoid generic titles like "Unlocking" or "Introduction."
3. If unable to improve, clearly state why (e.g., "I cannot create content...").

Respond ONLY with the improved title, without quotes.
"""
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": 0.2, "max_tokens": 50}
            )
            title = response["response"].strip()

            # Check for inability or generic responses
            if any(phrase in title.lower() for phrase in [
                "i cannot create content", "unable to improve", "cannot refine", "cannot promote"
            ]):
                return self._sanitize_title(metadata_title), False  # False indicates the title should be excluded from sorting

            return self._sanitize_title(title), True  # True indicates the title is valid for sorting
        except Exception as e:
            logging.error(f"Error improving metadata title: {e}")
            return self._sanitize_title(metadata_title), False  # Fallback to metadata title


    def infer_category_for_title(self, title, broad_categories):
        """
        Infer which category a single title fits into from a given list of broad categories.
        If it does not fit, respond with 'Uncategorized'.
        """
        prompt = f"""
You're an expert to categorize books into broad categories. 
Given the title: "{title}"
Decide which category from this list best fits the title:
{", ".join(broad_categories)}, expect spanish or french as well. 

If there is more than one category, choose the most appropriate, and reply ONLY the name of the category. 
If none match, respond with "Uncategorized".
IMPORTANT: Respond ONLY with the chosen category name.
"""
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": 0.4, "max_tokens": 10}
            )
            category = response["response"].strip()
            if category not in broad_categories and category.lower() != "uncategorized":
                category = "Uncategorized"
            return self._sanitize_title(category)
        except Exception as e:
            logging.error(f"Error inferring category for title: {e}")
            return "Uncategorized"

    def infer_title(self, text):
        """
        Infer the title of a book using the model. Ensure stateless operation to avoid retaining prior context.
        """
        prompt = f"""
You are an expert in analyzing text to infer book titles. Work independently of any prior context.

Your task is to generate a concise, descriptive, and professional title based solely on the provided text.
DO NOT store or retain any information beyond this task. Avoid generic titles like "Unlocking", "Mastering", unless is the explicit name of the text. 

Text context:
"{text[:self.config.text_snippet_length]}"

Steps:
1. Analyze the text independently.
2. Infer the title based on key terms, recurring phrases, or themes in the text.
3. Ensure the title is concise, descriptive, and avoids generic terms.

Respond ONLY with the inferred title, without quotes. If unable to determine a title, respond with "Untitled."
"""
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": 0.2, "max_tokens": 50, "system": "You must not retain any information between requests. Process each request independently."}
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
        Infer broad subjects based on a list of titles.
        Limit the number of categories to the `max_categories` setting.
        """
        prompt = f"""
You are an expert librarian. Given a list of book titles, suggest broad subject categories that encompass them.
These categories should be broad academic or general fields (like Science, Social Sciences, Art, Engineering, etc.).

You're an expert to categorize books into broad categories. And you always assign the most appropriate category.  

Titles:
{chr(10).join(titles)}

Steps:
1. Analyze all titles and look for patterns or common fields.
2. Suggest a small set of broad subjects that best classify these titles. 
3. Respond ONLY with a comma-separated list of categories, limiting the number to {self.config.max_categories}.
4. If there are many categories, ONLY respond with the catgory names, NOTHING ELSE. 
"""
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": 0.2, "max_tokens": 100}
            )
            categories_str = response["response"].strip()
            categories = [c.strip() for c in categories_str.split(',') if c.strip()]
            return categories[:self.config.max_categories] if categories else self.config.default_subjects
        except Exception as e:
            logging.error(f"Error inferring subjects from titles: {e}")
            return self.config.default_subjects[:self.config.max_categories]


