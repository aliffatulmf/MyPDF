import argparse
import json
import os
import signal
import threading
import time

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from document_search import DocumentSearch

load_dotenv()


class LoadingScreen:
    def __init__(self):
        self.stop_event = threading.Event()
        self.loading_thread = threading.Thread(target=self._show_loading_animation)

    def start(self):
        self.loading_thread.start()

    def stop(self):
        self.stop_event.set()
        self.loading_thread.join()

    def _show_loading_animation(self):
        count = 0
        while not self.stop_event.is_set():
            count += 1
            dots = "." * (count % 4)
            print(f"Loading{dots}", end="\r")
            time.sleep(0.5)

            if count % 4 == 0:
                count = 0


API_URL = os.getenv("API_URL")

HEADERS = {
    "Access-Code": os.getenv("API_KEY"),
    "Origin": os.getenv("API_ORIGIN"),
    "Referer": os.getenv("API_REFERER"),
    "Path": os.getenv("API_PATH"),
    "User-Agent": os.getenv("API_USER_AGENT"),
    "Content-Type": "application/json"
}

system_content = (
    "You are an AI assistant here to help. Use the following context snippet to answer the question at the end.\n"
    "If you don't know the answer, simply say that you don't know. DO NOT attempt to make up an answer!\n"
    "If the question is not related to the context, politely state that you are only set to answer context-related questions.\n"
    "If the question is not available, answer by saying that the answer is not available in the document data.\n"
)

payload = {
    "messages": [],
    "stream": True,
    "model": os.getenv("MODEL"),
    "temperature": 0.0,
    "presence_penalty": 0.0,
}


def prompt_template(context: list, question: str):
    prompt_length = 65
    query_words = question.split()
    query_length = len(query_words)
    total_length = query_length + len(context) + prompt_length

    if total_length > 4097:
        context_text = " ".join(context[:len(context) - (query_length + prompt_length)])
    else:
        context_text = " ".join(context)

    return (
        "\n**Context:**\n"
        f"{context_text}\n\n"
        f"**Question:** {question}\n"
        "**Helpful Answer:**"
    )


def read_documents(documents: list):
    texts = []
    for document in documents:
        with open(document["location"], "r", encoding="utf-8") as doc:
            texts.append(doc.read())

    return texts


def search_and_return_documents(question: str):
    ds = DocumentSearch(None, "docs")
    load_docs = ds.search_documents(question)
    read_docs = read_documents(load_docs)
    prompt = prompt_template(read_docs, question)
    payload["messages"] = [{"role": "system", "content": system_content}, {"role": "user", "content": prompt}]
    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))

    return response.text


def search_online(question: str):
    payload["messages"].append({"role": "user", "content": question})
    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
    payload["messages"].append({"role": "assistant", "content": response.text})

    return response.text


def signal_handler(sig, frame):
    print("Program terminated gracefully.")
    exit(0)


def run_search():
    console = Console()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type",
        choices=["internet", "document"],
        default="document",
        type=str,
        help="Choose between internet connection or document search. (default: document)"
    )
    parser.add_argument(
        "--style",
        choices=["none", "concise", "creative"],
        default="none",
        type=str,
        help="Choose the style for the responses. Options: 'none' (standard style), 'concise' (minimal words and "
             "characters), 'creative' (imaginative and varied style)."
    )
    args = parser.parse_args()

    if args.style == "concise":
        payload["messages"].append({
            "role": "system",
            "content": "This tone responds with the fewest words and characters possible. It skips extra words and "
                       "gets right to the point. Example: 'Data shows sales up 50%' instead of 'Based on the data "
                       "that we have collected, it appears that there has been an increase in sales by 50%.'"})
    elif args.style == "creative":
        payload["messages"].append({
            "role": "system",
            "content": "This style is characterized by a focus on imagination, expression, and originality. It often "
                       "involves using literary devices such as metaphors, imagery, and symbolism to convey meaning. "
                       "Example: 'The sunset painted the sky with a palette of fiery oranges and deep purples, "
                       "as if nature itself were an artist at work.'"
        })

    if args.type == "document":
        payload["presence_penalty"] = 0.6

        search_type = "Document"
        search_func = search_and_return_documents
    elif args.type == "internet":
        payload["messages"].append(
            {"role": "system", "content": "You are a helpful assistant. Please answer using Markdown."})
        payload["temperature"] = 1.0

        search_type = "Internet"
        search_func = search_online
    else:
        console.print("[red bold]Invalid value for --type argument. Please choose between 'document' or 'internet'.")
        return

    console.print(
        f"[green bold]To stop the program, press Ctrl+C on your keyboard while in {search_type} search mode.\n")

    while True:
        query = input(console.render_str(f"[white bold]({search_type}) Question[/][white]: "))
        answer = Markdown(search_func(query))
        console.print(f"[white bold]({search_type}) Answer[/]: {answer.markup}", end="\n\n", markup=True,
                      highlight=True)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    run_search()
