import os
import json
import random
import logging
import time
from typing import Literal, Tuple, get_args
from pydantic import BaseModel
from backend.src.definitions import DATA_DIR
from backend.src.environment import product_catalogues
from backend.src.data_import.stopwatch import Stopwatch
from backend.src.app.dependencies import llm, chroma, retrieve_graph as build_retrieve_graph

logging.basicConfig(format="%(asctime)s [%(name)s] %(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

QUERY_PROMPT = (
    """
Generate an e-commerce product query based on the specified conditions (style) and the 
provided context. The query should emulate a user searching for a specific e-commerce product 
based on the provided context.

Do not use any kind of text formatting. Do not echo my prompt. Do not remind me what I asked you 
for. Do not apologize. Do not self-reference. Only output the generated query without "Query:" in 
front.

### Examples:
Query style: Casual
Context: Sink into luxurious comfort with this stylish velvet armchair. Its sleek design and 
plush cushioning make it the perfect addition to any living room or reading nook. Available in a 
variety of rich colors.
Query: Indoor furniture armchair

----------------------------
Output query style: {style}

Here is the context:

{context}
    """
)

SUMMARIZE_PROMPT = (
    """
You are an AI E-commerce expert who writes compelling product descriptions.
I am going to provide the description of one e-commerce product and I want you to rewrite and 
enhance that description.

The main point of these commands is for you to developing a new informative, and captivating 
product summary/description that is less than {n_words} words long. The purpose of product 
description is marketing the products to users looking to buy.

Do not use any kind of text formatting besides line breaks. Do not echo my prompt. Do not remind 
me what I asked you for. Do not apologize. Do not self-reference.

Original description: {description}
    """
)

QueryStyle = Literal[
    "Formal",
    "Casual",
    "Misspelled",
    "Perfect grammar",
    "Poor grammar",
    "Web search like",
    "Chat like"
]

QUERY_STYLES: Tuple[QueryStyle, ...] = get_args(QueryStyle)


class DataFrame(BaseModel):
    query_style: QueryStyle
    user_input: str
    reference: str
    response: str | None = None
    retrieved_contexts: list[str] = []
    n_relevant_contexts: int | None = None

    def __str__(self):
        contexts = "\n".join([
            f"{c[:75].strip()} ... {c[len(c) - 75:].strip()}" for c in self.retrieved_contexts
        ])

        return (
            f"[{self.query_style}] {self.user_input}\n\n"
            "Expected:\n"
            f"{self.reference}\n\n"
            "Actual:\n"
            f"{self.response}\n\n"
            f"Contexts ({self.n_relevant_contexts} relevant):\n"
            f"{contexts}"
        )


def generate_testset(data_file: str, *, size: int, write_to_disk: bool = False) -> list[DataFrame]:
    log.info("Query vector store for documents from %s", data_file)
    page_contents = chroma.get(where={"source": data_file}).get("documents")
    testset: list[DataFrame] = []

    if page_contents:
        log.info("Found %s documents, generating testset of size %s", len(page_contents), size)

        i = random.randrange(0, len(page_contents) - size)
        for content in page_contents[i:i + size]:
            query_style = random.choice(QUERY_STYLES)
            query_prompt = QUERY_PROMPT.format(style=query_style, context=content)
            summarize_prompt = SUMMARIZE_PROMPT.format(n_words=100, description=content)

            query = llm.invoke(query_prompt).content
            summary = llm.invoke(summarize_prompt).content
            testset.append(DataFrame(
                query_style=query_style,
                user_input=query,
                reference=summary
            ))

        if write_to_disk:
            with open(os.path.join(DATA_DIR, f"testset_{data_file}"), "x",
                      encoding="utf-8") as file:
                dumps = [data_frame.model_dump() for data_frame in testset]
                json.dump(dumps, file)

        return testset
    else:
        log.error("No documents found for %s", data_file)
        raise ValueError(f"No documents found for {data_file}")


def run_testset(
        testset: list[DataFrame] = None,
        *,
        data_file: str = None,
        limit: int = None,
        record: bool = False
):
    if not testset and not data_file:
        raise ValueError()

    if not testset:
        with open(os.path.join(DATA_DIR, f"testset_{data_file}"), encoding="utf-8") as file:
            testset = [DataFrame(**data) for data in json.load(file)]

    retrieve_graph = build_retrieve_graph()
    end_index = limit if limit else len(testset)
    watch = Stopwatch(units="s")

    for data_frame in testset[:end_index]:
        result = retrieve_graph.invoke(query=data_frame.user_input)

        if documents := result.summarized_documents:
            data_frame.response = documents[0].page_content
            data_frame.retrieved_contexts = [d.page_content for d in result.retrieved_documents]
            data_frame.n_relevant_contexts = len(result.relevant_documents)
            print(f"{data_frame}\n\n")

        watch.lap()

    if record:
        now = round(time.time())
        with open(os.path.join(DATA_DIR, f"run_{now}_{data_file}"), "x", encoding="utf-8") as file:
            dumps = [data_frame.model_dump() for data_frame in testset[:end_index]]
            run = {"testset": dumps, **watch.json()}
            json.dump(run, file)


def main():
    data_file, *rest = product_catalogues()
    testset = generate_testset(data_file, size=7, write_to_disk=True)
    time.sleep(60)  # 60s timeout: 15 RPM Gemini API limit
    run_testset(testset, record=True)
    # run_testset(data_file=data_file, limit=7, record=True)


if __name__ == '__main__':
    main()
