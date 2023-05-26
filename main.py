import os
import signal
import sys

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from rich.console import Console
from document_search import DocumentSearch

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda signal, frame: print("Program terminated gracefully.") or sys.exit(0))
    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    folder_path = "docs"

    if not openai_api_key:
        print("Error: OpenAI API key not found. Please set the environment variable 'OPENAI_API_KEY'.")
        sys.exit(1)

    llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        temperature=0,
        model="gpt-3.5-turbo",
        streaming=False
    )

    console = Console()
    doc_search = DocumentSearch(llm, folder_path)

    while True:
        question = console.input("[bold green]Question:[/] [green]")
        if question == "exit":
            break

        result = doc_search.search(question)
        console.print(f"[bold blue]Answer:[/][blue] {result}")
