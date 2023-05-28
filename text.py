import re
import langid

from googletrans import Translator


class BatchText:

    def __init__(self, batch_text: list[str]) -> list:
        self.batch_text = batch_text


class Text:

    def __init__(self) -> None:
        self.translator = Translator()

    def detect_language(self, text: str, sanitize: bool = False) -> str:
        if sanitize:
            text = self.sanitize_text(text)

        detected_lang = langid.classify(text)
        return detected_lang[0]

    def sanitize_text(self, text: str) -> str:
        return re.sub(r"[^a-zA-Z0-9]", " ", text).strip()

    def text_length(self, text: str) -> int:
        return len(text.split(" "))

    def batch_sanitize_text(self, batch: BatchText) -> list:
        return [self.sanitize_text(text) for text in batch.batch_text]


class AutoTranslator(Text):

    def __init__(self) -> None:
        super().__init__()

    def text_translator(self,
                        text: str,
                        target: str = "en",
                        source: str = "auto") -> str:
        if source == "auto":
            source = self.detect_language(text)

        translated = self.translator.translate(text, target, source)
        text = translated.text

        return text
    def auto_translate_question(self, question: str, document_language: str) -> str:
        if document_language == "id":
            return self.text_translator(question, "id")
        elif document_language == "en":
            return self.text_translator(question)

    def auto_translate_keywords(self, keywords: list, document_language: str) -> list:
        translated = []

        if document_language != "id":
            for k in keywords:
                translated.append(self.text_translator(k))

        return translated

class SanitizedTextTranslator(AutoTranslator):

    def __init__(self) -> None:
        super().__init__()

    def text_translator(self,
                        text: str,
                        target: str = "en",
                        source: str = "auto") -> str:
        text = self.sanitize_text(text)
        return super().text_translator(text, target, source)
