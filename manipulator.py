import argparse
import os
import textwrap
import uuid
import pypdf

from tqdm import tqdm
from text import SanitizedTextTranslator


class Manipulator(SanitizedTextTranslator):

    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__()

        self.folder_path = "docs"
        self.args = args

    def split_pdf_to_text_files(self, pdf_path: str, max_words_per_file: int) -> None:
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_reader = pypdf.PdfReader(pdf_file)

                text = "".join(page.extract_text() for page in pdf_reader.pages)
                text = self.sanitize_text(text)

            # Clear the 'docs' folder
            for entry in os.scandir(self.folder_path):
                if entry.is_file():
                    os.remove(entry.path)

            # Split text into words
            words = text.split()

            # Save text to multiple files with specified number of words per file
            num_files = (len(words) + max_words_per_file -1) // max_words_per_file
            for i in range(num_files):
                txt_file = os.path.join(self.folder_path, f"{uuid.uuid4()}.txt")

                with open(txt_file, "w", encoding="utf-8") as file:
                    start_index = i * max_words_per_file
                    end_index = min((i + 1) * max_words_per_file, len(words))
                    text_part = " ".join(words[start_index:end_index])

                    wrapped_text = textwrap.fill(text_part, width=70)
                    file.write(wrapped_text.lower())

            print(f"The text is stored in {num_files} files in the {self.folder_path} directory.")
        except Exception as e:
            print("An error occurred while processing the PDF file:", str(e))

    def translate_documents(self) -> None:
        for filename in tqdm(os.listdir(self.folder_path),
                             desc='Translating documents'):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.folder_path, filename)

                with open(file_path, "r+", encoding="utf-8") as file:
                    text = file.read()

                    # Translate the text from English to Indonesian
                    translation = self.translator.translate(text,
                                                            src="en",
                                                            dest="id")
                    translated_text = translation.text

                    # Set the file position to the beginning and truncate the contents
                    file.seek(0)
                    file.truncate()

                    file.write(translated_text)

        print("Translation completed.")

    def run(self):
        if self.args.pdf is not None:
            self.split_pdf_to_text_files(self.args.pdf, self.args.max_word)

        if self.args.translate_all:
            self.translate_documents()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i",
                        "--pdf",
                        type=str,
                        required=False,
                        help="Location of the PDF file to be read")
    parser.add_argument("-w",
                        "--max-word",
                        type=int,
                        default=400,
                        help="Sets the maximum word limit per file. (default: 400)")
    parser.add_argument("-t",
                        "--translate-all",
                        action="store_true",
                        help="Translate all documents. [NOT RECOMMENDED]")
    args = parser.parse_args()

    manipulator = Manipulator(args)
    manipulator.run()
