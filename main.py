import os
import signal
import sys

from dotenv import load_dotenv
from langchain import OpenAI
from llama_index import (GPTVectorStoreIndex, LLMPredictor,
                         QuestionAnswerPrompt, ServiceContext,
                         SimpleDirectoryReader)
from rich.console import Console
from document_search import DocumentSearchBackend


class DocumentSearch:
    def __init__(self, folder_path, openai_api_key, question):
        self.folder_path = folder_path
        self.openai_api_key = openai_api_key
        self.console = Console()
        self.QA_PROMPT_TEMPLATE = (
            "You are an AI assistant here to help. Use the following context snippet to answer the question at the end.\n"
            "If you don't know the answer, simply say that you don't know. DO NOT attempt to make up an answer.\n"
            "If the question is not related to the context, politely state that you are only set to answer context-related questions.\n"
            "If the question is not available, answer by saying that the answer is not available in the document data.\n"
            "\n"
            "{context_str}"
            "\n"
            "Question: {query_str}\n"
            "Helpful Answer:\n"
            "\n"
        )
        self.QA_PROMPT = QuestionAnswerPrompt(self.QA_PROMPT_TEMPLATE)
        self.question = question
        self.backend = DocumentSearchBackend(self.folder_path)

    def stop_program(self, signal, frame):
        print("Program terminated gracefully.")
        sys.exit(0)

    def search(self):
        signal.signal(signal.SIGINT, self.stop_program)
        keywords = self.backend.extract_keywords(self.question)
        print("Found keywords:", keywords)

        processed_documents, file_names = self.backend.load_processed_documents()
        documents, input_files = self.backend.search_best_match(keywords, processed_documents, file_names)
        print(documents)

        llm = OpenAI(
            openai_api_key=self.openai_api_key,
            temperature=0.3,
            model="text-davinci-003",
            streaming=False)

        llm_predictor = LLMPredictor(llm=llm)
        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, chunk_size_limit=3000)
        load_docs = SimpleDirectoryReader(input_files=input_files).load_data()
        index = GPTVectorStoreIndex.from_documents(documents=load_docs, service_context=service_context)
        query_engine = index.as_query_engine(text_qa_template=self.QA_PROMPT, streaming=False)

        return query_engine


if __name__ == "__main__":
    load_dotenv()

    folder_path = "docs"
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        print("Error: OpenAI API key not found. Please set the environment variable 'OPENAI_API_KEY'.")
        sys.exit(1)

    console = Console()
    while True:
        question = console.input("[bold green]Question:[/] [green]")
        if question == "exit":
            break

        doc_search = DocumentSearch(folder_path, openai_api_key, question)
        result = doc_search.search()

        result = result.query(question)
        console.print(f"[bold blue]Answer:[/][blue] {result}")


