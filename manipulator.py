import argparse
import os
import textwrap
import uuid
import directory

from tqdm import tqdm
from text import Text, SanitizedTextTranslator
from langchain.document_loaders import UnstructuredPDFLoader, UnstructuredWordDocumentLoader
from langchain.schema import Document


class Manipulator:
    def __init__(self, args: argparse.Namespace = None) -> None:
        self.translator = SanitizedTextTranslator()
        self.text = Text()
        self.folder_path = "docs"
        self.args = args

    def read_and_split(self, documents: list[Document], max_words_per_file: int, wrap: bool = False):
        directory.clean_directory(self.folder_path)
        words = self.text.sanitize_text(" ".join(document.page_content for document in documents)).split()
        num_files = (len(words) + max_words_per_file - 1) // max_words_per_file

        for i in tqdm(range(num_files), desc="Writing document"):
            txt_file = os.path.join(self.folder_path, f"{uuid.uuid4()}.txt")

            with open(txt_file, "w", encoding="utf-8") as file:
                start_index = i * max_words_per_file
                end_index = min((i + 1) * max_words_per_file, len(words))
                text_part = " ".join(words[start_index:end_index])

                if wrap:
                    wrapped_text = textwrap.fill(text_part, width=70)
                    file.write(wrapped_text.lower())
                else:
                    file.write(text_part.lower())

        print(f"The text is stored in files in the {self.folder_path} directory.")


    def process_pdf(self, file_path: str):
        pdf_reader = UnstructuredPDFLoader(file_path)
        documents = pdf_reader.load_and_split()
        self.read_and_split(documents, self.args.max_word, self.args.wrap)

    def process_word(self, file_path: str):
        word_reader = UnstructuredWordDocumentLoader(file_path)
        documents = word_reader.load_and_split()
        self.read_and_split(documents, self.args.max_word, self.args.wrap)

    def run(self):
        if self.args.pdf:
            try:
                self.process_pdf(self.args.pdf)
            except ValueError as e:
                print(f"Error: {str(e)}")
        elif self.args.word:
            try:
                self.process_word(self.args.word)
            except ValueError as e:
                print(f"Error: {str(e)}")

        if self.args.clean:
            directory.clean_directory(self.folder_path, self.args.dry_run)


def check_file_type(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    supported_extensions = {".pdf", ".docx", ".doc"}

    if file_extension not in supported_extensions:
        raise ValueError("Unsupported file type. Please provide a PDF or Word document.")

    if file_extension == ".pdf":
        return "PDF"
    elif file_extension in {".docx", ".doc"}:
        return "Word"

def arguments():
    parser = argparse.ArgumentParser()

    # File options
    group_file = parser.add_argument_group("File options")
    group_file.add_argument("--pdf",
                            type=str,
                            help="location of the PDF file to be read")
    group_file.add_argument("--word",
                            type=str,
                            help="location of the Word file to be read")
    group_file.add_argument("-w",
                            "--max-word",
                            type=int,
                            default=400,
                            help="sets the maximum word limit per file. (default: 400)")

    # Processing options
    group_processing = parser.add_argument_group("Processing options")
    group_processing.add_argument("--clean",
                                   help="removes the 'docs' folder before processing the file.",
                                   action="store_true")
    group_processing.add_argument("--wrap",
                                   help="wraps the text into paragraphs with a width of 70 characters.",
                                   action="store_true")
    group_processing.add_argument("--dry-run",
                                   help="runs the process without taking any actual actions, only displays simulation output.",
                                   action="store_true")

    return parser.parse_args()

if __name__ == "__main__":
    args = arguments()
    manipulator = Manipulator(args)
    manipulator.run()
