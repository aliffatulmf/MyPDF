import argparse
import os
import textwrap
import uuid
import pypdf
import directory

from tqdm import tqdm
from text import SanitizedTextTranslator
from langchain.document_loaders import UnstructuredPDFLoader, UnstructuredWordDocumentLoader
from langchain.schema import Document


class Manipulator(SanitizedTextTranslator):

    def __init__(self, args: argparse.Namespace = None) -> None:
        super().__init__()

        self.folder_path = "docs"
        self.args = args

    def clean_only(self, dry_run: bool = False):
        directory.clean_before_run(self.folder_path, dry_run)

    def split_pdf_to_text_files(self, pdf_path: str, max_words_per_file: int) -> None:
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_reader = pypdf.PdfReader(pdf_file)

                text = "".join(page.extract_text() for page in pdf_reader.pages)
                text = self.sanitize_text(text)

            # Clear the 'docs' folder
            self.clean_only()

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

    def read_and_split(self, documents: list[Document], max_words_per_file: int, wrap: bool = False):
        # Clear the 'docs' folder
        self.clean_only()

        text = "".join(document.page_content for document in documents)
        text = self.sanitize_text(text)

        # Split text into words
        words = text.split()

        # Save text to multiple files with specified number of words per file
        num_files = (len(words) + max_words_per_file -1) // max_words_per_file
        for i in tqdm(range(num_files), desc="Writing document"):
            txt_file = os.path.join(self.folder_path, f"{uuid.uuid4()}.txt")

            with open(txt_file, "w", encoding="utf-8") as file:
                if wrap:
                    start_index = i * max_words_per_file
                    end_index = min((i + 1) * max_words_per_file, len(words))
                    text_part = " ".join(words[start_index:end_index])

                    wrapped_text = textwrap.fill(text_part, width=70)
                    file.write(wrapped_text.lower())
                else:
                    file.write(text.lower())
                file.close()


    def pdf_read_and_split(self, document: str, max_words_per_file: str = None, wrap: bool = False):
        try:
            pdf_reader = UnstructuredPDFLoader(document)
            pdf_reader = pdf_reader.load_and_split()

            self.read_and_split(pdf_reader, max_words_per_file, wrap)
            print(f"The text is stored in files in the {self.folder_path} directory.")
        except Exception as e:
            print("An error occurred while processing the PDF file:", str(e))

    def word_read_and_split(self, document: str, max_words_per_file: str = None, wrap: bool = False):
        try:
            word_reader = UnstructuredWordDocumentLoader(document)
            word_reader = word_reader.load_and_split()

            self.read_and_split(word_reader, max_words_per_file, wrap)
            print(f"The text is stored in files in the {self.folder_path} directory.")
        except Exception as e:
            print("An error occurred while processing the PDF file:", str(e))

    def run(self):
        if self.args.pdf:
            self.pdf_read_and_split(self.args.pdf, self.args.max_word, self.args.wrap)

        if self.args.word:
            self.word_read_and_split(self.args.word, self.args.max_word, self.args.wrap)

        # if self.args.translate_all:
        #     self.translate_documents()

        if self.args.clean:
            self.clean_only(self.args.dry_run)


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i",
                        "--pdf",
                        type=str,
                        help="location of the PDF file to be read")
    parser.add_argument("--word",
                        type=str,
                        help="location of the Word file to be read")
    parser.add_argument("-w",
                        "--max-word",
                        type=int,
                        default=400,
                        help="sets the maximum word limit per file. (default: 400)")
    # parser.add_argument("-t",
    #                     "--translate-all",
    #                     action="store_true",
    #                     help="translate all documents. [NOT RECOMMENDED]")
    parser.add_argument("--clean",
                        help="removes the 'docs' folder before processing the file.",
                        action="store_true")
    parser.add_argument("--wrap",
                        help="wraps the text into paragraphs with a width of 70 characters.",
                        action="store_true")
    parser.add_argument("--dry-run",
                        help="runs the process without taking any actual actions, only displays simulation output.",
                        action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    args = arguments()
    manipulator = Manipulator(args)
    manipulator.run()
