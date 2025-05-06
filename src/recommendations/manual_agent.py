from typing import TypedDict, Annotated

import chromadb
from pydantic import BaseModel, Field
from operator import add
from langchain import hub
from langchain.retrievers.multi_query import MultiQueryRetriever, LineListOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from src.environment import gemini_api_key

EVAL_QUERY_PROMPT = (
    "You are a evaluator assessing relevance of a user query.\n"
    "Evaluate if the users query contains valid products, categories, or specific user needs "
    "related to e-commerce products."
    "Here is the user query: {query} \n"
    "Give a binary 'yes' or 'no' score to indicate whether the query is valid."
)

RANK_DOCS_PROMPT = (
    "You are a grader assessing relevance of retrieved documents to a user query.\n"
    "Here are the retrieved documents: \n\n{documents}\n\n"
    "Here is the user query: {query} \n"
    "If the documents contain keywords or semantic meaning related to the user query, grade it as "
    "relevant.\n"
    "Give a binary 'yes' or 'no' score to indicate whether the documents are relevant to the "
    "question."
)

"""
retrieve documents related to the user query, but only if it contains a valid request for a 
specific product/category or a group of products/categories or specific user needs.
after retrieval of documents assess them based on keywords or semantic meaning related to the 
user query, grade them as relevant by giving them a binary 'yes' or 'no' score.
"""


class BinaryScore(BaseModel):
    score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    google_api_key=gemini_api_key()
)


# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
# chroma = Chroma(
#    client=chromadb.HttpClient(host="localhost", port=5000),
#    collection_name="kaleido_search_products",
#    embedding_function=embeddings
# )


def evaluate_user_query(query: str) -> bool:
    prompt = EVAL_QUERY_PROMPT.format(query=query)
    response = llm.with_structured_output(BinaryScore).invoke(prompt)
    return response.score == "yes"


def retrieve(query: str) -> list[str]:
    return [
        "Brand new blue car",
        "Brand new red SUV",
        "Used Mercedes in silver",
    ]


def rank_documents(query: str, documents: list[str]) -> bool:
    prompt = RANK_DOCS_PROMPT.format(query=query, documents=documents)
    response = llm.with_structured_output(BinaryScore).invoke(prompt)
    return response.score == "yes"


sys_message = SystemMessage("""
You are an AI product recommendation assistant.
Evaluate the users request if it contains valid products, categories, or specific user needs
related to e-commerce products.
If you find a valid request use the query tool and recommend the best product.
If you dont find a valid request, kindly ask the user for a valid request related to product search.
Do not be verbose, elaborate or explain yourself and do not introduce yourself.
""")

if __name__ == '__main__':
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["q"]:
            break

        if evaluate_user_query(user_input):
            docs = retrieve(user_input)

            if rank_documents(user_input, docs):
                for document in docs:
                    print(document)
