from typing import TypedDict, Annotated

import chromadb
from langchain import hub
from langchain.retrievers.multi_query import MultiQueryRetriever, LineListOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from src.environment import gemini_api_key


class State(TypedDict):
    messages: Annotated[list, add_messages]


def gemini(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


@tool(description="Respond with when user is thankful")
def your_welcome():
    return "Your welcome!"


@tool(description="Multiply two numbers")
def multiply(a: int, b: int) -> int:
    return a * b


@tool(description="Query for best product base on user request")
def query_best_product(user_request: str) -> list[str]:
    return [
        "Brand new blue car",
        "Brand new red SUV",
        "Used Mercedes in silver",
        "LEGO Star Wars Millennium Falcon"
    ]


tools = [your_welcome, multiply, query_best_product]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=gemini_api_key()
).bind_tools(tools)

# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
# chroma = Chroma(
#    client=chromadb.HttpClient(host="localhost", port=5000),
#    collection_name="kaleido_search_products",
#    embedding_function=embeddings
# )

graph_builder = StateGraph(State)

graph_builder.add_node("llm", gemini)
graph_builder.add_node("tools", ToolNode(tools))
graph_builder.add_conditional_edges("llm", tools_condition)
graph_builder.add_edge("tools", "llm")
graph_builder.set_entry_point("llm")

graph = graph_builder.compile(checkpointer=InMemorySaver())
config = RunnableConfig(configurable={"thread_id": "1"})

sys_message = SystemMessage("""
You are an AI product recommendation assistant.
Evaluate the users request if it contains valid products, categories, or specific user needs
related to e-commerce products.
If you find a valid request use the query tool and recommend the best product.
If you dont find a valid request, kindly ask the user for a valid request related to product search.
Do not be verbose, elaborate or explain yourself and do not introduce yourself.
""")

while True:
    user_input = input("User: ")
    if user_input.lower() in ["q"]:
        break

    if user_input == "1":
        config = RunnableConfig(configurable={"thread_id": "1"})
        continue
    elif user_input == "2":
        config = RunnableConfig(configurable={"thread_id": "2"})
        continue

    for event in graph.stream({"messages": [sys_message, HumanMessage(user_input)]}, config):
        for node, update in event.items():
            print("Update from node", node)
            update["messages"][-1].pretty_print()
            print("\n")
