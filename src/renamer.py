import os
import logging
from shutil import move
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from metadata import extract_pdf_metadata, extract_epub_metadata

class Renamer:
    def __init__(self, config, inference, text_extractor):
        self.config = config
        self.inference = inference
        self.text_extractor = text_extractor
        self.success_count = 0
        self.total_count = 0

    def process_file(self, args):
        """
        Process and rename a single file. If a title refinement fails due to an inability response,
        keep the original metadata title and skip categorization.
        """
        file_path, renamed_path, not_renamed_path = args
        file_name = os.path.basename(file_path)
        try:
            if os.path.isfile(file_path):
                extension = os.path.splitext(file_name)[1].lower()
                text = ""
                metadata_title = None
                valid_for_sorting = True  # Flag to determine if the file should be categorized

                # Extract metadata title
                if extension == ".pdf":
                    metadata_title = extract_pdf_metadata(file_path)
                elif extension == ".epub":
                    metadata_title = extract_epub_metadata(file_path)

                # Refine metadata title or fallback to text inference
                if metadata_title:
                    if extension == ".pdf":
                        text = self.text_extractor.extract_text_from_pdf(file_path)
                    elif extension == ".epub":
                        text = self.text_extractor.extract_text_from_epub(file_path)

                    new_title, valid_for_sorting = self.inference.improve_title_from_metadata(metadata_title, text)
                else:
                    if extension == ".pdf":
                        text = self.text_extractor.extract_text_from_pdf(file_path)
                    elif extension == ".epub":
                        text = self.text_extractor.extract_text_from_epub(file_path)

                    if not text.strip():
                        # No text available, move to not renamed
                        move(file_path, os.path.join(not_renamed_path, file_name))
                        return
                    new_title, valid_for_sorting = self.inference.infer_title(text), True

                # Rename file
                new_file_name = f"{new_title}{extension}"
                new_file_path = os.path.join(renamed_path, new_file_name)

                # Ensure unique filename
                counter = 1
                while os.path.exists(new_file_path):
                    new_file_name = f"{new_title}_{counter}{extension}"
                    new_file_path = os.path.join(renamed_path, new_file_name)
                    counter += 1

                os.rename(file_path, new_file_path)

                # Add sorting exclusion metadata
                if valid_for_sorting:
                    return new_file_path, True  # Include in sorting
                else:
                    logging.info(f"File '{file_name}' excluded from sorting due to inability response.")
                    return new_file_path, False  # Exclude from sorting

            else:
                move(file_path, os.path.join(not_renamed_path, file_name))
        except Exception as e:
            logging.error(f"Error processing file '{file_name}': {e}")
            move(file_path, os.path.join(not_renamed_path, file_name))
            return None, False  # Exclude on error

    def rename_files_in_folder(self, folder_path):
        """
        Rename all supported files in a folder based on metadata or inferred titles.
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

        self.total_count = len(tasks)
        if self.total_count == 0:
            logging.info("No PDF or EPUB files found to rename.")
            return

        with Pool(processes=cpu_count()) as pool:
            for _ in tqdm(pool.imap_unordered(self.process_file, tasks), total=len(tasks), desc="Processing Files"):
                pass

        # Print percentage of successfully renamed
        if self.total_count > 0:
            success_percentage = (self.success_count / self.total_count) * 100
            print(f"Successfully renamed {self.success_count}/{self.total_count} books ({success_percentage:.2f}%).")
