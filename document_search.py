import heapq
import os
import string
import warnings
import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from rank_bm25 import BM25Okapi
from tqdm import tqdm
from text import AutoTranslator


with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        category=UserWarning)  # Sembunyikan peringatan saat pengunduhan
    nltk.download('stopwords', quiet=True)


class DocumentSearchBackend:
    def __init__(self, folder_path: str = None) -> None:
        self.translator = AutoTranslator()
        self.folder_path = folder_path if folder_path is None else "docs"
        self.national_language = self.override_language_detection("id")
        self.document_length = 0

    def override_language_detection(self, text: str, override_language: str = None):
        language_dict = {"id": "indonesian", "en": "english"}
        detected_language = self.translator.detect_language(text)

        if override_language is None:
            return language_dict.get(detected_language, None)

        return language_dict.get(override_language, None)

    def load_processed_documents(self):
        processed_documents = []
        file_names = []

        file_list = [file_name for file_name in os.listdir(self.folder_path) if file_name.endswith('.txt')]


        for file_name in tqdm(file_list, desc='Processing documents'):
            with open(os.path.join(self.folder_path, file_name), "r", encoding="utf-8") as file:
                text = file.read()

                processed_documents.append(self.word_tokenizing(text))
                file_names.append(file_name)

        return processed_documents, file_names

    def get_document_language(self, file_names: list):
        with open(os.path.join(self.folder_path, file_names[0]), "r", encoding="utf-8") as file:
            text = file.read()
            self.document_language = self.translator.detect_language(text)

    def word_tokenizing(self, text: str, override_language: str = None):
        if override_language is None:
            text_length = self.translator.text_length(text) // 4
            language = self.override_language_detection(text[:text_length])
        else:
            language = self.override_language_detection("", override_language)

        words = nltk.word_tokenize(text)
        return [word for word in words if word not in stopwords.words(language)] # return word

    def extract_keywords(self, question: str, override_language: str = None):
        language = self.override_language_detection(question)
        stop_words = set(stopwords.words(language))
        custom_stop_words = {"?", "!", ".", ","}
        stop_words.update(custom_stop_words)

        tokens = word_tokenize(question.lower())
        return [token for token in tokens if token not in stop_words] # return keyword

    def search_best_match(self, keywords: list, processed_documents: list, file_names: list):
        bm25 = BM25Okapi(processed_documents)
        translated_keywords = self.translator.auto_translate_keywords(keywords, self.get_document_language(file_names))
        doc_scores = bm25.get_scores(translated_keywords)

        relevant_documents = heapq.nlargest(3, zip(file_names, doc_scores), key=lambda x: x[1])
        return {file_name: score for file_name, score in relevant_documents}, [os.path.join(self.folder_path, file_name) for file_name, _ in relevant_documents]
