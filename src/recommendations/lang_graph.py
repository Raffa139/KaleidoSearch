from typing import TypedDict, Annotated
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from src.environment import gemini_api_key

EVAL_QUERY_PROMPT = (
    "You are a evaluator assessing relevance of a user query.\n"
    "Evaluate if the users query contains valid products, categories, or specific user needs "
    "related to e-commerce products.\n"
    "Guide the user with questions to improve the query and to add information to it.\n"
    "Once you gathered enough information consider the query to be valid and score it with True, "
    "score False otherwise.\n"
    "Also provide a cleaned-up version of the users query with the same semantic meaning and "
    "incorporating all answered questions, used for distance-based similarity search.\n"
    "There is always room for improvement, provide further guidance with questions, even if the "
    "query scored a True."
)

"""
retrieve documents related to the user query, but only if it contains a valid request for a 
specific product/category or a group of products/categories or specific user needs.
after retrieval of documents assess them based on keywords or semantic meaning related to the 
user query, grade them as relevant by giving them a binary 'yes' or 'no' score.
"""


class QueryEvaluation(BaseModel):
    score: bool = Field(
        description="Relevance score: True if valid, or False if not valid"
    )


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    google_api_key=gemini_api_key()
)


def gemini(state: State):
    return {
        "messages": [llm.invoke(state["messages"])]
    }



graph_builder = StateGraph(State)

graph_builder.add_node("llm", gemini)
graph_builder.add_edge(START, "llm")
graph_builder.add_edge("llm", END)

graph = graph_builder.compile(checkpointer=InMemorySaver())
config = RunnableConfig(configurable={"thread_id": "1"})

sys_message = SystemMessage(EVAL_QUERY_PROMPT)

if __name__ == '__main__':
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

        for event in graph.stream(State(messages=[sys_message, HumanMessage(user_input)]), config):
            for node, update in event.items():
                print("Update from node", node)
                print(update)
                print("\n")
